# Generated by Django 3.2.18 on 2023-02-21 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('networkanalyzer', '0039_alter_link_lastevent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='shippingAddress',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='shippingAddress2',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='streetAddress',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='streetAddress2',
            field=models.TextField(null=True),
        ),
    ]
