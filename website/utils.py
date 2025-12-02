from django.conf import settings
from django.urls import reverse


def manage_preferences_url() -> str:
    base = getattr(settings, "PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    return f"{base}{reverse('website:manage-preferences')}"
