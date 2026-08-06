from django.urls import path

from . import views

app_name = "insights"

urlpatterns = [
    path("api/blog/webhook/vibeseo/", views.vibeseo_webhook, name="vibeseo_webhook"),
]
