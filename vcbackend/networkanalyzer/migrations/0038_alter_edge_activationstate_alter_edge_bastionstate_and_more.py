# Generated by Django 4.1.7 on 2023-02-21 15:22

from django.db import migrations, models
import networkanalyzer.models


class Migration(migrations.Migration):

    dependencies = [
        ("networkanalyzer", "0037_device"),
    ]

    operations = [
        migrations.AlterField(
            model_name="edge", name="activationState", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="edge", name="bastionState", field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="edge", name="buildNumber", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="edge", name="description", field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="edge", name="deviceFamily", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="edge", name="edgeState", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="edge", name="factoryBuildNumber", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="edge", name="factorySoftwareVersion", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="edge", name="haSerialNumber", field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="edge", name="index", field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="edge", name="modelNumber", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="edge", name="selfMacAddress", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="edge", name="serialNumber", field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="edge", name="serviceState", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="edge", name="softwareVersion", field=models.TextField(),
        ),
        migrations.AlterField(model_name="ha", name="type", field=models.TextField(),),
        migrations.AlterField(
            model_name="link", name="backupState", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link", name="displayName", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link", name="effectiveState", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link", name="interface", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link", name="ipAddress", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link", name="ipV6Address", field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="link",
            name="lastActive",
            field=networkanalyzer.models.ZeroNullDateTime(),
        ),
        migrations.AlterField(
            model_name="link",
            name="lastEvent",
            field=networkanalyzer.models.ZeroNullDateTime(),
        ),
        migrations.AlterField(
            model_name="link", name="lastEventState", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link", name="linkMode", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link",
            name="modified",
            field=networkanalyzer.models.ZeroNullDateTime(),
        ),
        migrations.AlterField(
            model_name="link", name="networkSide", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link", name="networkType", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link", name="overlayType", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link", name="serviceState", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link", name="state", field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="link", name="vpnState", field=models.TextField(),
        ),
    ]
