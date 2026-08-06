from django.contrib import admin
from django.utils.html import format_html

from .models import (
    DoNotEmailRequest,
    DoNotCallRequest,
    DataBrokers2025,
    Consumer,
    BrokerContactLog,
    EmailDripState,
    ConsumerBrokerStatus,
    NewsletterSubscriber,
    SiteImage,
)
# Register your models here.


@admin.register(SiteImage)
class SiteImageAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "thumbnail", "alt_text", "updated_at")
    search_fields = ("key", "title", "alt_text")
    readonly_fields = ("thumbnail_preview", "uploaded_at", "updated_at")
    fields = ("key", "title", "image", "thumbnail_preview", "alt_text", "uploaded_at", "updated_at")

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;object-fit:cover;">', obj.image.url)
        return "—"
    thumbnail.short_description = "Preview"

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:240px;border-radius:8px;">', obj.image.url)
        return "No image uploaded yet"
    thumbnail_preview.short_description = "Preview"


class DoNotEmailRequestAdmin(admin.ModelAdmin):
    list_display = ("primary_email", "secondary_email", "primary_phone", "secondary_phone", "created_at", "paid_confirmed")


class DoNotCallRequestAdmin(admin.ModelAdmin):
    list_display = ("phone", "created_at", "paid_confirmed")


admin.site.register(DoNotEmailRequest, DoNotEmailRequestAdmin)
admin.site.register(DoNotCallRequest, DoNotCallRequestAdmin)
@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "primary_email", "phone", "created_at", "weekly_status_opt_in")
    search_fields = ("id", "first_name", "last_name", "primary_email")


admin.site.register(BrokerContactLog)
admin.site.register(EmailDripState)
admin.site.register(NewsletterSubscriber)


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
