from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Insight",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                (
                    "topic",
                    models.CharField(
                        choices=[
                            ("marketing", "Marketing"),
                            ("web-development", "Web Development"),
                            ("ios-development", "iOS Development"),
                            ("ecommerce", "eCommerce"),
                            ("data-privacy", "Data privacy"),
                        ],
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
