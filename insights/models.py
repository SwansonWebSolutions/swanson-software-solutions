from django.db import models
from django.utils.text import slugify


class Insight(models.Model):
    TOPIC_MARKETING = "marketing"
    TOPIC_WEB_DEV = "web-development"
    TOPIC_IOS = "ios-development"
    TOPIC_ECOMMERCE = "ecommerce"
    TOPIC_DATA_PRIVACY = "data-privacy"

    TOPIC_CHOICES = [
        (TOPIC_MARKETING, "Marketing"),
        (TOPIC_WEB_DEV, "Web Development"),
        (TOPIC_IOS, "iOS Development"),
        (TOPIC_ECOMMERCE, "eCommerce"),
        (TOPIC_DATA_PRIVACY, "Data Privacy"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
    ]

    # Core content
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(
        help_text="Short excerpt shown on the listing page and used as the default meta description."
    )
    topic = models.CharField(max_length=32, choices=TOPIC_CHOICES)
    author = models.CharField(max_length=100, blank=True, default="SwanTech")
    featured_image = models.ImageField(upload_to="insights/featured/", blank=True, help_text="Upload the featured/hero image.")
    featured_image_alt = models.CharField(max_length=255, blank=True)
    reading_time_minutes = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Estimated reading time in minutes. Leave blank to auto-calculate from section word count.",
    )

    # Status
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)

    # SEO
    seo_title = models.CharField(
        max_length=70, blank=True,
        help_text="Page &lt;title&gt; tag. Defaults to the post title if blank. Keep under 60 chars.",
    )
    seo_description = models.CharField(
        max_length=160, blank=True,
        help_text="Meta description shown in search results. Defaults to the excerpt. Keep under 160 chars.",
    )
    seo_keywords = models.CharField(
        max_length=255, blank=True,
        help_text="Comma-separated keywords.",
    )
    canonical_url = models.URLField(
        blank=True,
        help_text="Override the canonical URL. Leave blank to use the page URL.",
    )
    noindex = models.BooleanField(
        default=False,
        help_text="Add noindex, nofollow robots meta tag to prevent search engine indexing.",
    )

    # Open Graph
    og_title = models.CharField(
        max_length=100, blank=True,
        help_text="Open Graph title for social sharing. Defaults to the SEO title.",
    )
    og_description = models.CharField(
        max_length=300, blank=True,
        help_text="Open Graph description. Defaults to the SEO description.",
    )
    og_image_url = models.URLField(
        blank=True,
        help_text="Open Graph image URL (external link). Leave blank to use the featured image.",
    )

    # Twitter Card
    twitter_title = models.CharField(max_length=100, blank=True, help_text="Twitter card title. Defaults to OG title.")
    twitter_description = models.CharField(
        max_length=300, blank=True,
        help_text="Twitter card description. Defaults to OG description.",
    )

    # Advanced schema
    json_ld_extra = models.JSONField(
        null=True, blank=True,
        help_text=(
            "Extra JSON-LD properties merged into the Article schema. "
            "Must be a valid JSON object, e.g. {\"speakable\": {\"@type\": \"SpeakableSpecification\"}}."
        ),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_topic_display()}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Insight.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("website:insight-detail", kwargs={"slug": self.slug})

    def get_effective_reading_time(self):
        if self.reading_time_minutes is not None:
            return self.reading_time_minutes
        words = sum(len((s.content or "").split()) for s in self.sections.all())
        return max(1, round(words / 200))

    def get_effective_seo_title(self):
        return self.seo_title or self.title

    def get_effective_seo_description(self):
        return self.seo_description or self.description[:160]

    def get_featured_image_url(self):
        return self.featured_image.url if self.featured_image else ""

    def get_effective_og_image(self):
        return self.og_image_url or self.get_featured_image_url()


class InsightSection(models.Model):
    HEADING_H2 = "h2"
    HEADING_H3 = "h3"
    HEADING_H4 = "h4"
    HEADING_CHOICES = [
        (HEADING_H2, "H2"),
        (HEADING_H3, "H3"),
        (HEADING_H4, "H4"),
    ]

    insight = models.ForeignKey(Insight, on_delete=models.CASCADE, related_name="sections")
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order — lower numbers appear first.")
    heading = models.CharField(max_length=255, blank=True)
    heading_level = models.CharField(max_length=2, choices=HEADING_CHOICES, default=HEADING_H2)
    content = models.TextField(blank=True, help_text="Paragraph text for this section. Basic HTML is supported.")
    image = models.ImageField(upload_to="insights/sections/", blank=True, help_text="Upload an image for this section.")
    image_alt = models.CharField(max_length=255, blank=True)
    image_caption = models.CharField(max_length=255, blank=True)
    link_text = models.CharField(max_length=100, blank=True, help_text="Call-to-action link label.")
    link_url = models.URLField(blank=True)
    link_open_new_tab = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Section {self.order}: {self.heading or '(no heading)'}"
