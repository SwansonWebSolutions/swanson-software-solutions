from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0011_brokeracknowledgement"),
    ]

    operations = [
        migrations.AlterField(
            model_name="servicemarket",
            name="service_type",
            field=models.CharField(
                choices=[
                    ("web-development", "Web Development"),
                    ("ios-app-development", "iOS App Development"),
                    ("shopify", "Shopify Store"),
                ],
                default="web-development",
                max_length=32,
            ),
        ),
    ]
