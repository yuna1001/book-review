# Generated by Django 2.2.4 on 2019-10-13 03:53

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_pic',
            field=models.ImageField(blank=True, default='noimage.jpg', null=True, upload_to='', verbose_name='profile_picture'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(error_messages={'unique': '同じユーザ名が既に録済みです。お手数となりますが別のユーザ名にてご登録いただけますようお願い申し上げます。'}, help_text='ユーザ名は25文字以内でご登録いただけますようお願い申し上げます。', max_length=25, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
        ),
    ]
