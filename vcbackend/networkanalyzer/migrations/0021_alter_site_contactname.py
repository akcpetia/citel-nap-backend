# Generated by Django 4.1.5 on 2023-01-31 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0020_site_logicalid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="site",
            name="contactName",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
