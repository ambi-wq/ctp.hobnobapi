# Generated by Django 3.2.5 on 2022-08-09 07:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0007_alter_events_event_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='going_users',
            field=models.ManyToManyField(blank=True, null=True, related_name='going_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='events',
            name='yet_to_decide_users',
            field=models.ManyToManyField(blank=True, null=True, related_name='yet_to_decide_users', to=settings.AUTH_USER_MODEL),
        ),

    ]