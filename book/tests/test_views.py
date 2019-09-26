from http import HTTPStatus
import random
import string

from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.urls import reverse

from .factory import BookFactory, CommentFactory, CustomUserFactory, FavoriteFactory, WantedFactory
from ..forms import (BookSearchForm, CommentCreateForm)
from ..models import Book, Comment, Favorite, Wanted


def get_response_messages(response):
    """
    Responseのフラッシュメッセージ取得関数
    """

    return list(response.context['messages'])


class TestBookSearchView(TestCase):
    """
    書籍の検索を行うビュークラスのテスト
    """

    def test_post_search_request(self):
        """
        APIで書籍の検索を行う機能のテスト
        """

        response = self.client.post(reverse('book:search'), {
            'book_name': 'Python',
        })

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.context.get('book_list'))
        self.assertFalse(response.context.get('form').errors)
        self.assertTemplateUsed(response, 'book/book_search.html')

    def test_invalid_search_word(self):
        """
        検索キーワードの入力値のバリデーションのテスト
        """

        invalid_search_word_length = 51

        invalid_search_word = self.create_random_name(invalid_search_word_length)

        response = self.client.post(reverse('book:search'), {
            'book_name': invalid_search_word,
        })

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.context.get('form').errors)

        expected_message = 'この値は 50 文字以下でなければなりません( ' + str(invalid_search_word_length) + ' 文字になっています)。'
        self.assertEqual(response.context.get('form').errors.get('book_name')[0], expected_message)

    def create_random_name(self, num):
        """
        num数のランダム文字列を生成する
        """
        randlst = [random.choice(string.ascii_letters + string.digits) for i in range(num)]
        return ''.join(randlst)


class TestBookAddView(TestCase):
    """
    書籍をDBに登録するビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()
        self.client.login(username=self.user.username, password='defaultpassword')

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

        response = self.client.post(reverse('book:add'), self.book_info, follow=True)

        book = get_object_or_404(Book, title=self.book_title)
        self.assertTrue(book)

        expected_message = self.book_title + 'を登録しました。'
        messages = get_response_messages(response)
        self.assertEqual(str(messages[0]), expected_message)

        self.assertRedirects(response, book.get_absolute_url())

    def test_non_login_user_cannot_add_book(self):
        """
        非ログインユーザは書籍の登録時にログインページに遷移させられるかテスト
        """

        self.client.logout()

        response = self.client.post(reverse('book:add'), self.book_info, follow=True)

        expected_message = 'ログインしてください。'
        messages = get_response_messages(response)
        self.assertEqual(str(messages[0]), expected_message)

        self.assertRedirects(response, '/accounts/login/?next=/add/')


class TestBookDetailView(TestCase):
    """
    書籍の詳細表示を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory(username='テストユーザ')
        self.client.login(username=self.user.username, password='defaultpassword')
        self.expected_book_title = 'テストタイトル'
        self.book = BookFactory(title=self.expected_book_title)

    def test_get_book_detail(self):
        """
        書籍の詳細ページを表示する機能のテスト
        """

        response = self.client.get(reverse('book:detail', args=[self.book.uuid]))

        self.assertEqual(self.expected_book_title, response.context.get('book').title)
        self.assertEqual(self.book, response.context.get('book'))
        self.assertTemplateUsed(response, 'book/book_detail.html')

    def test_context_data(self):
        """
        context_dataの中身のテスト
        """

        comment = CommentFactory(user=self.user, book=self.book)
        favorite = FavoriteFactory(user=self.user, book=self.book)
        wanted = WantedFactory(user=self.user, book=self.book)
        form = CommentCreateForm()

        response = self.client.get(reverse('book:detail', args=[self.book.uuid]))

        context_data = response.context

        self.assertEqual(self.book, context_data.get('book'))
        self.assertIn(comment, context_data.get('comment_list'))
        self.assertTrue(form.fields, context_data.get('form').fields)
        self.assertEqual(favorite, context_data.get('favorite'))
        self.assertEqual(wanted, context_data.get('wanted'))

    def test_add_comment(self):
        """
        書籍へのコメント機能のテスト
        """

        comment_title = 'comment_title'
        comment_info = {
            'user': self.user,
            'title': comment_title,
            'score': 5.0,
            'content': 'content',
        }

        comment_info['book'] = self.book

        response = self.client.post(reverse('book:detail', kwargs={'pk': self.book.uuid}),
                                    comment_info, follow=True)

        comment = get_object_or_404(Comment, title=comment_title)
        expected_message = 'コメントを投稿しました。'
        messages = get_response_messages(response)

        self.assertTrue(comment)
        self.assertEqual(comment_title, response.context.get('comment_list')[0].title)
        self.assertEqual(str(messages[0]), expected_message)
        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': self.book.uuid}))


