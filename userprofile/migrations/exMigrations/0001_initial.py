# Generated by Django 3.0.7 on 2020-06-12 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileUID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_id', models.CharField(blank=True, help_text='Firbease User UID', max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], help_text='Gender of User', max_length=10)),
                ('dob', models.DateField()),
                ('full_name', models.CharField(help_text='Full name of User', max_length=40)),
                ('uuid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='userprofile.ProfileUID')),
            ],
        ),
    ]