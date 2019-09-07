import random
import string
from http import HTTPStatus

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.shortcuts import get_object_or_404

from book.models import Book
from book.tests.factory import BookFactory


class TestBookSearchView(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user', email='test@example.com', password='password'
        )

    def test_post_search_request(self):
        response = self.client.post(reverse('book:search'), {
            'book_name': 'Python',
        })

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.context['book_list'])
        self.assertFalse(response.context['form'].errors)
        self.assertTemplateUsed(response, 'book/book_search.html')

    def test_invalid_search_word(self):
        invalid_search_word_length = 51

        invalid_search_word = self.randomname(invalid_search_word_length)

        response = self.client.post(reverse('book:search'), {
            'book_name': invalid_search_word,
        })

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.context['form'].errors)

        expected_message = 'この値は 50 文字以下でなければなりません( ' + str(invalid_search_word_length) + ' 文字になっています)。'
        self.assertEqual(response.context['form'].errors['book_name'][0], expected_message)

    def randomname(self, n):
        randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
        return ''.join(randlst)


class TestBookAddView(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user', email='test@example.com', password='password'
        )
        self.client.login(username=self.user.username, password='password')

        self.book_title = 'Django'

        self.book_info = {
            'book_isbn': 'book_isbn',
            'book_title': self.book_title,
            'book_author': 'book_author',
            'book_image_url': 'http:bookurl',
            'book_description': 'book_description',
            'book_price': '1000',
            'book_publisher': 'book_publisher',
            'book_published_date': 'book_published_date',
            'book_affiliate_url': 'book_affiliate_url',
        }

    def test_add_book(self):
        response = self.client.post(reverse('book:add'), self.book_info)

        book = get_object_or_404(Book, title=self.book_title)

        self.assertTrue(book)
        self.assertRedirects(response, book.get_absolute_url())


class TestBookDetailView(TestCase):
    '''DBに登録した書籍の詳細ページ遷移するテスト'''

    def test_get_book_detail(self):
        expected_book_title = 'Django'
        book = BookFactory(title=expected_book_title)

        response = self.client.get(reverse('book:detail', args=[book.uuid]))

        self.assertTemplateUsed(response, 'book/book_detail.html')
        self.assertEqual(expected_book_title, response.context['book'].title)