class TestFavoriteAddView(TestCase):
    """
    お気に入りに追加するビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()
        self.client.login(username=self.user.username, password='defaultpassword')
        self.book = BookFactory()

    def test_add_favorite_on_book_list(self):
        """
        書籍一覧画面からお気に入り追加するテスト
        """

        response = self.client.post(reverse('book:add_favorite'), {
            'book_uuid': self.book.uuid,
            'template_name': 'book_list'
        }, follow=True)

        favorite = get_object_or_404(Favorite, user=self.user, book=self.book)

        expected_message = self.book.title + 'をお気に入りに追加しました。'
        messages = get_response_messages(response)

        self.assertTrue(favorite)
        self.assertEqual(str(messages[0]), expected_message)
        self.assertRedirects(response, reverse('book:list'))

    def test_add_favorite_on_book_detail(self):
        """
        書籍詳細画面からお気に入り追加するテスト
        """

        response = self.client.post(reverse('book:add_favorite'), {
            'book_uuid': self.book.uuid,
        }, follow=True)

        favorite = get_object_or_404(Favorite, user=self.user, book=self.book)

        expected_message = self.book.title + 'をお気に入りに追加しました。'
        messages = get_response_messages(response)

        self.assertTrue(favorite)
        self.assertEqual(str(messages[0]), expected_message)
        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': self.book.uuid}))


class TestWantedAddView(TestCase):
    """
    読みたいに追加するビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()
        self.client.login(username=self.user.username, password='defaultpassword')
        self.book = BookFactory()

    def test_add_wanted_on_book_list(self):
        """
        書籍一覧画面から読みたいに追加するテスト
        """

        response = self.client.post(reverse('book:add_wanted'), {
            'book_uuid': self.book.uuid,
            'template_name': 'book_list'
        }, follow=True)

        wanted = get_object_or_404(Wanted, user=self.user, book=self.book)

        expected_message = self.book.title + 'を読みたいに追加しました。'
        messages = get_response_messages(response)

        self.assertTrue(wanted)
        self.assertEqual(str(messages[0]), expected_message)
        self.assertRedirects(response, reverse('book:list'))

    def test_add_wanted_on_book_detail(self):
        """
        書籍詳細画面から読みたいに追加するテスト
        """

        response = self.client.post(reverse('book:add_wanted'), {
            'book_uuid': self.book.uuid,
        }, follow=True)

        wanted = get_object_or_404(Wanted, user=self.user, book=self.book)

        expected_message = self.book.title + 'を読みたいに追加しました。'
        messages = get_response_messages(response)

        self.assertTrue(wanted)
        self.assertEqual(str(messages[0]), expected_message)
        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': self.book.uuid}))


