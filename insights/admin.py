from django import forms
from django.contrib import admin, messages
from django.core.management import call_command
from django.core.management.base import CommandError
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import format_html

from .models import Insight, InsightSection


class InsightGenerationForm(forms.Form):
    MODE_CHOICES = [
        ("random", "Random topics"),
        ("order", "Cycle in order"),
        ("choice", "Single topic"),
    ]
    mode = forms.ChoiceField(choices=MODE_CHOICES, initial="random", required=True)
    topic = forms.ChoiceField(
        choices=Insight.TOPIC_CHOICES, required=False, help_text="Required if mode is Single topic"
    )
    count = forms.IntegerField(min_value=1, initial=1, help_text="How many insights to generate")


class InsightSectionInline(admin.StackedInline):
    model = InsightSection
    extra = 1
    fields = (
        ("order", "heading", "heading_level"),
        "content",
        ("image", "image_alt"),
        "image_caption",
        ("link_text", "link_url", "link_open_new_tab"),
    )


@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "status", "seo_score", "published_at", "created_at", "view_link")
    list_filter = ("topic", "status")
    search_fields = ("title", "description", "slug", "focus_keyword")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = (
        "vibeseo_post_id",
        "seo_score",
        "vibeseo_published_at",
        "created_at",
        "updated_at",
    )
    inlines = [InsightSectionInline]
    change_list_template = "admin/insights/insight_change_list.html"

    fieldsets = (
        ("Content", {
            "fields": (
                "title",
                "slug",
                "topic",
                "status",
                "published_at",
                "description",
                "author",
                "featured_image",
                "featured_image_alt",
                "reading_time_minutes",
            ),
        }),
        ("SEO — Basic", {
            "classes": ("collapse",),
            "description": (
                "Control how this page appears in search engine results. "
                "All fields fall back to the post title/description if left blank."
            ),
            "fields": (
                "seo_title",
                "seo_description",
                "seo_keywords",
                "canonical_url",
                "noindex",
            ),
        }),
        ("SEO — Open Graph & Twitter", {
            "classes": ("collapse",),
            "description": "Controls how this post looks when shared on social media.",
            "fields": (
                "og_title",
                "og_description",
                "og_image_url",
                "twitter_title",
                "twitter_description",
            ),
        }),
        ("SEO — Advanced Schema (JSON-LD)", {
            "classes": ("collapse",),
            "description": (
                "Optional extra properties merged into the Article JSON-LD schema block. "
                "Must be a valid JSON object. Leave blank unless you know what you are doing."
            ),
            "fields": ("json_ld_extra",),
        }),
        ("VibeSEO Content", {
            "classes": ("collapse",),
            "description": (
                "Raw markdown delivered by the VibeSEO webhook. Re-rendered into the first content "
                "section automatically every time this post is saved."
            ),
            "fields": ("body_markdown", "focus_keyword", "seo_score"),
        }),
        ("Structured Data", {
            "classes": ("collapse",),
            "description": "FAQ and related-link data captured from VibeSEO.",
            "fields": ("faq", "internal_links"),
        }),
        ("VibeSEO Metadata", {
            "classes": ("collapse",),
            "fields": ("vibeseo_post_id", "vibeseo_published_at"),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    def view_link(self, obj):
        if obj.pk and obj.slug:
            url = obj.get_absolute_url()
            label = "View" if obj.status == Insight.STATUS_PUBLISHED else "Preview"
            return format_html('<a href="{}" target="_blank">{}</a>', url, label)
        return "-"
    view_link.short_description = "View"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("generate/", self.admin_site.admin_view(self.generate_view), name="insights_generate"),
        ]
        return custom + urls

    def generate_view(self, request):
        form = InsightGenerationForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            mode = form.cleaned_data["mode"]
            topic = form.cleaned_data["topic"]
            count = form.cleaned_data["count"]
            try:
                kwargs = {"mode": mode, "count": count}
                if mode == "choice":
                    kwargs["topic"] = topic
                result = call_command("generate_insights", **kwargs)
                messages.success(request, f"Generated {count} insight(s): {result}")
                return redirect("admin:insights_insight_changelist")
            except CommandError as exc:
                messages.error(request, f"Failed to generate insights: {exc}")
            except Exception as exc:  # pragma: no cover - defensive guard
                messages.error(request, f"Unexpected error: {exc}")

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "form": form,
            "title": "Generate AI Insights",
        }
        return render(request, "admin/insights/generate_insights.html", context)
