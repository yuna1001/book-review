# Generated by Django 2.2.4 on 2019-10-26 07:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20191013_1545'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='date_joined',
        ),
        migrations.AddField(
            model_name='customuser',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日時'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='更新日時'),
        ),
        migrations.AddField(
            model_name='relation',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日時'),
        ),
        migrations.AddField(
            model_name='relation',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='更新日時'),
        ),
    ]