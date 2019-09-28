
import uuid

from django.db import models
from django.utils import timezone
from django.urls import reverse

from django.conf import settings


class TimeStampedModel(models.Model):
    """
    作成日時・更新日時のモデル
    """
    created = models.DateTimeField(verbose_name='作成日時', default=timezone.now)
    modified = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        # Trueにすることでマイグレーションしてもテーブルは作られない
        abstract = True


class Book(TimeStampedModel):
    """
    書籍モデル
    """
    class Meta:
        db_table = 'book'

    uuid = models.UUIDField(verbose_name='uuid', primary_key=True, default=uuid.uuid4, editable=False)
    isbn = models.CharField(verbose_name='ISBN', max_length=255, unique=True)
    title = models.CharField(verbose_name='タイトル', max_length=255)
    author = models.CharField(verbose_name='著者', max_length=100)
    image_url = models.URLField(verbose_name='画像URL', blank=True, null=True)
    description = models.TextField(verbose_name='説明')
    price = models.IntegerField(verbose_name='価格')
    publisher = models.CharField(verbose_name='出版社', max_length=100)
    published_date = models.CharField(verbose_name='発売日', max_length=50)
    affiliate_url = models.URLField(verbose_name='楽天ブックスURL', max_length=2000)
    fav_count = models.IntegerField(verbose_name='お気に入り数', default=0)
    wanted_count = models.IntegerField(verbose_name='読みたい数', default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book:detail', kwargs={'pk': self.uuid})


class Comment(TimeStampedModel):
    """
    コメントモデル
    """

    class Meta:
        db_table = 'comment'

    uuid = models.UUIDField(verbose_name='uuid', primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(verbose_name='タイトル', max_length=50)
    score = models.FloatField(verbose_name='評価')
    content = models.TextField(verbose_name='本文')

    def __str__(self):
        return self.title


class Favorite(TimeStampedModel):
    """
    お気に入りモデル
    """

    class Meta:
        db_table = 'favorite'
        unique_together = ('user', 'book')

    uuid = models.UUIDField(verbose_name='uuid', primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.uuid)


class Wanted(TimeStampedModel):
    """
    読みたいモデル
    """

    class Meta:
        db_table = 'wanted'
        unique_together = ('user', 'book')

    uuid = models.UUIDField(verbose_name='uuid', primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.uuid)
