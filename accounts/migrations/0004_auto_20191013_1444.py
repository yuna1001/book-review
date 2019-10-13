# Generated by Django 2.2.4 on 2019-10-13 05:44

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20191013_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(error_messages={'unique': 'ユーザ名は既に登録されています。お手数となりますが別のユーザ名をご検討ください。'}, help_text='ユーザ名は必須となります。25文字以内でご設定ください。', max_length=25, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
        ),
    ]
