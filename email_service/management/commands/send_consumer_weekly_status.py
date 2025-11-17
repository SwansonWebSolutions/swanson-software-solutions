from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from email_service.logger import get_script_logger
from website.models import Consumer


class Command(BaseCommand):
    help = "Email consumers a weekly status summary of broker outreach."

    def add_arguments(self, parser):
        parser.add_argument("--consumer-id", type=int, help="Limit to a specific consumer ID.")
        parser.add_argument("--days", type=int, default=7, help="Lookback window for 'recent' metrics.")
        parser.add_argument("--dry-run", action="store_true", help="Log but do not send emails.")
        parser.add_argument("--force", action="store_true", help="Send even if a status email was sent recently.")
        parser.add_argument(
            "--subject",
            default="Weekly Status Update from Stop My Spam",
            help="Email subject line.",
        )

    def handle(self, *args, **opts):
        logger = get_script_logger("send_consumer_weekly_status")
        consumers = Consumer.objects.filter(weekly_status_opt_in=True).order_by("id")
        if opts.get("consumer_id"):
            consumers = consumers.filter(id=opts["consumer_id"])

        lookback = timezone.now() - timedelta(days=opts["days"])
        dry_run = opts.get("dry_run", False)
        subject = opts["subject"]
        sent = 0

        for consumer in consumers:
            if (
                not opts.get("force")
                and consumer.last_status_email_at
                and consumer.last_status_email_at > lookback
            ):
                logger.info(
                    "Skipping consumer %s (status email sent %s)",
                    consumer.id,
                    consumer.last_status_email_at,
                )
                continue

            snapshot = consumer.progress_snapshot(window_start=lookback)
            total = snapshot.get("total", 0)
            if total == 0:
                continue

            context = {
                "consumer": consumer,
                "snapshot": snapshot,
                "total_brokers": total,
                "lookback_start": lookback,
                "generated_at": timezone.now(),
            }
            text_body = render_to_string("emails/consumer_weekly_status.txt", context)
            html_body = render_to_string("emails/consumer_weekly_status.html", context)
            from_email = getattr(
                settings, "DEFAULT_FROM_EMAIL", getattr(settings, "EMAIL_HOST_USER", None)
            )
            email = EmailMultiAlternatives(
                subject,
                text_body,
                from_email,
                [consumer.primary_email],
            )
            email.attach_alternative(html_body, "text/html")

            if dry_run:
                logger.info(
                    "[DRY RUN] Would send weekly status to consumer id=%s email=%s",
                    consumer.id,
                    consumer.primary_email,
                )
                continue

            email.send()
            consumer.last_status_email_at = timezone.now()
            consumer.save(update_fields=["last_status_email_at", "updated_at"])
            sent += 1

        logger.info("Weekly status run completed. Emails sent=%s", sent)
        self.stdout.write(self.style.SUCCESS(f"Weekly status run completed. Emails sent={sent}"))
