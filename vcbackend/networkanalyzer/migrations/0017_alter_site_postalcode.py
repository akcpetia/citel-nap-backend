# Generated by Django 4.1.5 on 2023-01-31 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0016_alter_site_state"),
    ]

    operations = [
        migrations.AlterField(
            model_name="site",
            name="postalCode",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
