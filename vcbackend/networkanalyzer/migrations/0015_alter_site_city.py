# Generated by Django 4.1.5 on 2023-01-31 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0014_alter_edge_issoftwareversionsupportedbyvco"),
    ]

    operations = [
        migrations.AlterField(
            model_name="site",
            name="city",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
