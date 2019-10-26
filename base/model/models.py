from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    作成日時・更新日時のモデル
    """

    created = models.DateTimeField(verbose_name='作成日時', default=timezone.now)
    modified = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        # Trueにすることでマイグレーションしてもテーブルは作られない
        abstract = True
