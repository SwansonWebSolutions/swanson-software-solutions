from django.db import models


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
        (TOPIC_DATA_PRIVACY, "Data privacy"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    topic = models.CharField(max_length=32, choices=TOPIC_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - admin string helper
        return f"{self.get_topic_display()}: {self.title}"
