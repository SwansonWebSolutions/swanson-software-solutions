from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0007_alter_donotcallrequest_phone_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="brokercompliance",
            name="last_export_filename",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="brokercompliance",
            name="last_request_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="brokercompliance",
            name="last_window_end",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="brokercompliance",
            name="last_window_start",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
