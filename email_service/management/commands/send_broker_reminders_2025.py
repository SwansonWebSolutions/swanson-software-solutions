import time
from datetime import datetime, timedelta
from typing import Iterable

from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.urls import reverse, NoReverseMatch

from email_service.logger import get_script_logger
from website.models import DataBrokers2025, BrokerCompliance


TEST_RECIPIENTS = [
    "daswanson22@gmail.com",
    "cyberswanson14@gmail.com",
]


class Command(BaseCommand):
    help = (
        "Send reminder emails to brokers who have not submitted compliance "
        "within 30 days of the first outreach."
    )

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None)
        parser.add_argument("--duration-seconds", type=int, default=1800)
        parser.add_argument("--real", action="store_true")
        parser.add_argument(
            "--subject",
            default="Reminder: Please confirm Stop My Spam suppression",
        )

    def handle(self, *args, **opts):
        logger = get_script_logger("send_broker_reminders_2025")

        now = timezone.now()
        threshold = now - timedelta(days=30)
        qs = (
            BrokerCompliance.objects.select_related("broker")
            .filter(submitted=False, first_sent_at__isnull=False, first_sent_at__lte=threshold)
            .order_by("first_sent_at")
        )
        if opts["limit"]:
            qs = qs[: opts["limit"]]

        total = qs.count()
        if total == 0:
            self.stdout.write("No brokers require reminders.")
            return

        base = getattr(settings, "PUBLIC_BASE_URL", "http://127.0.0.1:8000")
        duration = max(0, int(opts["duration_seconds"]))
        interval = duration / total if total else 0
        logger.info("Starting reminders: total=%s interval=%.2fs", total, interval)

        for idx, compliance in enumerate(qs, start=1):
            broker = compliance.broker
            link = build_compliance_link(base, compliance.token)
            if opts["real"]:
                recipients = self._parse_recipients(broker.contact_email)
                if not recipients:
                    logger.warning("Skipping broker without contact email: %s (id=%s)", broker.name, broker.id)
                    continue
            else:
                recipients = TEST_RECIPIENTS

            subject = opts["subject"]
            body = (
                "Hello,\n\n"
                "This is a friendly reminder to confirm that Stop My Spam (email suppression) "
                "has been completed for the consumer records previously provided.\n\n"
                f"Please confirm completion here: {link}\n\n"
                "Regards,\nStop My Spam"
            )
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", None)

            try:
                email = EmailMultiAlternatives(subject, body, from_email, recipients)
                email.send()
                compliance.reminders_sent = (compliance.reminders_sent or 0) + 1
                compliance.last_reminder_at = timezone.now()
                compliance.save(update_fields=["reminders_sent", "last_reminder_at", "updated_at"])
                logger.info("[%d/%d] Reminder sent to %s | broker=%s", idx, total, ", ".join(recipients), broker.name)
            except Exception as exc:
                logger.exception("[%d/%d] Failed to send reminder to %s | broker=%s | %s", idx, total, recipients, broker.name, exc)

            if idx < total and interval > 0:
                time.sleep(max(0.01, interval))

        logger.info("Completed reminder run: total=%s", total)

    @staticmethod
    def _parse_recipients(value: str) -> list[str]:
        if not value:
            return []
        parts = [p.strip() for p in value.replace(";", ",").split(",")]
        return [p for p in parts if p]


def build_compliance_link(base_url: str, token: str) -> str:
    normalized_base = (base_url or "").rstrip("/")
    try:
        path = reverse("website:broker-compliance-token", args=[token])
        return f"{normalized_base}{path}"
    except NoReverseMatch:
        path = reverse("website:broker-compliance")
        separator = "&" if "?" in path else "?"
        return f"{normalized_base}{path}{separator}t={token}"
