from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0010_servicemarket"),
    ]

    operations = [
        migrations.CreateModel(
            name="BrokerAcknowledgement",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("acknowledged", models.BooleanField(default=False)),
                ("acknowledged_at", models.DateTimeField(blank=True, null=True)),
                ("last_sent_at", models.DateTimeField(blank=True, null=True)),
                ("send_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "broker",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="acknowledgement",
                        to="website.databrokers2025",
                    ),
                ),
            ],
            options={
                "verbose_name": "Broker Acknowledgement",
                "verbose_name_plural": "Broker Acknowledgements",
            },
        ),
    ]

