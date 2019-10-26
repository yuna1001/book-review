from http import HTTPStatus
import random
import string

from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.urls import reverse

from base.tests import factory
from ..models import Book, Comment, Favorite


def get_response_message(response):
    """
    Responseのフラッシュメッセージ取得関数
    """

    messages = list(response.context.get('messages'))

    return str(messages[0])


class TestAboutTemplateView(TestCase):
    """
    aboutページを表示するビュークラスのテスト
    """

    def test_get_success(self):
        """
        aboutページにGETリクエストを行った際に
        aboutページに遷移するかテスト
        """

        response = self.client.get(reverse('book:about'), follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'about.html')


class TestTermsOfServiceTemplateView(TestCase):
    """
    利用規約ページを表示するビュークラスのテスト
    """

    def test_get_success(self):
        """
        利用規約ページにGETリクエストを行った際に
        利用規約ページに遷移するかテスト
        """

        response = self.client.get(reverse('book:terms_of_service'), follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'terms_of_service.html')


class TestPrivacyPolicyTemplateView(TestCase):
    """
    プライバシーポリシーページを表示するビュークラスのテスト
    """

    def test_get_success(self):
        """
        プライバシーポリシーページにGETリクエストを行った際に
        プライバシーポリシーページに遷移するかテスト
        """

        response = self.client.get(reverse('book:privacy_policy'), follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'privacy_policy.html')


class TestBookSearchView(TestCase):
    """
    書籍の検索を行うビュークラスのテスト
    """

    def test_post_search_request(self):
        """
        APIで書籍の検索を行う機能のテスト
        """

        data = {
            'search_word': 'Python'
        }

        response = self.client.post(reverse('book:search'), data)

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

        data = {
            'search_word': invalid_search_word
        }

        response = self.client.post(reverse('book:search'), data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.context.get('form').errors)

        expected_message = 'この値は 50 文字以下でなければなりません( ' + str(invalid_search_word_length) + ' 文字になっています)。'
        self.assertEqual(response.context.get('form').errors.get('search_word')[0], expected_message)

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

        self.user = factory.CustomUserFactory()
        self.client.login(email='test@example.com', password='defaultpassword')

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

        expected_message = self.book_title + 'を登録しました。'
        message = get_response_message(response)

        self.assertTrue(book)
        self.assertEqual(message, expected_message)
        self.assertRedirects(response, book.get_absolute_url())

    def test_non_login_user_cannot_add_book(self):
        """
        非ログインユーザは書籍の登録時にログインページに遷移させられるかテスト
        """

        self.client.logout()

        response = self.client.post(reverse('book:add'), self.book_info, follow=True)

        expected_message = 'ログインしてください。'
        message = get_response_message(response)

        self.assertEqual(message, expected_message)
        self.assertRedirects(response, '/accounts/login/?next=/add/')


