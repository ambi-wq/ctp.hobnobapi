# Generated by Django 3.2.5 on 2022-07-06 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_imagesupload_image_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportEventsDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(help_text='User Id')),
                ('event_id', models.IntegerField(help_text='Event Id')),
                ('report_reason', models.CharField(blank=True, help_text='report reason', max_length=1000)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]