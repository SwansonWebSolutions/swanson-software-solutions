from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0009_newslettersubscriber"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceMarket",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("city", models.CharField(max_length=120)),
                ("state_id", models.CharField(max_length=2)),
                ("state_name", models.CharField(max_length=100)),
                ("zip_code", models.CharField(blank=True, max_length=10)),
                ("slug_city", models.SlugField(max_length=140)),
                ("slug_state", models.SlugField(max_length=140)),
                (
                    "service_type",
                    models.CharField(
                        choices=[
                            ("web-development", "Web Development"),
                            ("ios-app-development", "iOS App Development"),
                        ],
                        default="web-development",
                        max_length=32,
                    ),
                ),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("state_name", "city"),
                "unique_together": {("slug_state", "slug_city", "service_type")},
            },
        ),
        migrations.AddIndex(
            model_name="servicemarket",
            index=models.Index(fields=["slug_state", "slug_city", "service_type"], name="website_ser_slug_st_e32676_idx"),
        ),
        migrations.AddIndex(
            model_name="servicemarket",
            index=models.Index(fields=["state_id", "service_type"], name="website_ser_state_i_ae5d34_idx"),
        ),
    ]
