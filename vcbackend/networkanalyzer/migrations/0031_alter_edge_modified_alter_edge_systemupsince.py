# Generated by Django 4.1.5 on 2023-02-08 19:39

from django.db import migrations
import networkanalyzer.models


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0030_alter_database3_event_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="edge",
            name="modified",
            field=networkanalyzer.models.ZeroNullDateTime(),
        ),
        migrations.AlterField(
            model_name="edge",
            name="systemUpSince",
            field=networkanalyzer.models.ZeroNullDateTime(),
        ),
    ]
