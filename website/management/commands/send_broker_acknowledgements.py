import time

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q

from website.models import BrokerAcknowledgement, DataBrokers2025


def _split_recipients(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.replace(";", ",").split(",") if part.strip()]


class Command(BaseCommand):
    help = (
        "Send an introductory acknowledgement email to each data broker asking them "
        "to confirm SwanTech as a service that protects consumer data."
    )

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None, help="Limit the number of brokers processed.")
        parser.add_argument("--offset", type=int, default=0, help="Skip the first N brokers.")
        parser.add_argument(
            "--include-acknowledged",
            action="store_true",
            help="Also send to brokers that have already confirmed acknowledgement.",
        )
        parser.add_argument(
            "--test",
            action="store_true",
            help="Send to TEST_BROKER_RECIPIENTS instead of broker contact emails (first broker only).",
        )
        parser.add_argument(
            "--subject",
            default="Please confirm SwanTech as your consumer data protection partner",
            help="Subject line to use for the acknowledgement email.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Log intended recipients without sending or updating acknowledgement records.",
        )
        parser.add_argument(
            "--delay-seconds",
            type=float,
            default=120.0,
            help="Delay between emails in seconds (default: 120 = 2 minutes).",
        )

    def handle(self, *args, **opts):
        base_url = getattr(settings, "PUBLIC_BASE_URL", "https://swantech.org").rstrip("/")
        confirmation_path = reverse("website:broker-acknowledgement-confirmation")
        confirmation_base = f"{base_url}{confirmation_path}"
        support_email = getattr(
            settings,
            "SUPPORT_EMAIL_HOST_USER",
            getattr(settings, "DEFAULT_FROM_EMAIL", "support@swantech.org"),
        )
        test_recipients = list(getattr(settings, "TEST_BROKER_RECIPIENTS", []))
        subject = opts["subject"]
        dry_run = opts["dry_run"]
        delay_seconds = max(0.0, float(opts.get("delay_seconds", 120.0)))
        include_acknowledged = opts["include_acknowledged"]
        from_email = (
            getattr(settings, "COMPLIANCE_EMAIL_HOST_USER", None)
            or getattr(settings, "EMAIL_HOST_USER", None)
            or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@swantech.org")
        )
        from_email_formatted = f"SwanTech Compliance <{from_email}>"

        qs = DataBrokers2025.objects.filter(is_active=True).select_related("acknowledgement").order_by("id")
        if not include_acknowledged:
            qs = qs.filter(Q(acknowledgement__acknowledged=False) | Q(acknowledgement__isnull=True))
        if opts["offset"]:
            qs = qs[opts["offset"] :]
        if opts["limit"] is not None:
            qs = qs[: opts["limit"]]
        if opts["test"]:
            qs = qs[:1]

        total_candidates = qs.count()
        if total_candidates == 0:
            self.stdout.write(self.style.WARNING("No data brokers available to process."))
            return

        sent = 0
        skipped = 0
        for idx, broker in enumerate(qs, start=1):
            try:
                acknowledgement = broker.acknowledgement
            except BrokerAcknowledgement.DoesNotExist:
                acknowledgement = None

            if acknowledgement and acknowledgement.acknowledged and not include_acknowledged:
                skipped += 1
                continue

            recipients = test_recipients if opts["test"] else _split_recipients(broker.contact_email)
            if not recipients:
                skipped += 1
                continue

            confirmation_url = f"{confirmation_base}?brokerid={broker.id}"
            context = {
                "broker": broker,
                "confirmation_url": confirmation_url,
                "support_email": support_email,
                "base_url": base_url,
            }
            text_body = render_to_string("emails/broker_acknowledgement_request.txt", context)
            html_body = render_to_string("emails/broker_acknowledgement_request.html", context)

            if dry_run:
                self.stdout.write(f"[DRY RUN] {broker.name} -> {', '.join(recipients)} | {confirmation_url}")
                continue

            email = EmailMultiAlternatives(
                subject,
                text_body,
                from_email_formatted,
                recipients,
            )
            email.attach_alternative(html_body, "text/html")
            email.send()

            ack_record, _ = BrokerAcknowledgement.objects.get_or_create(broker=broker)
            now = timezone.now()
            ack_record.last_sent_at = now
            ack_record.send_count = (ack_record.send_count or 0) + 1
            ack_record.save(update_fields=["last_sent_at", "send_count", "updated_at"])
            sent += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"[{sent}/{total_candidates}] Sent acknowledgement request to {broker.name} ({', '.join(recipients)})"
                )
            )

            if not dry_run and idx < total_candidates and delay_seconds > 0:
                time.sleep(delay_seconds)

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed acknowledgement run. Sent={sent} skipped={skipped} total_candidates={total_candidates}"
            )
        )
