import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone

from insights.models import Insight
from website.models import NewsletterSubscriber
from website.utils import manage_preferences_url


class Command(BaseCommand):
    help = (
        "Send the weekly newsletter (latest 3 insights) to all newsletter subscribers. "
        "Schedule this for Wednesdays at 8:30 AM."
    )

    def handle(self, *args, **options):
        subscribers = list(
            NewsletterSubscriber.objects.values_list("email", flat=True)
        )
        if not subscribers:
            self.stdout.write(self.style.WARNING("No newsletter subscribers found; nothing sent."))
            return

        insights = list(Insight.objects.order_by("-created_at")[:3])
        if not insights:
            self.stdout.write(self.style.WARNING("No insights available; nothing sent."))
            return

        base_url = getattr(settings, "PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
        insights_url = f"{base_url}{reverse('website:insights')}"
        home_url = f"{base_url}{reverse('website:index')}"
        logo_url = f"{base_url}{static('images/logo-text.png')}"

        context = {
            "insights": insights,
            "insights_url": insights_url,
            "home_url": home_url,
            "logo_url": logo_url,
            "generated_at": timezone.now(),
            "manage_url": manage_preferences_url(),
            "support_email": getattr(settings, "SUPPORT_EMAIL_HOST_USER", "support@swantech.org"),
        }

        subject = "SwanTech weekly insights — latest 3"
        text_body = render_to_string("emails/newsletter_digest.txt", context)
        html_body = render_to_string("emails/newsletter_digest.html", context)

        from_email = f"SwanTech Newsletter <{getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@swantech.org')}>"

        msg = EmailMultiAlternatives(subject, text_body, from_email, bcc=subscribers)
        msg.attach_alternative(html_body, "text/html")
        msg.send()

        self.stdout.write(
            self.style.SUCCESS(
                f"Sent weekly newsletter to {len(subscribers)} subscriber(s) with {len(insights)} insight(s)."
            )
        )
