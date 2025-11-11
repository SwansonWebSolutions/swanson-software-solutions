from django.contrib import admin
from .models import DoNotEmailRequest, DoNotCallRequest
# Register your models here.

class DoNotEmailRequestAdmin(admin.ModelAdmin):
    list_display = ('primary_email', 'secondary_email', 'created_at', 'paid_confirmed')

class DoNotCallRequestAdmin(admin.ModelAdmin):
    list_display = ('phone', 'created_at', 'paid_confirmed')


admin.site.register(DoNotEmailRequest, DoNotEmailRequestAdmin)
admin.site.register(DoNotCallRequest, DoNotCallRequestAdmin)