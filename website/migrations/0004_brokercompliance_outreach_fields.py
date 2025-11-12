from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_brokercompliance'),
    ]

    operations = [
        migrations.AddField(
            model_name='brokercompliance',
            name='first_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brokercompliance',
            name='last_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brokercompliance',
            name='last_reminder_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brokercompliance',
            name='reminders_sent',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

