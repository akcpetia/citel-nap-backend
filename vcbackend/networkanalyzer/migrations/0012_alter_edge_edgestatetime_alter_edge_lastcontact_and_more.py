# Generated by Django 4.1.5 on 2023-01-31 23:19

from django.db import migrations
import networkanalyzer.models


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0011_alter_edge_deviceid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="edge",
            name="edgeStateTime",
            field=networkanalyzer.models.ZeroNullDateTime(null=True),
        ),
        migrations.AlterField(
            model_name="edge",
            name="lastContact",
            field=networkanalyzer.models.ZeroNullDateTime(null=True),
        ),
        migrations.AlterField(
            model_name="edge",
            name="serviceUpSince",
            field=networkanalyzer.models.ZeroNullDateTime(null=True),
        ),
        migrations.AlterField(
            model_name="edge",
            name="softwareUpdated",
            field=networkanalyzer.models.ZeroNullDateTime(null=True),
        ),
    ]
