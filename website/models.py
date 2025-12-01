import secrets
import uuid
from typing import Iterable, Sequence

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import RegexValidator


class BrokerRequestType(models.TextChoices):
    DELETE = "delete", "Delete / Remove"
    DO_NOT_SELL = "do_not_sell", "Do Not Sell / Share"
    DO_NOT_CONTACT = "do_not_contact", "Do Not Contact"


class DoNotEmailRequest(models.Model):
    ten_digit_phone = RegexValidator(
        regex=r"^\d{10}$",
        message="Enter a 10-digit phone number with digits only.",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    primary_email = models.EmailField()
    secondary_email = models.EmailField(blank=True, null=True)
    primary_phone = models.CharField(max_length=40, blank=True, null=True, validators=[ten_digit_phone])
    secondary_phone = models.CharField(max_length=40, blank=True, null=True, validators=[ten_digit_phone])
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    postal = models.CharField(max_length=20)
    country = models.CharField(max_length=2, default='US')
    notes = models.TextField(blank=True, null=True)

    paid_confirmed = models.BooleanField(default=False)
    weekly_status_opt_in = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DNE {self.primary_email} ({self.first_name} {self.last_name})"


class DoNotCallRequest(models.Model):
    ten_digit_phone = RegexValidator(
        regex=r"^\d{10}$",
        message="Enter a 10-digit phone number with digits only.",
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=40, validators=[ten_digit_phone])
    notes = models.TextField(blank=True, null=True)

    paid_confirmed = models.BooleanField(default=False)
    weekly_status_opt_in = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DNC {self.phone} ({self.full_name})"


class DataBrokers2025(models.Model):
    """California Data Broker Registry (2025 snapshot).

    Stores a normalized subset of key columns for fast lookups and the full
    original row in ``raw`` for completeness.
    """

    name = models.CharField(max_length=255)
    dba = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    contact_email = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=64, blank=True)

    street = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=60, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=60, blank=True)

    privacy_url = models.URLField(blank=True)

    raw = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'DataBrokers2025'
        verbose_name = 'Data Broker (2025)'
        verbose_name_plural = 'Data Brokers (2025)'

    def __str__(self):
        return self.name


class BrokerCompliance(models.Model):
    broker = models.OneToOneField(
        DataBrokers2025,
        on_delete=models.CASCADE,
        related_name="compliance_record",
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(blank=True, null=True)
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Outreach tracking
    first_sent_at = models.DateTimeField(blank=True, null=True)
    last_sent_at = models.DateTimeField(blank=True, null=True)
    reminders_sent = models.PositiveIntegerField(default=0)
    last_reminder_at = models.DateTimeField(blank=True, null=True)
    last_window_start = models.DateTimeField(blank=True, null=True)
    last_window_end = models.DateTimeField(blank=True, null=True)
    last_request_count = models.PositiveIntegerField(default=0)
    last_export_filename = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Broker Compliance Link"
        verbose_name_plural = "Broker Compliance Links"

    def __str__(self):
        return f"Compliance for {self.broker.name}"

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)


