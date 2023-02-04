# Generated by Django 4.1.5 on 2023-01-31 20:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0005_alter_link_netmask"),
    ]

    operations = [
        migrations.AddField(
            model_name="edge", name="customInfo", field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="edge",
            name="recentLinks",
            field=models.ManyToManyField(to="networkanalyzer.link"),
        ),
        migrations.AddField(
            model_name="edge",
            name="site",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="networkanalyzer.site",
            ),
        ),
    ]