import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from django.utils import timezone

from accounts.models import CustomUser
from book.models import Book, Comment, Favorite, Wanted


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = FuzzyText()
    email = 'test@example.com'

    # passwordとして'defaultpassword'を設定
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')


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
    published_date = timezone.localtime()
    affiliate_url = 'http://example.com'
    fav_count = 0
    wanted_count = 0


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    user = factory.SubFactory(CustomUserFactory)
    book = factory.SubFactory(BookFactory)
    title = factory.Sequence(lambda n: "Agent %03d" % n)
    score = '1'
    content = FuzzyText()


class FavoriteFactory(DjangoModelFactory):
    class Meta:
        model = Favorite

    user = factory.SubFactory(CustomUserFactory)
    book = factory.SubFactory(BookFactory)


class WantedFactory(DjangoModelFactory):
    class Meta:
        model = Wanted

    user = factory.SubFactory(CustomUserFactory)
    book = factory.SubFactory(BookFactory)
