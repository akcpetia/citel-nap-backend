# Generated by Django 4.1.5 on 2023-02-06 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0028_database2_database3"),
    ]

    operations = [
        migrations.AddField(
            model_name="database1",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="database2",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="database3",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]