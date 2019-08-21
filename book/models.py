import uuid

from django.db import models
from django.urls import reverse


class Book(models.Model):
    uuid = models.UUIDField(verbose_name='uuid', primary_key=True, default=uuid.uuid4, editable=False)
    isbn = models.CharField(verbose_name='ISBN', max_length=255)
    title = models.CharField(verbose_name='タイトル', max_length=255)
    author = models.CharField(verbose_name='著者', max_length=100)
    image_url = models.URLField(verbose_name='画像URL', blank=True, null=True)
    description = models.CharField(verbose_name='説明', max_length=255)
    price = models.IntegerField(verbose_name='価格')
    publisher = models.CharField(verbose_name='出版社', max_length=100)
    published_date = models.DateField(verbose_name='発売日')
    affiliate_url = models.URLField(verbose_name='楽天ブックスURL')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book:detail', kwargs={'pk': self.uuid})
