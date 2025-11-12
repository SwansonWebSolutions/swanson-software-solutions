from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataBrokers2025',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('dba', models.CharField(blank=True, max_length=255)),
                ('website', models.URLField(blank=True)),
                ('contact_email', models.CharField(blank=True, max_length=255)),
                ('phone', models.CharField(blank=True, max_length=64)),
                ('street', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=120)),
                ('state', models.CharField(blank=True, max_length=60)),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('country', models.CharField(blank=True, max_length=60)),
                ('privacy_url', models.URLField(blank=True)),
                ('raw', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'DataBrokers2025',
                'verbose_name': 'Data Broker (2025)',
                'verbose_name_plural': 'Data Brokers (2025)',
            },
        ),
    ]

