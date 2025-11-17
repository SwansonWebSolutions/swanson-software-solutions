from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from email_service.logger import get_script_logger
from website.models import (
    BrokerContactLog,
    Consumer,
    ConsumerBrokerStatus,
    EmailDripState,
)


def _split_recipients(raw: str | None) -> list[str]:
    if not raw:
        return []
    recipients: list[str] = []
    for part in raw.replace(";", ",").split(","):
        value = part.strip()
        if value:
            recipients.append(value)
    return recipients


class Command(BaseCommand):
    help = "Send throttled broker outreach emails for queued ConsumerBrokerStatus rows."

    def add_arguments(self, parser):
        parser.add_argument("--consumer-id", type=int, help="Limit to a single consumer ID.")
        parser.add_argument("--max-batch", type=int, help="Override computed batch size.")
        parser.add_argument("--limit", type=int, help="Absolute cap on rows to process this run.")
        parser.add_argument("--dry-run", action="store_true", help="Log actions without sending.")
        parser.add_argument(
            "--subject",
            default="Stop My Spam deletion request for {consumer}",
            help="Subject template. Available fields: {consumer}, {broker}, {request_type}.",
        )
        parser.add_argument(
            "--from-email",
            default=None,
            help="Override default from email address.",
        )
        parser.add_argument(
            "--test",
            action="store_true",
            help="Send to TEST_BROKER_RECIPIENTS (settings) instead of broker contact emails.",
        )
        parser.add_argument(
            "--attach-window-csv",
            action="store_true",
            help="Build a CSV for paid Stop My Spam submissions between 8am prior day and 8am today (America/Los_Angeles) and attach to each email.",
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
        # Setup logger
        logger = get_script_logger("send_consumer_broker_drip")
        consumers = Consumer.objects.all().order_by("id")
        if opts.get("consumer_id"):
            consumers = consumers.filter(id=opts["consumer_id"])
        if not consumers.exists():
            self.stdout.write("No consumers found for drip processing.")
            return
        csv_payload = None
        if opts.get("attach_window_csv"):
            csv_payload = self._build_window_csv(opts)
        # Process each consumer record
        total_sent = 0
        for consumer in consumers:
            sent = self._process_consumer(consumer, opts, logger, csv_payload)
            total_sent += sent

        logger.info("Completed drip run. Emails sent=%s", total_sent)
        self.stdout.write(self.style.SUCCESS(f"Completed drip run. Emails sent={total_sent}"))

    def _process_consumer(self, consumer: Consumer, opts: dict, logger, csv_payload) -> int:
        """
        Process a single consumer's queued broker statuses, sending emails as appropriate.
        """
        state, _ = EmailDripState.objects.get_or_create(consumer=consumer)
        batch_size = state.next_batch_size(opts.get("max_batch"))
        if opts.get("limit"):
            batch_size = min(batch_size, opts["limit"])

        # Ensure broker statuses exist for this consumer (default DELETE)
        if not consumer.broker_statuses.exists():
            consumer.initialize_broker_statuses(request_type=ConsumerBrokerStatus.RequestType.DELETE)

        qs = consumer.broker_statuses.filter(
            status=ConsumerBrokerStatus.Status.QUEUED,
            broker__contact_email__gt="",
            request_type=ConsumerBrokerStatus.RequestType.DELETE,
        ).select_related("broker")

        statuses = list(qs[:batch_size])
        if not statuses:
            logger.info("Consumer %s has no queued brokers.", consumer.id)
            return 0

        base_url = getattr(settings, "PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
        path_template = self._resolve_path_template(statuses[0].tracking_token)
        from_email = opts.get("from_email") or getattr(
            settings, "DEFAULT_FROM_EMAIL", getattr(settings, "EMAIL_HOST_USER", None)
        )
        subject_template = opts["subject"]
        dry_run = opts.get("dry_run", False)
        test_mode = opts.get("test", False)
        test_recipients = []
        if test_mode:
            test_recipients = list(getattr(settings, "TEST_BROKER_RECIPIENTS", []))
            if not test_recipients:
                logger.warning("TEST_BROKER_RECIPIENTS is empty; test mode will send nothing.")
        sent = 0
        batch_number = state.sequence_index + 1

        for status in statuses:
            if test_mode:
                recipients = test_recipients
            else:
                recipients = _split_recipients(status.broker.contact_email)
            if not recipients:
                logger.warning("Skipping broker id=%s (no recipients)", status.broker_id)
                continue

            compliance_link = f"{base_url}{path_template.format(token=status.tracking_token)}"
            context = {
                "consumer": consumer,
                "status": status,
                "broker": status.broker,
                "compliance_link": compliance_link,
            }
            subject = subject_template.format(
                consumer=consumer.full_name,
                broker=status.broker.name,
                request_type=status.get_request_type_display(),
            )
            text_body = render_to_string("emails/broker_outreach_request.txt", context)
            html_body = render_to_string("emails/broker_outreach_request.html", context)
            email = EmailMultiAlternatives(subject, text_body, from_email, recipients)
            email.attach_alternative(html_body, "text/html")
            if csv_payload:
                filename, content = csv_payload
                email.attach(filename, content, "text/csv")

            if dry_run:
                logger.info(
                    "[DRY RUN] Would send to %s for consumer %s broker %s",
                    recipients,
                    consumer.id,
                    status.broker_id,
                )
                continue

            try:
                email.send()
                status.mark_contacted(subject=subject, batch_number=batch_number)
                BrokerContactLog.objects.create(
                    consumer=consumer,
                    broker=status.broker,
                    status=status,
                    subject=subject,
                    snippet=text_body[:500],
                    sent_at=timezone.now(),
                    success=True,
                )
                sent += 1
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception(
                    "Failed to send to broker id=%s for consumer id=%s | %s",
                    status.broker_id,
                    consumer.id,
                    exc,
                )
                status.status = ConsumerBrokerStatus.Status.BOUNCED
                status.notes = f"Send failure: {exc}"
                status.save(update_fields=["status", "notes", "updated_at"])
                BrokerContactLog.objects.create(
                    consumer=consumer,
                    broker=status.broker,
                    status=status,
                    subject=subject,
                    snippet=text_body[:500],
                    sent_at=timezone.now(),
                    success=False,
                    error=str(exc),
                )

        if not dry_run and sent:
            state.mark_batch_complete(sent)
        return sent

    @staticmethod
    def _resolve_path_template(sample_token):
        try:
            path = reverse("website:broker-compliance-token", args=[sample_token])
            return path.replace(str(sample_token), "{token}")
        except NoReverseMatch:
            try:
                legacy_path = reverse("website:broker-compliance")
            except NoReverseMatch:
                legacy_path = "/broker-compliance/"
            separator = "&" if "?" in legacy_path else "?"
            return f"{legacy_path}{separator}t={{token}}"

    def _build_window_csv(self, opts) -> tuple[str, str] | None:
        """Build a CSV of paid Stop My Spam signups within the specified LA window."""
        from io import StringIO
        import csv
        from website.models import DoNotEmailRequest

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
            return None

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
        for r in dne_qs:
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

    def _compute_window(self, opts, la: ZoneInfo) -> tuple[datetime, datetime]:
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
