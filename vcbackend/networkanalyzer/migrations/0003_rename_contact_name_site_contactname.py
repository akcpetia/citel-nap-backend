# Generated by Django 4.1.5 on 2023-01-31 03:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0002_rename_lng_site_lon"),
    ]

    operations = [
        migrations.RenameField(
            model_name="site", old_name="contact_name", new_name="contactName",
        ),
    ]