from django.contrib import admin
from .models import DoNotEmailRequest, DoNotCallRequest, DataBrokers2025, BrokerCompliance
# Register your models here.

class DoNotEmailRequestAdmin(admin.ModelAdmin):
    list_display = ('primary_email', 'secondary_email', 'created_at', 'paid_confirmed')

class DoNotCallRequestAdmin(admin.ModelAdmin):
    list_display = ('phone', 'created_at', 'paid_confirmed')


admin.site.register(DoNotEmailRequest, DoNotEmailRequestAdmin)
admin.site.register(DoNotCallRequest, DoNotCallRequestAdmin)


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
