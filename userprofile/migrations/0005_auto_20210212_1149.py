# Generated by Django 2.2.13 on 2021-02-12 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0004_auto_20210212_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiledetails',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='profiledetails',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]