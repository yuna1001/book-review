import random
import string
from http import HTTPStatus

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.shortcuts import get_object_or_404

from book.models import Book, Favorite, Wanted
from book.tests.factory import BookFactory


class TestBookSearchView(TestCase):
    """
    書籍の検索を行うビュークラスのテスト
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user', email='test@example.com', password='password'
        )

    def test_post_search_request(self):
        """
        APIで書籍の検索を行う機能のテスト
        """
        response = self.client.post(reverse('book:search'), {
            'book_name': 'Python',
        })

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.context['book_list'])
        self.assertFalse(response.context['form'].errors)
        self.assertTemplateUsed(response, 'book/book_search.html')

    def test_invalid_search_word(self):
        """
        検索キーワードの入力値のバリデーションのテスト
        """
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
    """
    書籍をDBに登録するビュークラスのテスト
    """

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
        """
        書籍をDBに登録する機能のテスト
        """
        response = self.client.post(reverse('book:add'), self.book_info)

        book = get_object_or_404(Book, title=self.book_title)

        self.assertTrue(book)
        self.assertRedirects(response, book.get_absolute_url())


class TestBookDetailView(TestCase):
    """
    書籍の詳細表示を行うビュークラスのテスト
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user', email='test@example.com', password='password'
        )
        self.client.login(username=self.user.username, password='password')

        self.comment_title = 'comment_title'
        self.comment_info = {
            'user': self.user,
            'title': self.comment_title,
            'score': 5.0,
            'content': 'content',
        }

    def test_get_book_detail(self):
        """
        書籍の詳細ページを表示する機能のテスト
        """
        expected_book_title = 'book_title'
        book = BookFactory(title=expected_book_title)

        response = self.client.get(reverse('book:detail', args=[book.uuid]))

        self.assertTemplateUsed(response, 'book/book_detail.html')
        self.assertEqual(expected_book_title, response.context['book'].title)

    def test_add_comment(self):
        """
        書籍のコメント機能のテスト
        """
        book_title = 'Django'
        book = BookFactory(title=book_title)
        self.comment_info['book'] = book

        response = self.client.post(reverse('book:detail', kwargs={'pk': book.uuid}), self.comment_info, follow=True)
        self.assertEqual(self.comment_title, response.context.get('comment_list')[0].title)


class TestFavoriteAddView(TestCase):
    """
    お気に入りに追加するビュークラスのテスト
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user', email='test@example.com', password='password'
        )
        self.client.login(username=self.user.username, password='password')

    def test_add_favorite(self):
        """
        お気に入り追加機能のテスト
        """
        book = BookFactory()

        response = self.client.post(reverse('book:add_favorite'), {
            'book_uuid': book.uuid,
        }, follow=True)

        favorite = get_object_or_404(Favorite, user=self.user, book=book)

        self.assertTrue(favorite)
        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': book.uuid}))


class TestWantedAddView(TestCase):
    """
    読みたいに追加するビュークラスのテスト
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user', email='test@example.com', password='password'
        )
        self.client.login(username=self.user.username, password='password')

    def test_add_wanted(self):
        """
        読みたい追加機能のテスト
        """
        book = BookFactory()

        response = self.client.post(reverse('book:add_wanted'), {
            'book_uuid': book.uuid,
        }, follow=True)

        wanted = get_object_or_404(Wanted, user=self.user, book=book)

        self.assertTrue(wanted)
        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': book.uuid}))


class TestBookListView(TestCase):
    """
    書籍の一覧表示を行うビュークラスのテスト
    """

    def test_list_view(self):
        """
        登録した10件の書籍が一覧表示されるかテスト
        """
        book_count = 10
        BookFactory.create_batch(book_count)

        response = self.client.get(reverse('book:list'), follow=True)

        self.assertEqual(book_count, len(response.context.get('book_list')))
