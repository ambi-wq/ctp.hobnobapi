# Generated by Django 3.0.7 on 2020-09-07 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0021_auto_20200907_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpreference',
            name='opposite_gender',
            field=models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Both', 'Both')], help_text="User interested in Opposite Gender. **It is removed that why it's made optional", max_length=6, null=True),
        ),
    ]