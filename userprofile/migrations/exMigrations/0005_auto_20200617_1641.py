# Generated by Django 3.0.7 on 2020-06-17 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0004_auto_20200617_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiledetails',
            name='interest',
            field=models.ManyToManyField(blank=True, related_name='interest', to='userprofile.Interest'),
        ),
    ]