class TestBookDetailView(TestCase):
    """
    書籍の詳細表示を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = factory.CustomUserFactory()
        self.client.login(email='test@example.com', password='defaultpassword')
        self.expected_book_title = 'テストタイトル'
        self.book = factory.BookFactory(title=self.expected_book_title)

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

        comment = factory.CommentFactory(user=self.user, book=self.book)
        favorite = factory.FavoriteFactory(user=self.user, book=self.book)

        response = self.client.get(reverse('book:detail', args=[self.book.uuid]))

        context_data = response.context

        self.assertEqual(self.book, context_data.get('book'))
        self.assertIn(comment, context_data.get('comment_list'))
        self.assertTrue(context_data.get('form'))
        self.assertEqual(favorite, context_data.get('favorite'))

    def test_add_comment(self):
        """
        書籍へのコメント機能のテスト
        """

        comment_title = 'comment_title'
        comment_info = {
            'user': self.user,
            'title': comment_title,
            'score': '5',
            'content': 'content',
        }

        comment_info['book'] = self.book

        response = self.client.post(reverse('book:detail', kwargs={'pk': self.book.uuid}),
                                    comment_info, follow=True)

        comment = get_object_or_404(Comment, title=comment_title)
        expected_message = 'コメントを投稿しました。'
        message = get_response_message(response)

        self.assertTrue(comment)
        self.assertEqual(comment_title, response.context.get('comment_list')[0].title)
        self.assertEqual(message, expected_message)
        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': self.book.uuid}))

    def test_non_login_user_cannnot_add_comment(self):
        """
        非ログインユーザはコメントできないこと
        フラッシュメッセージが表示されることをテスト
        """

        comment_title = 'comment_title'
        comment_info = {
            'user': self.user,
            'title': comment_title,
            'score': '5',
            'content': 'content',
        }

        comment_info['book'] = self.book

        self.client.logout()

        response = self.client.post(reverse('book:detail', kwargs={'pk': self.book.uuid}),
                                    comment_info, follow=True)

        is_comment_created = Comment.objects.filter(title=comment_title).exists()

        message = get_response_message(response)
        expected_message = 'ログインしてください。'

        self.assertFalse(is_comment_created)
        self.assertEqual(message, expected_message)

    def test_comment_is_invalid(self):
        """
        コメントフォームのバリデーションエラーの際にコメントが投稿されないこと
        フラッシュメッセージが表示されることをテスト
        """

        comment_title = 'comment_title'
        comment_info = {
            'user': self.user,
            'title': '',
            'score': '5',
            'content': 'content',
        }

        comment_info['book'] = self.book

        response = self.client.post(reverse('book:detail', kwargs={'pk': self.book.uuid}),
                                    comment_info, follow=True)

        is_comment_created = Comment.objects.filter(title=comment_title).exists()

        message = get_response_message(response)
        expected_message = 'コメントの投稿に失敗しました。'

        self.assertFalse(is_comment_created)
        self.assertEqual(message, expected_message)


class TestFavoriteAddView(TestCase):
    """
    お気に入りに追加するビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = factory.CustomUserFactory()
        self.client.login(email='test@example.com', password='defaultpassword')
        self.book = factory.BookFactory()

    def test_add_favorite_on_book_list(self):
        """
        書籍一覧画面からお気に入り追加するテスト
        """

        data = {
            'book_uuid': self.book.uuid,
            'template_name': 'book_list'
        }

        response = self.client.post(reverse('book:add_favorite'), data, follow=True)

        favorite = get_object_or_404(Favorite, user=self.user, book=self.book)

        expected_message = self.book.title + 'をお気に入りに追加しました。'
        message = get_response_message(response)

        self.assertTrue(favorite)
        self.assertEqual(message, expected_message)
        self.assertRedirects(response, reverse('book:list'))

    def test_add_favorite_on_book_detail(self):
        """
        書籍詳細画面からお気に入り追加するテスト
        """

        data = {
            'book_uuid': self.book.uuid
        }

        response = self.client.post(reverse('book:add_favorite'), data, follow=True)

        favorite = get_object_or_404(Favorite, user=self.user, book=self.book)

        expected_message = self.book.title + 'をお気に入りに追加しました。'
        message = get_response_message(response)

        self.assertTrue(favorite)
        self.assertEqual(message, expected_message)
        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': self.book.uuid}))


