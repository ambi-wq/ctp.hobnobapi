# Generated by Django 3.2.5 on 2022-07-21 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_reporteventsdetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='event_end_date',
            field=models.DateField(default=None),
        ),
    ]