class TestBookListView(TestCase):
    """
    書籍の一覧表示を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()
        self.client.login(username=self.user.username, password='defaultpassword')

    def test_list_view(self):
        """
        登録した10件の書籍が一覧表示されるかテスト
        """
        book_count = 10
        BookFactory.create_batch(book_count)

        response = self.client.get(reverse('book:list'), follow=True)

        self.assertEqual(book_count, len(response.context.get('book_list')))

    def test_context_data(self):
        """
        context_dataの中身のテスト
        """

        book = BookFactory()
        FavoriteFactory(user=self.user, book=book)
        WantedFactory(user=self.user, book=book)

        response = self.client.get(reverse('book:list'), follow=True)

        self.assertIn(book, response.context.get('book_list'))
        self.assertIn(book, response.context.get('fav_book_list'))
        self.assertIn(book, response.context.get('wanted_book_list'))


class TestFavoriteDeleteView(TestCase):
    """
    お気に入り削除を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()
        self.client.login(username=self.user.username, password='defaultpassword')
        self.book = BookFactory()

    def test_only_owner_can_delete(self):
        """
        所有者はお気に入りの削除ができることをテスト
        """

        favorite = FavoriteFactory(user=self.user, book=self.book)

        response = self.client.post(reverse('book:delete_favorite'), {
            'favorite_uuid': favorite.uuid,
            'template_name': 'book_list'
        })

        is_favorite_exist = Favorite.objects.filter(book=self.book, user=self.user).exists()

        self.assertFalse(is_favorite_exist)
        self.assertRedirects(response, reverse('book:list'))

    def non_owner_cannot_delete(self):
        """
        非所有者はお気に入りの削除ができないことをテスト
        """

        favorite = FavoriteFactory(user=self.user, book=self.book)

        self.client.logout()

        non_owner = CustomUserFactory()
        self.client.login(username=non_owner.username, password='defaultpassword')

        response = self.client.post(reverse('book:delete_favorite'), {
            'favorite_uuid': favorite.uuid,
            'template_name': 'book_list'
        })

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_non_login_user_cannnot_delete(self):
        """
        非ログインユーザはお気に入りの削除ができないことをテスト
        """

        favorite = FavoriteFactory(user=self.user, book=self.book)

        self.client.logout()

        response = self.client.post(reverse('book:delete_favorite'), {
            'favorite_uuid': favorite.uuid,
            'template_name': 'book_list'
        }, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_on_customuser_detail(self):
        """
        ユーザ詳細ページでの削除実行後のページ遷移のテスト
        """

        favorite = FavoriteFactory(user=self.user, book=self.book)

        response = self.client.post(reverse('book:delete_favorite'), {
            'favorite_uuid': favorite.uuid,
            'template_name': 'customuser_detail',
            'user_uuid': self.user.uuid
        }, follow=True)

        self.assertRedirects(response, reverse('accounts:detail', kwargs={'pk': self.user.uuid}))

    def test_delete_on_book_detail(self):
        """
        書籍詳細ページでの削除実行後のページ遷移のテスト
        """

        favorite = FavoriteFactory(user=self.user, book=self.book)

        response = self.client.post(reverse('book:delete_favorite'), {
            'favorite_uuid': favorite.uuid,
            'book_uuid': self.book.uuid
        }, follow=True)

        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': self.book.uuid}))


class TestWantedDeleteView(TestCase):
    """
    読みたい削除を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()
        self.client.login(username=self.user.username, password='defaultpassword')
        self.book = BookFactory()

    def test_only_owner_can_delete(self):
        """
        所有者は読みたいの削除ができることをテスト
        """

        wanted = WantedFactory(user=self.user, book=self.book)

        response = self.client.post(reverse('book:delete_wanted'), {
            'wanted_uuid': wanted.uuid,
            'template_name': 'book_list'
        })

        is_wanted_exist = Wanted.objects.filter(book=self.book, user=self.user).exists()

        self.assertFalse(is_wanted_exist)
        self.assertRedirects(response, reverse('book:list'))

    def non_owner_cannot_delete(self):
        """
        非所有者は読みたいの削除ができないことをテスト
        """

        wanted = WantedFactory(user=self.user, book=self.book)

        self.client.logout()

        non_owner = CustomUserFactory()
        self.client.login(username=non_owner.username, password='defaultpassword')

        response = self.client.post(reverse('book:delete_wanted'), {
            'wanted_uuid': wanted.uuid,
            'template_name': 'book_list'
        })

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_non_login_user_cannnot_delete(self):
        """
        非ログインユーザは読みたいの削除ができないことをテスト
        """

        wanted = WantedFactory(user=self.user, book=self.book)

        self.client.logout()

        response = self.client.post(reverse('book:delete_wanted'), {
            'wanted_uuid': wanted.uuid,
            'template_name': 'book_list'
        }, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_on_customuser_detail(self):
        """
        ユーザ詳細ページでの削除実行後のページ遷移のテスト
        """

        wanted = WantedFactory(user=self.user, book=self.book)

        response = self.client.post(reverse('book:delete_wanted'), {
            'wanted_uuid': wanted.uuid,
            'template_name': 'customuser_detail',
            'user_uuid': self.user.uuid
        }, follow=True)

        self.assertRedirects(response, reverse('accounts:detail', kwargs={'pk': self.user.uuid}))

    def test_delete_on_book_detail(self):
        """
        書籍詳細ページでの削除実行後のページ遷移のテスト
        """

        wanted = WantedFactory(user=self.user, book=self.book)

        response = self.client.post(reverse('book:delete_wanted'), {
            'wanted_uuid': wanted.uuid,
            'book_uuid': self.book.uuid
        }, follow=True)

        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': self.book.uuid}))


class TestCommentUpdateView(TestCase):
    """
    コメントの編集を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory(username='テストユーザ')
        self.client.login(username=self.user.username, password='defaultpassword')
        self.expected_book_title = 'テストタイトル'
        self.book = BookFactory(title=self.expected_book_title)

    def test_update_comment_get(self):
        """
        コメント編集ページにGETリクエストを送信時のテスト
        """

        comment = CommentFactory(user=self.user, book=self.book)

        response = self.client.get(reverse('book:update_comment', kwargs={
            'book_pk': self.book.uuid,
            'comment_pk': comment.uuid
        }), follow=True)

        self.assertTrue(response.context.get('form'))
        self.assertTemplateUsed('book/comment_form.html')

    def test_update_comment(self):
        """
        コメント編集ページにPOSTリクエストを送信時のテスト
        """

        book = BookFactory()
        comment = CommentFactory(book=book, user=self.user)
        comment = get_object_or_404(Comment, uuid=comment.uuid)

        expected_comment_title = 'テストタイトル'
        expected_comment_score = 5
        expected_comment_content = 'テストコンテンツ'

        response = self.client.post(reverse('book:update_comment', kwargs={
            'book_pk': book.uuid,
            'comment_pk': comment.uuid
        }),
            {
            'title': expected_comment_title,
            'score': expected_comment_score,
            'content': expected_comment_content
        }, follow=True)

        comment = get_object_or_404(Comment, uuid=comment.uuid)

        # TODO フラッシュメッセージの内容をテスト

        self.assertEqual(comment.title, expected_comment_title)
        self.assertEqual(comment.score, expected_comment_score)
        self.assertEqual(comment.content, expected_comment_content)
        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': book.uuid}))


class TestCommentDeleteView(TestCase):
    """
    コメントの削除を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory(username='テストユーザ')
        self.client.login(username=self.user.username, password='defaultpassword')
        self.expected_book_title = 'テストタイトル'
        self.book = BookFactory(title=self.expected_book_title)

    def test_delete_comment_on_customuser_detail(self):
        """
        ユーザ詳細画面から書籍に紐付いたコメントを削除するテスト
        """

        comment = CommentFactory(book=self.book, user=self.user)

        comment = get_object_or_404(Comment, uuid=comment.uuid)

        response = self.client.post(reverse('book:delete_comment', kwargs={
            'book_pk': self.book.uuid,
            'comment_pk': comment.uuid}),
            {
            'template_name': 'customuser_detail',
            'user_uuid': self.user.uuid
        }, follow=True)

        is_comment_exist = Comment.objects.filter(book=self.book, user=self.user).exists()

        expected_message = 'コメントを削除しました。'
        messages = get_response_messages(response)

        self.assertFalse(is_comment_exist)
        self.assertEqual(str(messages[0]), expected_message)
        self.assertRedirects(response, reverse('accounts:detail', kwargs={'pk': self.user.uuid}))

    def test_delete_comment_on_book_detail(self):
        """
        書籍詳細画面から書籍に紐付いたコメントを削除するテスト
        """

        book = BookFactory()
        comment = CommentFactory(book=book, user=self.user)

        comment = get_object_or_404(Comment, uuid=comment.uuid)

        response = self.client.post(reverse('book:delete_comment', kwargs={
            'book_pk': book.uuid,
            'comment_pk': comment.uuid}), follow=True)

        is_comment_exist = Comment.objects.filter(book=self.book, user=self.user).exists()

        expected_message = 'コメントを削除しました。'
        messages = get_response_messages(response)

        self.assertFalse(is_comment_exist)
        self.assertEqual(str(messages[0]), expected_message)

        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': book.uuid}))


class TestFavoriteLankingListView(TestCase):
    """
    お気に入り数の降順で一覧表示を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory(username='テストユーザ')
        self.client.login(username=self.user.username, password='defaultpassword')
        self.book = BookFactory()

    def test_book_order(self):
        """
        お気に入り追加数順にbook_listが生成されるかテスト
        """

        FavoriteFactory(user=self.user, book=self.book)
        book2 = BookFactory()

        response = self.client.get(reverse('book:favorite_lanking'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context.get('book_list')[0], self.book)
        self.assertEqual(response.context.get('book_list')[1], book2)
        self.assertTemplateUsed(response, 'book/book_fav_lanking.html')


class TestWantedLankingListView(TestCase):
    """
    読みたい数の降順で一覧表示を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory(username='テストユーザ')
        self.client.login(username=self.user.username, password='defaultpassword')
        self.book = BookFactory()

    def test_book_order(self):
        """
        読みたい追加数順にbook_listが生成されるかテスト
        """

        WantedFactory(user=self.user, book=self.book)
        book2 = BookFactory()

        response = self.client.get(reverse('book:wanted_lanking'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context.get('book_list')[0], self.book)
        self.assertEqual(response.context.get('book_list')[1], book2)
        self.assertTemplateUsed(response, 'book/book_wanted_lanking.html')
