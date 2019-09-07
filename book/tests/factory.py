
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from django.utils import timezone

from book.models import Book


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    isbn = FuzzyText()
    title = FuzzyText()
    author = FuzzyText()
    image_url = 'http://example.com'
    description = FuzzyText()
    price = 1000
    publisher = FuzzyText()
    published_date = timezone.now()
    affiliate_url = 'http://example.com'
