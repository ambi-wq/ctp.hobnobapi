# Generated by Django 3.2.5 on 2022-07-14 07:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('matching', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuggesstedUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suggessted_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggessted_user', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]