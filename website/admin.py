from django.contrib import admin, messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import DoNotEmailRequest, DoNotCallRequest, DataBrokers2025, BrokerCompliance, Consumer, BrokerContactLog, EmailDripState, ConsumerBrokerStatus
# Register your models here.

class DoNotEmailRequestAdmin(admin.ModelAdmin):
    list_display = ('primary_email', 'secondary_email', 'primary_phone', 'secondary_phone', 'created_at', 'paid_confirmed')

class DoNotCallRequestAdmin(admin.ModelAdmin):
    list_display = ('phone', 'created_at', 'paid_confirmed')


admin.site.register(DoNotEmailRequest, DoNotEmailRequestAdmin)
admin.site.register(DoNotCallRequest, DoNotCallRequestAdmin)
@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "primary_email", "phone", "created_at", "weekly_status_opt_in")
    search_fields = ("id", "first_name", "last_name", "primary_email")
    actions = ["send_weekly_status_email"]

    @admin.action(description="Send weekly status email to selected consumers")
    def send_weekly_status_email(self, request, queryset):
        sent = 0
        for consumer in queryset:
            snapshot = consumer.progress_snapshot(window_start=timezone.now() - timedelta(days=7))
            total = snapshot.get("total", 0)
            if total == 0:
                continue
            context = {
                "consumer": consumer,
                "snapshot": snapshot,
                "total_brokers": total,
                "lookback_start": timezone.now() - timedelta(days=7),
                "generated_at": timezone.now(),
            }
            subject = "Weekly Status Update from Stop My Spam"
            text_body = render_to_string("emails/consumer_weekly_status.txt", context)
            html_body = render_to_string("emails/consumer_weekly_status.html", context)
            from_email = getattr(settings, "NO_REPLY_EMAIL_HOST_USER", getattr(settings, "DEFAULT_FROM_EMAIL", None))
            from_email_str = f"Stop My Spam <{from_email}>" if from_email else "Stop My Spam"
            email = EmailMultiAlternatives(subject, text_body, from_email_str, [consumer.primary_email])
            email.attach_alternative(html_body, "text/html")
            email.send()
            consumer.last_status_email_at = timezone.now()
            consumer.save(update_fields=["last_status_email_at", "updated_at"])
            sent += 1
        if sent:
            messages.success(request, f"Queued {sent} weekly status email(s).")
        else:
            messages.info(request, "No emails sent. Ensure selected consumers have broker data.")


admin.site.register(BrokerContactLog)
admin.site.register(EmailDripState)


@admin.register(ConsumerBrokerStatus)
class ConsumerBrokerStatusAdmin(admin.ModelAdmin):
    list_display = (
        "consumer",
        "broker",
        "status",
        "request_type",
        "tracking_token",
        "updated_at",
    )
    list_filter = ("status", "request_type")
    search_fields = ("consumer__first_name", "consumer__last_name", "broker__name", "tracking_token")
    readonly_fields = ("tracking_token", "created_at", "updated_at")

@admin.register(DataBrokers2025)
class DataBrokers2025Admin(admin.ModelAdmin):
    list_display = ("name", "state", "website", "contact_email")
    search_fields = ("name", "dba", "website", "contact_email", "city", "state")
    list_filter = ("state", "country")


@admin.register(BrokerCompliance)
class BrokerComplianceAdmin(admin.ModelAdmin):
    list_display = ("broker", "submitted", "submitted_at", "first_sent_at", "last_sent_at", "reminders_sent")
    search_fields = ("broker__name", "token")
    list_filter = ("submitted",)
