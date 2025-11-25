from datetime import datetime, time, timedelta
from io import StringIO
from zoneinfo import ZoneInfo
import csv
import time as time_module

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.urls import reverse, NoReverseMatch
from django.utils import timezone

from email_service.logger import get_script_logger
from website.models import DataBrokers2025, BrokerCompliance, DoNotEmailRequest


def _split_recipients(raw: str | None) -> list[str]:
    if not raw:
        return []
    parts = [p.strip() for p in raw.replace(";", ",").split(",")]
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


class Command(BaseCommand):
    help = (
        "Send one daily outreach email per broker with a CSV of paid Stop My Spam "
        "signups from 8am prior day to 8am today (America/Los_Angeles)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--duration-seconds",
            type=int,
            default=3600,
            help="Drip duration across all emails (default: 3600 = 1 hour).",
        )
        parser.add_argument("--limit", type=int, default=None, help="Limit number of brokers processed.")
        parser.add_argument("--offset", type=int, default=0, help="Skip the first N brokers before processing.")
        parser.add_argument(
            "--test",
            action="store_true",
            help="Send to TEST_BROKER_RECIPIENTS (settings) instead of broker contact emails. Only the first broker will be processed in test mode.",
        )
        parser.add_argument(
            "--subject",
            default="Consumer Deletion Request from Stop My Spam",
            help="Email subject line.",
        )
        parser.add_argument(
            "--message",
            default=(
                "Hello {broker},\n\n"
                "This is a consumer privacy request submitted through Stop My Spam for the deletion of the following records in the attached CSV.\n\n"
                "Requested action: Delete/Remove\n\n"
                "Please confirm completion or provide the current status using the secure link below:\n"
                "{compliance_link}\n\n"
                "If you have questions you can reply to this email and our compliance team will follow up promptly.\n\n"
                "Thank you for your cooperation,\n"
                "Stop My Spam Compliance"
            ),
            help="Plain-text email body. Available format fields: {compliance_link}, {broker}.",
        )
        parser.add_argument(
            "--window-start",
            help="Override window start (ISO 8601). If naive, assumes America/Los_Angeles.",
        )
        parser.add_argument(
            "--window-end",
            help="Override window end (ISO 8601). If naive, assumes America/Los_Angeles.",
        )

    def handle(self, *args, **opts):
        logger = get_script_logger("send_broker_daily_outreach")
        la = ZoneInfo("America/Los_Angeles")
        start, end = self._compute_window(opts, la)

        dne_qs = (
            DoNotEmailRequest.objects.filter(
                paid_confirmed=True,
                created_at__gte=start,
                created_at__lt=end,
            ).order_by("created_at")
        )
        if not dne_qs.exists():
            self.stdout.write("No paid Stop My Spam signups in the window; no emails sent.")
            return

        record_count = dne_qs.count()
        csv_filename, csv_body = self._build_csv(dne_qs, la, start, end)

        qs = DataBrokers2025.objects.filter(is_active=True).order_by("id")
        if opts["offset"]:
            qs = qs[opts["offset"] :]
        if opts["limit"] is not None:
            qs = qs[: opts["limit"]]
        if opts.get("test"):
            qs = qs[:1]

        total = qs.count()
        if total == 0:
            self.stdout.write("No brokers to process.")
            return

        duration = max(0, int(opts["duration_seconds"]))
        interval = duration / total if total else 0

        base_url = getattr(settings, "PUBLIC_BASE_URL", "http://127.0.0.1:8000")
        from_email = getattr(settings, "COMPLIANCE_EMAIL_HOST_USER", None) or getattr(settings, "EMAIL_HOST_USER", None)
        subject = opts["subject"]
        message_template = opts["message"]
        test_mode = opts.get("test", False)
        test_recipients = list(getattr(settings, "TEST_BROKER_RECIPIENTS", []))

        if test_mode and not test_recipients:
            logger.warning("TEST_BROKER_RECIPIENTS is empty; test mode will send nothing.")

        logger.info(
            "Starting daily broker outreach: total=%s interval=%.2fs window=%s->%s",
            total,
            interval,
            start,
            end,
        )

        sent = 0
        for idx, broker in enumerate(qs, start=1):
            compliance, _ = BrokerCompliance.objects.get_or_create(
                broker=broker,
                defaults={"token": BrokerCompliance.generate_token()},
            )
            # Rotate token each send so prior submissions don't count for future runs.
            compliance.token = BrokerCompliance.generate_token()
            compliance.submitted = False
            compliance.submitted_at = None
            compliance.last_request_count = record_count
            compliance.last_window_start = start
            compliance.last_window_end = end
            compliance.last_export_filename = csv_filename
            compliance.save(
                update_fields=[
                    "token",
                    "submitted",
                    "submitted_at",
                    "last_request_count",
                    "last_window_start",
                    "last_window_end",
                    "last_export_filename",
                    "updated_at",
                ]
            )
            link = build_compliance_link(base_url, compliance.token)

            if test_mode:
                recipients = test_recipients
            else:
                recipients = _split_recipients(broker.contact_email)
            if not recipients:
                logger.warning("Skipping broker without recipients: %s (id=%s)", broker.name, broker.id)
                continue

            body = message_template.format(compliance_link=link, broker=broker.name)

            try:
                email = EmailMultiAlternatives(subject, body, from_email, recipients)
                html_body = render_to_string(
                    "emails/broker_daily_outreach.html",
                    {
                        "broker_name": broker.name,
                        "compliance_link": link,
                    },
                )
                email.attach_alternative(html_body, "text/html")
                email.attach(csv_filename, csv_body, "text/csv")
                email.send()
                sent += 1
                now_ts = timezone.now()
                if not compliance.first_sent_at:
                    compliance.first_sent_at = now_ts
                compliance.last_sent_at = now_ts
                compliance.save(update_fields=["first_sent_at", "last_sent_at", "updated_at"])
                logger.info("[%d/%d] Sent to %s | broker=%s", idx, total, ", ".join(recipients), broker.name)
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("[%d/%d] Failed to send to %s | broker=%s | %s", idx, total, recipients, broker.name, exc)

            if idx < total and interval > 0:
                time_module.sleep(max(0.01, interval))

        logger.info("Completed daily outreach. Sent=%s of total=%s", sent, total)
        self.stdout.write(self.style.SUCCESS(f"Completed daily outreach. Sent={sent} of total={total}"))

    def _build_csv(self, qs, la: ZoneInfo, start, end) -> tuple[str, str]:
        buf = StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            [
                "first_name",
                "last_name",
                "email1",
                "email2",
                "address1",
                "address2",
                "city",
                "state",
                "postal",
                "region",
                "created_at",
            ]
        )
        for r in qs:
            created_local = r.created_at.astimezone(la).isoformat()
            writer.writerow(
                [
                    r.first_name,
                    r.last_name,
                    r.primary_email,
                    r.secondary_email or "",
                    r.address1,
                    r.address2 or "",
                    r.city,
                    r.region,
                    r.postal,
                    r.region,
                    created_local,
                ]
            )
        start_label = start.astimezone(la).strftime("%Y%m%d_%H%M")
        end_label = end.astimezone(la).strftime("%Y%m%d_%H%M")
        filename = f"dne_records_{start_label}_to_{end_label}.csv"
        return filename, buf.getvalue()

    def _compute_window(self, opts, la: ZoneInfo):
        """Default window: 8am prior day -> 8am today (America/Los_Angeles)."""

        def _parse(dt_str: str) -> datetime:
            dt = datetime.fromisoformat(dt_str)
            if dt.tzinfo is None:
                return timezone.make_aware(dt, la)
            return dt.astimezone(la)

        now_la = timezone.now().astimezone(la)
        today = now_la.date()
        end_default = timezone.make_aware(datetime.combine(today, time(8)), la)
        if now_la < end_default:
            end_default -= timedelta(days=1)
        start_default = end_default - timedelta(days=1)

        start = _parse(opts["window_start"]) if opts.get("window_start") else start_default
        end = _parse(opts["window_end"]) if opts.get("window_end") else end_default
        return start, end
