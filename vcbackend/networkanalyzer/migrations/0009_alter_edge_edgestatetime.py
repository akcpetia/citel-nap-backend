# Generated by Django 4.1.5 on 2023-01-31 23:09

from django.db import migrations
import networkanalyzer.models


class Migration(migrations.Migration):

    dependencies = [
        (
            "networkanalyzer",
            "0008_alter_edge_halastcontact_alter_edge_lastcontact_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="edge",
            name="edgeStateTime",
            field=networkanalyzer.models.ZeroNullDateTime(),
        ),
    ]
