# Generated by Django 4.1.7 on 2023-02-15 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0032_edge_edgeid"),
    ]

    operations = [
        migrations.AddField(
            model_name="edge",
            name="index",
            field=models.IntegerField(default=None),
            preserve_default=False,
        ),
    ]
