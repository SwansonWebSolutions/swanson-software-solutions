from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_databrokers2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrokerCompliance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(db_index=True, max_length=64, unique=True)),
                ('submitted', models.BooleanField(default=False)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('contact_name', models.CharField(blank=True, max_length=255)),
                ('contact_email', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('broker', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='compliance_record', to='website.databrokers2025')),
            ],
            options={
                'verbose_name': 'Broker Compliance Link',
                'verbose_name_plural': 'Broker Compliance Links',
            },
        ),
    ]

