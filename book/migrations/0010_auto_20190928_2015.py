# Generated by Django 2.2.4 on 2019-09-28 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0009_auto_20190928_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='score',
            field=models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], default=1, max_length=1, verbose_name='評価'),
        ),
    ]
