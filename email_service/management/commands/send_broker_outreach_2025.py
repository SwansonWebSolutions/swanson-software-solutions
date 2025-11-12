import math
import time
import csv
from io import StringIO
from typing import Iterable

from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from email_service.logger import get_script_logger
from website.models import DataBrokers2025, BrokerCompliance, DoNotEmailRequest
from django.urls import reverse


TEST_RECIPIENTS = [
    "daswanson22@gmail.com",
    "cyberswanson14@gmail.com",
]


def chunked(iterable: Iterable, size: int):
    buf = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf


class Command(BaseCommand):
    help = (
        "Send an individual email to each broker in DataBrokers2025. "
        "For testing, emails go to test inboxes rather than broker emails."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit number of brokers processed (for testing).",
        )
        parser.add_argument(
            "--offset",
            type=int,
            default=0,
            help="Skip the first N brokers before processing.",
        )
        parser.add_argument(
            "--duration-seconds",
            type=int,
            default=3600,
            help="Drip duration across all emails (default: 3600 = 1 hour).",
        )
        parser.add_argument(
            "--real",
            action="store_true",
            help="Send to the broker's contact_email instead of test inboxes.",
        )
        parser.add_argument(
            "--subject",
            default="Notice: Consumer Email Suppression (Stop My Spam)",
            help="Email subject line.",
        )
        parser.add_argument(
            "--message",
            default=(
                "Hello,\n\n"
                "We are contacting you in relation to California consumer privacy. "
                "Please confirm your process for honoring Stop My Spam (email suppression) requests "
                "and provide the preferred contact channel for agent-submitted requests.\n\n"
                "Regards,\nStop My Spam"
            ),
            help="Plain-text email body."
        )

    def handle(self, *args, **opts):
        logger = get_script_logger("send_broker_outreach_2025")
        # Build weekly CSV: 8AM Monday -> 8AM next Monday (local time)
        # We choose the most recent Monday 8AM that is <= now as the end,
        # and the Monday 8AM one week prior as the start.
        la_tz = ZoneInfo("America/Los_Angeles")
        now_la = datetime.now(la_tz)
        today_la = now_la.date()
        # Date of this week's Monday
        this_monday_date = today_la - timedelta(days=today_la.weekday())  # 0 = Monday
        this_monday_8 = timezone.make_aware(
            datetime.combine(this_monday_date, datetime.min.time()).replace(hour=8), la_tz
        )
        if now_la >= this_monday_8:
            end_local = this_monday_8
        else:
            end_local = this_monday_8 - timedelta(days=7)
        start_local = end_local - timedelta(days=7)

        # Use timezone-aware datetimes directly; Django converts to UTC internally
        dne_qs = (
            DoNotEmailRequest.objects
            .filter(created_at__gte=start_local, created_at__lt=end_local)
            .order_by("created_at")
        )
        count = dne_qs.count()
        if count == 0:
            logger.info("No Do Not Email records in window %s -> %s. Aborting send.", start_local, end_local)
            self.stdout.write("No consumer records for this window. No emails sent.")
            return

        # Prepare CSV once and attach to each email
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow([
            "first_name", "last_name", "email1", "email2", "address1", "address2",
            "city", "state", "postal", "region", "created_at",
        ])
        for r in dne_qs:
            writer.writerow([
                r.first_name,
                r.last_name,
                r.primary_email,
                r.secondary_email or "",
                r.address1,
                r.address2 or "",
                r.city,
                r.region,                # state
                r.postal,
                r.region,                # region (duplicate as requested)
                r.created_at.astimezone(la_tz).isoformat(),
            ])
        csv_content = csv_buffer.getvalue()
        csv_filename = f"dne_records_{start_local.strftime('%Y%m%d_%H%M')}_to_{end_local.strftime('%Y%m%d_%H%M')}.csv"

        qs = DataBrokers2025.objects.all().order_by("id")
        if opts["offset"]:
            qs = qs[opts["offset"] :]
        if opts["limit"] is not None:
            qs = qs[: opts["limit"]]

        total = qs.count()
        if total == 0:
            self.stdout.write("No brokers to process.")
            return

        duration = max(0, int(opts["duration_seconds"]))
        interval = duration / total if total > 0 else 0
        logger.info(
            "Starting weekly outreach: brokers=%s duration=%ss interval=%.2fs records=%s window=%s->%s",
            total, duration, interval, count, start_local, end_local,
        )

        sent = 0
        base = getattr(settings, 'PUBLIC_BASE_URL', 'http://127.0.0.1:8000')
        path = reverse('website:broker-compliance')

        for idx, broker in enumerate(qs, start=1):
            # Ensure a per-broker token exists
            compliance, created = BrokerCompliance.objects.get_or_create(
                broker=broker,
                defaults={
                    'token': BrokerCompliance.generate_token(),
                },
            )
            link = f"{base}{path}?t={compliance.token}"
            # Determine recipients
            if opts["real"]:
                recipients = self._parse_recipients(broker.contact_email)
                # If no valid email, skip
                if not recipients:
                    logger.warning("Skipping broker without contact email: %s (id=%s)", broker.name, broker.id)
                    continue
            else:
                recipients = TEST_RECIPIENTS

            subject = opts["subject"]
            body = opts["message"]

            # Per-broker context appended
            decorated_body = (
                f"Broker: {broker.name}\n"
                f"Website: {broker.website or 'n/a'}\n"
                f"State: {broker.state or 'n/a'}\n\n"
                f"{body}\n\nPlease confirm completion here: {link}\n"
            )

            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", None)
            try:
                email = EmailMultiAlternatives(subject, decorated_body, from_email, recipients)
                email.attach(csv_filename, csv_content, "text/csv")
                email.send()
                sent += 1
                # Record send timestamps for compliance tracking
                now_ts = timezone.now()
                if not compliance.first_sent_at:
                    compliance.first_sent_at = now_ts
                compliance.last_sent_at = now_ts
                compliance.save(update_fields=["first_sent_at", "last_sent_at", "updated_at"])
                logger.info("[%d/%d] Sent to %s | broker=%s", idx, total, ", ".join(recipients), broker.name)
            except Exception as exc:
                logger.exception("[%d/%d] Failed to send to %s | broker=%s | %s", idx, total, recipients, broker.name, exc)

            # Drip pacing
            if idx < total and interval > 0:
                # Sleep with a floor to avoid micro-sleeps; allow sub-second precision
                time.sleep(max(0.01, interval))

        logger.info("Completed outreach. Sent=%s of total=%s", sent, total)
        self.stdout.write(self.style.SUCCESS(f"Completed outreach. Sent={sent} of total={total}"))

    @staticmethod
    def _parse_recipients(value: str) -> list[str]:
        if not value:
            return []
        parts = [p.strip() for p in value.replace(";", ",").split(",")]
        return [p for p in parts if p]
