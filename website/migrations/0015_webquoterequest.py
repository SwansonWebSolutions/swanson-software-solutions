from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0014_siteimage"),
    ]

    operations = [
        migrations.CreateModel(
            name="WebQuoteRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("project_type", models.CharField(max_length=40)),
                ("primary_goal", models.CharField(max_length=40)),
                ("primary_goal_other", models.CharField(blank=True, max_length=500)),
                ("page_count", models.CharField(max_length=20)),
                ("features", models.JSONField(default=list)),
                ("features_other", models.CharField(blank=True, max_length=500)),
                ("maintenance", models.JSONField(default=list)),
                ("full_name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=40)),
                ("company", models.CharField(max_length=200)),
                ("current_url", models.URLField(blank=True, max_length=500)),
                ("one_time_total", models.PositiveIntegerField(default=0)),
                ("monthly_total", models.PositiveIntegerField(default=0)),
                ("estimate_lines", models.JSONField(default=dict)),
                ("attribution", models.JSONField(default=dict, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
    ]
