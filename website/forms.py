from django import forms

from .quote_config import (
    FEATURE_CHOICES,
    MAINTENANCE_CHOICES,
    PAGE_COUNT_CHOICES,
    PRIMARY_GOAL_CHOICES,
    PROJECT_TYPE_CHOICES,
)


class RequestWebQuoteForm(forms.Form):
    project_type = forms.ChoiceField(choices=PROJECT_TYPE_CHOICES)
    primary_goal = forms.ChoiceField(choices=PRIMARY_GOAL_CHOICES)
    primary_goal_other = forms.CharField(required=False, max_length=500)
    page_count = forms.ChoiceField(choices=PAGE_COUNT_CHOICES)
    features = forms.MultipleChoiceField(
        choices=FEATURE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    features_other = forms.CharField(required=False, max_length=500)
    maintenance = forms.MultipleChoiceField(
        choices=MAINTENANCE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=40)
    company = forms.CharField(max_length=200)
    current_url = forms.URLField(required=False, max_length=500)
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("primary_goal") == "other" and not cleaned.get("primary_goal_other", "").strip():
            self.add_error("primary_goal_other", "Please describe what you are looking for.")
        if "other" in cleaned.get("features", []) and not cleaned.get("features_other", "").strip():
            self.add_error("features_other", "Please describe the feature or functionality you need.")
        return cleaned