class Consumer(models.Model):
    """Represents a paying consumer that we execute suppression requests for."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="consumer_profile",
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    primary_email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    onboarding_notes = models.TextField(blank=True)
    default_request_type = models.CharField(
        max_length=32,
        choices=BrokerRequestType.choices,
        default=BrokerRequestType.DELETE,
    )
    weekly_status_opt_in = models.BooleanField(default=True)
    last_status_email_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def initialize_broker_statuses(
        self,
        *,
        brokers: Iterable["DataBrokers2025"] | Iterable[int] | None = None,
        request_type: str | None = None,
        batch_size: int = 500,
    ) -> int:
        """Create queued ConsumerBrokerStatus rows for all active brokers."""
        request_type = request_type or ConsumerBrokerStatus.RequestType.DELETE
        if brokers is None:
            broker_ids = list(
                DataBrokers2025.objects.filter(is_active=True).values_list(
                    "id", flat=True
                )
            )
        else:
            broker_ids = [
                b if isinstance(b, int) else getattr(b, "id")
                for b in brokers
                if b
            ]
        if not broker_ids:
            return 0

        existing = set(
            ConsumerBrokerStatus.objects.filter(
                consumer=self, broker_id__in=broker_ids
            ).values_list("broker_id", flat=True)
        )

        created = 0
        buffer: list[ConsumerBrokerStatus] = []
        for broker_id in broker_ids:
            if broker_id in existing:
                continue
            buffer.append(
                ConsumerBrokerStatus(
                    consumer=self,
                    broker_id=broker_id,
                    request_type=request_type,
                    status=ConsumerBrokerStatus.Status.QUEUED,
                )
            )
            if len(buffer) >= batch_size:
                created += self._bulk_insert_statuses(buffer)
                buffer = []
        if buffer:
            created += self._bulk_insert_statuses(buffer)
        return created

    def _bulk_insert_statuses(self, statuses: Sequence["ConsumerBrokerStatus"]) -> int:
        ConsumerBrokerStatus.objects.bulk_create(statuses, ignore_conflicts=True)
        return len(statuses)

    def progress_snapshot(self, window_start=None) -> dict:
        qs = self.broker_statuses.all()
        total = qs.count()
        snapshot = {"total": total}
        status_counts = {}
        for choice, _ in ConsumerBrokerStatus.Status.choices:
            count = qs.filter(status=choice).count()
            snapshot[choice] = count
            status_counts[choice] = count
        engaged_statuses = [
            ConsumerBrokerStatus.Status.CONTACTED,
            ConsumerBrokerStatus.Status.PROCESSING,
            ConsumerBrokerStatus.Status.COMPLETED,
            ConsumerBrokerStatus.Status.REJECTED,
            ConsumerBrokerStatus.Status.BOUNCED,
            ConsumerBrokerStatus.Status.NO_RESPONSE,
        ]
        contacted_total = qs.filter(
            models.Q(contacted_at__isnull=False) | models.Q(status__in=engaged_statuses)
        ).count()
        snapshot["contacted"] = contacted_total
        completed_count = status_counts.get(ConsumerBrokerStatus.Status.COMPLETED, 0)
        if contacted_total > 0:
            completed_pct = (completed_count / contacted_total) * 100
        else:
            completed_pct = 0
        if 0 < completed_pct < 1:
            completed_display = "<1%"
        else:
            completed_display = f"{completed_pct:.0f}%"
        snapshot["completed_percentage"] = completed_pct
        snapshot["completed_percentage_display"] = completed_display
        if window_start:
            snapshot["recent_completions"] = qs.filter(
                status=ConsumerBrokerStatus.Status.COMPLETED,
                completed_at__gte=window_start,
            ).count()
        return snapshot


class ConsumerBrokerStatus(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        CONTACTED = "contacted", "Contacted"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"
        BOUNCED = "bounced", "Bounced"
        NO_RESPONSE = "no_response", "No Response"

    RequestType = BrokerRequestType

    consumer = models.ForeignKey(
        Consumer,
        related_name="broker_statuses",
        on_delete=models.CASCADE,
    )
    broker = models.ForeignKey(
        DataBrokers2025,
        related_name="consumer_statuses",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        db_index=True,
    )
    tracking_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    request_type = models.CharField(
        max_length=20,
        choices=BrokerRequestType.choices,
        default=BrokerRequestType.DELETE,
    )
    batch_number = models.PositiveIntegerField(blank=True, null=True)
    contacted_at = models.DateTimeField(blank=True, null=True)
    last_response_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    broker_contact_name = models.CharField(max_length=255, blank=True)
    broker_contact_email = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    last_email_subject = models.CharField(max_length=255, blank=True)
    last_email_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("consumer", "broker")
        indexes = [
            models.Index(fields=("consumer", "status")),
            models.Index(fields=("broker", "status")),
            models.Index(fields=("status", "request_type")),
        ]

    def __str__(self):
        return f"{self.consumer} -> {self.broker} ({self.status})"

    def mark_contacted(
        self,
        subject: str | None = None,
        email_id: str | None = None,
        batch_number: int | None = None,
    ):
        self.status = self.Status.CONTACTED
        self.contacted_at = timezone.now()
        update_fields = ["status", "contacted_at", "updated_at"]
        if subject:
            self.last_email_subject = subject
            update_fields.append("last_email_subject")
        if email_id:
            self.last_email_id = email_id
            update_fields.append("last_email_id")
        if batch_number is not None:
            self.batch_number = batch_number
            update_fields.append("batch_number")
        self.save(update_fields=update_fields)

    def apply_broker_response(self, status: str, notes: str = "", contact_name: str = "", contact_email: str = ""):
        """Update the record based on broker feedback."""
        now = timezone.now()
        self.status = status
        self.last_response_at = now
        update_fields = ["status", "last_response_at", "notes", "broker_contact_name", "broker_contact_email", "updated_at"]
        if not self.contacted_at:
            self.contacted_at = now
            update_fields.append("contacted_at")
        if status == self.Status.COMPLETED:
            self.completed_at = now
            update_fields.append("completed_at")
        self.notes = notes
        self.broker_contact_name = contact_name
        self.broker_contact_email = contact_email
        self.save(update_fields=update_fields)


class EmailDripState(models.Model):
    """State machine that tracks drip batch sizes per consumer."""

    consumer = models.OneToOneField(
        Consumer, on_delete=models.CASCADE, related_name="drip_state"
    )
    sequence_index = models.PositiveIntegerField(default=0)
    last_batch_size = models.PositiveIntegerField(default=0)
    total_contacted = models.PositiveIntegerField(default=0)
    last_run_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    DEFAULT_SEQUENCE = (5, 10, 20, 30, 50, 75, 100)

    def next_batch_size(self, override: int | None = None) -> int:
        if override:
            return max(1, override)
        sequence = getattr(
            settings,
            "BROKER_DRIP_BATCH_SEQUENCE",
            self.DEFAULT_SEQUENCE,
        )
        if not sequence:
            sequence = self.DEFAULT_SEQUENCE
        idx = min(self.sequence_index, len(sequence) - 1)
        return max(1, sequence[idx])

    def mark_batch_complete(self, sent: int):
        if sent <= 0:
            return
        self.last_batch_size = sent
        self.total_contacted += sent
        self.last_run_at = timezone.now()
        max_index = len(
            getattr(settings, "BROKER_DRIP_BATCH_SEQUENCE", self.DEFAULT_SEQUENCE)
        ) - 1
        if self.sequence_index < max_index:
            self.sequence_index += 1
        self.save(
            update_fields=[
                "sequence_index",
                "last_batch_size",
                "total_contacted",
                "last_run_at",
                "updated_at",
            ]
        )


class BrokerContactLog(models.Model):
    """Audit trail for outbound broker emails."""

    consumer = models.ForeignKey(
        Consumer, related_name="contact_logs", on_delete=models.CASCADE
    )
    broker = models.ForeignKey(
        DataBrokers2025, related_name="contact_logs", on_delete=models.CASCADE
    )
    status = models.ForeignKey(
        ConsumerBrokerStatus,
        related_name="contact_logs",
        on_delete=models.CASCADE,
    )
    subject = models.CharField(max_length=255)
    snippet = models.TextField(blank=True)
    sent_at = models.DateTimeField()
    success = models.BooleanField(default=True)
    error = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-sent_at",)


class NewsletterSubscriber(models.Model):
    """Newsletter opt-in records."""

    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.email


@receiver(post_save, sender=Consumer)
def auto_initialize_brokers(sender, instance: Consumer, created: bool, **kwargs):
    if created:
        instance.initialize_broker_statuses()
