from datetime import datetime
import uuid

from django.urls import reverse
from django.db import models
from accounts.models import CustomUser


class Book(models.Model):
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

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book:detail', kwargs={'pk': self.uuid})


class Comment(models.Model):
    """
    コメントモデル
    """
    class Meta:
        db_table = 'comment'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(verbose_name='タイトル', max_length=50)
    score = models.FloatField(verbose_name='評価')
    content = models.TextField(verbose_name='本文')
    created_date = models.DateTimeField(verbose_name='作成日', default=datetime.now)


class Favorite(models.Model):
    """
    お気に入りモデル
    """
    class Meta:
        db_table = 'favorite'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_date = models.DateTimeField(verbose_name='作成日', default=datetime.now)


class Wanted(models.Model):
    """
    読みたいモデル
    """
    class Meta:
        db_table = 'wanted'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_date = models.DateTimeField(verbose_name='作成日', default=datetime.now)
