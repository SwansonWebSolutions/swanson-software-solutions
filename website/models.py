from django.db import models
import secrets


class DoNotEmailRequest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    primary_email = models.EmailField()
    secondary_email = models.EmailField(blank=True, null=True)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    postal = models.CharField(max_length=20)
    country = models.CharField(max_length=2, default='US')
    notes = models.TextField(blank=True, null=True)

    paid_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DNE {self.primary_email} ({self.first_name} {self.last_name})"


class DoNotCallRequest(models.Model):
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=40)
    notes = models.TextField(blank=True, null=True)

    paid_confirmed = models.BooleanField(default=False)
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

    class Meta:
        verbose_name = "Broker Compliance Link"
        verbose_name_plural = "Broker Compliance Links"

    def __str__(self):
        return f"Compliance for {self.broker.name}"

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)
