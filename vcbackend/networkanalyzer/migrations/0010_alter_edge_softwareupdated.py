# Generated by Django 4.1.5 on 2023-01-31 23:12

from django.db import migrations
import networkanalyzer.models


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0009_alter_edge_edgestatetime"),
    ]

    operations = [
        migrations.AlterField(
            model_name="edge",
            name="softwareUpdated",
            field=networkanalyzer.models.ZeroNullDateTime(),
        ),
    ]
