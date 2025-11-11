from django.db import models


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
