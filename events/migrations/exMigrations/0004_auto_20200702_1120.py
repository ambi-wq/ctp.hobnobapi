# Generated by Django 3.0.7 on 2020-07-02 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0012_auto_20200623_1141'),
        ('events', '0003_events_interested_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='event_interest',
            field=models.ManyToManyField(related_name='event_interest', to='userprofile.Interest'),
        ),
    ]