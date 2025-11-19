from django import forms
from django.contrib import admin, messages
from django.core.management import call_command
from django.core.management.base import CommandError
from django.shortcuts import redirect, render
from django.urls import path

from .models import Insight


class InsightGenerationForm(forms.Form):
    MODE_CHOICES = [
        ("random", "Random topics"),
        ("order", "Cycle in order"),
        ("choice", "Single topic"),
    ]
    mode = forms.ChoiceField(choices=MODE_CHOICES, initial="random", required=True)
    topic = forms.ChoiceField(
        choices=Insight.TOPIC_CHOICES, required=False, help_text="Required if mode is Single topic"
    )
    count = forms.IntegerField(min_value=1, initial=1, help_text="How many insights to generate")


@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "created_at")
    list_filter = ("topic",)
    search_fields = ("title", "description")
    change_list_template = "admin/insights/insight_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("generate/", self.admin_site.admin_view(self.generate_view), name="insights_generate"),
        ]
        return custom + urls

    def generate_view(self, request):
        form = InsightGenerationForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            mode = form.cleaned_data["mode"]
            topic = form.cleaned_data["topic"]
            count = form.cleaned_data["count"]
            try:
                kwargs = {"mode": mode, "count": count}
                if mode == "choice":
                    kwargs["topic"] = topic
                result = call_command("generate_insights", **kwargs)
                messages.success(request, f"Generated {count} insight(s): {result}")
                return redirect("admin:insights_insight_changelist")
            except CommandError as exc:
                messages.error(request, f"Failed to generate insights: {exc}")
            except Exception as exc:  # pragma: no cover - defensive guard
                messages.error(request, f"Unexpected error: {exc}")

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "form": form,
            "title": "Generate AI Insights",
        }
        return render(request, "admin/insights/generate_insights.html", context)
