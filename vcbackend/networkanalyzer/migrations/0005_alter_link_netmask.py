# Generated by Django 4.1.5 on 2023-01-31 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0004_edge_ha_link"),
    ]

    operations = [
        migrations.AlterField(
            model_name="link",
            name="netmask",
            field=models.CharField(max_length=30, null=True),
        ),
    ]
