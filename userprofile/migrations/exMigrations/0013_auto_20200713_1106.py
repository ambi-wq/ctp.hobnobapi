# Generated by Django 3.0.7 on 2020-07-13 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0012_auto_20200623_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='profiledetails',
            name='bio',
            field=models.TextField(blank=True, help_text='Description of User'),
        ),
        migrations.AddField(
            model_name='profiledetails',
            name='enjoy',
            field=models.TextField(blank=True, help_text='Description of things user enjoy doing'),
        ),
        migrations.AddField(
            model_name='profiledetails',
            name='fun_fact',
            field=models.TextField(blank=True, help_text='Fun Fact of User'),
        ),
        migrations.AddField(
            model_name='profiledetails',
            name='work_as',
            field=models.CharField(blank=True, help_text='Designation at Work Place', max_length=100),
        ),
    ]