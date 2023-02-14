# Generated by Django 4.1.6 on 2023-02-11 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0031_alter_edge_modified_alter_edge_systemupsince"),
    ]

    operations = [
        migrations.AddField(
            model_name="edge",
            name="edgeId",
            field=models.IntegerField(
                default=None, help_text="The ID used in the Velocloud API", unique=True
            ),
            preserve_default=False,
        ),
    ]