class TestBookListView(TestCase):
    """
    書籍の一覧表示を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = factory.CustomUserFactory()
        self.client.login(email='test@example.com', password='defaultpassword')
        self.book_count = 5

    def test_list_view(self):
        """
        登録した10件の書籍が一覧表示されるかテスト
        """

        factory.BookFactory.create_batch(self.book_count)

        response = self.client.get(reverse('book:list'), follow=True)

        self.assertEqual(self.book_count, len(response.context.get('book_list')))

    def test_list_view_no_data(self):
        """
        登録書籍が0件の際にフラッシュメッセージが表示されるか
        表示される書籍が0件かテスト
        """

        response = self.client.get(reverse('book:list'), follow=True)

        expected_message = '登録されている書籍は０件です。'
        message = get_response_message(response)

        self.assertEqual(message, expected_message)
        self.assertFalse(response.context.get('book_list'))

    def test_search_title(self):
        """
        検索キーワードを含む書籍が返されるかテスト
        書籍のタイトルが検索範囲となっているかテスト
        """

        factory.BookFactory.create_batch(self.book_count, title='Python')

        data = {
            'search_word': 'Python'
        }

        response = self.client.get(reverse('book:list'), data, follow=True)

        self.assertEqual(self.book_count, len(response.context.get('book_list')))

    def test_search_description(self):
        """
        検索キーワードを含む書籍が返されるかテスト
        書籍の説明が検索範囲となっているかテスト
        """

        factory.BookFactory.create_batch(self.book_count, description='Python')

        data = {
            'search_word': 'Python'
        }

        response = self.client.get(reverse('book:list'), data, follow=True)

        self.assertEqual(self.book_count, len(response.context.get('book_list')))

    def test_search_result_no_data(self):
        """
        検索結果が0件の際にフラッシュメッセージが表示されるか
        表示される書籍が0件かテスト
        """

        factory.BookFactory(title='Python')

        data = {
            'search_word': 'Java'
        }

        response = self.client.get(reverse('book:list'), data, follow=True)

        expected_message = '検索結果は０件です。'
        message = get_response_message(response)

        self.assertEqual(message, expected_message)
        self.assertFalse(response.context.get('book_list'))

    def test_context_data(self):
        """
        context_dataの中身のテスト
        """

        book = factory.BookFactory()
        factory.FavoriteFactory(user=self.user, book=book)

        response = self.client.get(reverse('book:list'), follow=True)

        self.assertIn(book, response.context.get('book_list'))
        self.assertIn(book, response.context.get('fav_book_list'))
        self.assertTrue(response.context.get('form'))


class TestFavoriteDeleteView(TestCase):
    """
    お気に入り削除を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = factory.CustomUserFactory()
        self.client.login(email=self.user.email, password='defaultpassword')
        self.book = factory.BookFactory()

    def test_only_owner_can_delete(self):
        """
        所有者はお気に入りの削除ができることをテスト
        """

        favorite = factory.FavoriteFactory(user=self.user, book=self.book)

        data = {
            'favorite_uuid': favorite.uuid,
            'template_name': 'book_list'
        }

        response = self.client.post(reverse('book:delete_favorite'), data)

        is_favorite_exist = Favorite.objects.filter(book=self.book, user=self.user).exists()

        self.assertFalse(is_favorite_exist)
        self.assertRedirects(response, reverse('book:list'))

    def test_non_owner_cannot_delete(self):
        """
        非所有者はお気に入りの削除ができないことをテスト
        """

        favorite = factory.FavoriteFactory(user=self.user, book=self.book)

        self.client.logout()

        non_owner = factory.CustomUserFactory(email='hoge@example.com')
        self.client.login(email=non_owner.email, password='defaultpassword')

        data = {
            'favorite_uuid': favorite.uuid,
            'template_name': 'book_list'
        }

        response = self.client.post(reverse('book:delete_favorite'), data)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_non_login_user_cannnot_delete(self):
        """
        非ログインユーザはお気に入りの削除ができないことをテスト
        """

        favorite = factory.FavoriteFactory(user=self.user, book=self.book)

        self.client.logout()

        data = {
            'favorite_uuid': favorite.uuid,
            'template_name': 'book_list'
        }

        response = self.client.post(reverse('book:delete_favorite'), data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_on_customuser_detail(self):
        """
        ユーザ詳細ページでの削除実行後のページ遷移のテスト
        """

        favorite = factory.FavoriteFactory(user=self.user, book=self.book)

        data = {
            'favorite_uuid': favorite.uuid,
            'template_name': 'customuser_detail',
            'user_uuid': self.user.uuid
        }

        response = self.client.post(reverse('book:delete_favorite'), data, follow=True)

        self.assertRedirects(response, reverse('accounts:detail', kwargs={'pk': self.user.uuid}))

    def test_delete_on_book_detail(self):
        """
        書籍詳細ページでの削除実行後のページ遷移のテスト
        """

        favorite = factory.FavoriteFactory(user=self.user, book=self.book)

        data = {
            'favorite_uuid': favorite.uuid,
            'book_uuid': self.book.uuid
        }

        response = self.client.post(reverse('book:delete_favorite'), data, follow=True)

        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': self.book.uuid}))

    def test_delete_fav_count(self):
        """
        お気に入り削除すると書籍のfav_countが-1されることをテスト
        """

        data = {
            'book_uuid': self.book.uuid,
        }

        self.client.post(reverse('book:add_favorite'), data)

        favorite = Favorite.objects.get(book=self.book)

        data = {
            'favorite_uuid': favorite.uuid,
            'template_name': 'book_fav_lanking',
        }

        self.client.post(reverse('book:delete_favorite'), data)

        self.assertEqual(self.book.fav_count, 0)


class TestCommentUpdateView(TestCase):
    """
    コメントの編集を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = factory.CustomUserFactory()
        self.client.login(email='test@example.com', password='defaultpassword')
        self.expected_book_title = 'テストタイトル'
        self.book = factory.BookFactory(title=self.expected_book_title)

    def test_update_comment_get(self):
        """
        コメント編集ページにGETリクエストを送信時のテスト
        """

        comment = factory.CommentFactory(user=self.user, book=self.book)

        kwargs = {
            'book_pk': self.book.uuid,
            'comment_pk': comment.uuid
        }

        response = self.client.get(reverse('book:update_comment', kwargs=kwargs), follow=True)

        self.assertTrue(response.context.get('form'))
        self.assertTemplateUsed('book/comment_form.html')

    def test_update_comment(self):
        """
        コメント編集ページにPOSTリクエストを送信時のテスト
        """

        book = factory.BookFactory()
        comment = factory.CommentFactory(book=book, user=self.user)
        comment = get_object_or_404(Comment, uuid=comment.uuid)

        expected_comment_title = 'テストタイトル'
        expected_comment_score = '5'
        expected_comment_content = 'テストコンテンツ'

        kwargs = {
            'book_pk': book.uuid,
            'comment_pk': comment.uuid
        }

        data = {
            'title': expected_comment_title,
            'score': expected_comment_score,
            'content': expected_comment_content
        }

        response = self.client.post(reverse('book:update_comment', kwargs=kwargs),
                                    data, follow=True)

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

        self.user = factory.CustomUserFactory()
        self.client.login(email='test@example.com', password='defaultpassword')
        self.expected_book_title = 'テストタイトル'
        self.book = factory.BookFactory(title=self.expected_book_title)

    def test_delete_comment_on_customuser_detail(self):
        """
        ユーザ詳細画面から書籍に紐付いたコメントを削除するテスト
        """

        comment = factory.CommentFactory(book=self.book, user=self.user)

        comment = get_object_or_404(Comment, uuid=comment.uuid)

        kwargs = {
            'book_pk': self.book.uuid,
            'comment_pk': comment.uuid
        }

        data = {
            'template_name': 'customuser_detail',
            'user_uuid': self.user.uuid
        }

        response = self.client.post(reverse('book:delete_comment', kwargs=kwargs),
                                    data, follow=True)

        is_comment_exist = Comment.objects.filter(book=self.book, user=self.user).exists()

        expected_message = 'コメントを削除しました。'
        message = get_response_message(response)

        self.assertFalse(is_comment_exist)
        self.assertEqual(message, expected_message)
        self.assertRedirects(response, reverse('accounts:detail', kwargs={'pk': self.user.uuid}))

    def test_delete_comment_on_book_detail(self):
        """
        書籍詳細画面から書籍に紐付いたコメントを削除するテスト
        """

        book = factory.BookFactory()
        comment = factory.CommentFactory(book=book, user=self.user)

        comment = get_object_or_404(Comment, uuid=comment.uuid)

        kwargs = {
            'book_pk': book.uuid,
            'comment_pk': comment.uuid
        }

        response = self.client.post(reverse('book:delete_comment', kwargs=kwargs), follow=True)

        is_comment_exist = Comment.objects.filter(book=self.book, user=self.user).exists()

        expected_message = 'コメントを削除しました。'
        message = get_response_message(response)

        self.assertFalse(is_comment_exist)
        self.assertEqual(message, expected_message)

        self.assertRedirects(response, reverse('book:detail', kwargs={'pk': book.uuid}))


class TestFavoriteLankingListView(TestCase):
    """
    お気に入り数の降順で一覧表示を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = factory.CustomUserFactory()
        self.client.login(email='test@example.com', password='defaultpassword')
        self.book = factory.BookFactory(fav_count=5)

    def test_book_order(self):
        """
        お気に入り追加数順にbook_listが生成されるかテスト
        """

        no_fav_book = factory.BookFactory(fav_count=0)
        one_fav_book = factory.BookFactory(fav_count=1)

        response = self.client.get(reverse('book:favorite_lanking'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context.get('book_list')[0], self.book)
        self.assertEqual(response.context.get('book_list')[1], one_fav_book)
        self.assertNotIn(no_fav_book, response.context.get('book_list'))
        self.assertTemplateUsed(response, 'book/book_fav_lanking.html')
