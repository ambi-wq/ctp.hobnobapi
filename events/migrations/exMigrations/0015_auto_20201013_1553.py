# Generated by Django 3.0.7 on 2020-10-13 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_auto_20201013_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curatedevents',
            name='description',
            field=models.TextField(blank=True, help_text='Description of Events', null=True),
        ),
    ]
