from http import HTTPStatus
import random
import string

from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.urls import reverse

from base.tests.factory import CustomUserFactory, BookFactory, CommentFactory, FavoriteFactory, WantedFactory
from ..models import CustomUser, Relation
from book.models import Book, Comment, Favorite, Wanted


def get_response_message(response):
    """
    Responseのフラッシュメッセージ取得関数
    """

    messages = list(response.context.get('messages'))

    return str(messages[0])


class TestCustomUserDetailView(TestCase):
    """
    ユーザの詳細表示を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()

    def test_get_customuser_detail_by_owner(self):
        """
        ユーザ詳細ページにGETリクエストを行うと
        対象ユーザの詳細ページに遷移することをテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        response = self.client.get(reverse('accounts:detail', kwargs={'pk': self.user.uuid}), follow=True)

        self.assertTemplateUsed(response, 'accounts/customuser_detail.html')

    def test_get_customuser_detail_by_non_login_user(self):
        """
        非ログインユーザでもGETリクエストを行うと
        対象ユーザの詳細ページに遷移することをテスト
        """

        response = self.client.get(reverse('accounts:detail', kwargs={'pk': self.user.uuid}), follow=True)
        self.assertTemplateUsed(response, 'accounts/customuser_detail.html')

    def test_get_customuser_detail_by_non_owner(self):
        """
        ログイン済みの別ユーザでもGETリクエストを行うと
        対象ユーザの詳細ページに遷移することをテスト
        """

        another = CustomUserFactory(email='hoge@examle.com')
        self.client.login(username=another.username, password='defaultpassword')

        response = self.client.get(reverse('accounts:detail', kwargs={'pk': self.user.uuid}), follow=True)
        self.assertTemplateUsed(response, 'accounts/customuser_detail.html')

    def test_context_data(self):
        """
        対象ユーザの詳細ページのHTMLに
        渡されるcontextの内容のテスト
        """

        book = BookFactory()
        favorite = FavoriteFactory(user=self.user, book=book)
        wanted = WantedFactory(user=self.user, book=book)
        comment = CommentFactory(user=self.user, book=book)

        another = CustomUserFactory(email='hoge@example.com')
        following_relation = Relation(user=self.user, followed=another)
        following_relation.save()
        followed_relation = Relation(user=another, followed=self.user)
        followed_relation.save()

        response = self.client.get(reverse('accounts:detail', kwargs={'pk': self.user.uuid}), follow=True)

        self.assertEqual(response.context.get('customuser'), self.user)
        self.assertIn(favorite, response.context.get('favorite_list'))
        self.assertIn(wanted, response.context.get('wanted_list'))
        self.assertIn(comment, response.context.get('comment_list'))
        self.assertIn(following_relation, response.context.get('following_list'))
        self.assertIn(followed_relation, response.context.get('followed_list'))

    def test_create_request_user_following_user_list(self):
        """
        ログインユーザの場合のみフォローしている
        ユーザのリストがcontextに追加されるかテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        another = CustomUserFactory(email='hoge@example.com')
        following_relation = Relation(user=self.user, followed=another)
        following_relation.save()

        response = self.client.get(reverse('accounts:detail', kwargs={'pk': self.user.uuid}), follow=True)

        self.assertIn(another, response.context.get('request_user_following_user_list'))


class TestCustomUserUpdateView(TestCase):
    """
    ユーザの更新を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()

    def test_update(self):
        """
        対象ユーザの更新のテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        response = self.client.post(reverse('accounts:update', kwargs={'pk': self.user.uuid}), {
            'username': 'test',
            'email': 'hoge@example.com',
            'profile_pic': ''
        })

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTemplateUsed(reverse('accounts:detail', kwargs={'pk': self.user.uuid}))
        self.assertEqual(self.user.username, 'test')


class TestCustomUserFollowView(TestCase):
    """
    ユーザのフォローを行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()
        self.followed_user = CustomUserFactory(email='followed_user@example.com')

    def test_follow(self):
        """
        ユーザをフォローできるかテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        response = self.client.post(reverse('accounts:follow', kwargs={'pk': self.followed_user.uuid}), follow=True)
        is_relation_created = Relation.objects.filter(user=self.user).exists()

        expected_message = self.followed_user.username + 'をフォローしました。'
        message = get_response_message(response)

        self.assertTrue(is_relation_created)
        self.assertEqual(message, expected_message)
        self.assertRedirects(response, reverse('accounts:detail', kwargs={'pk': self.followed_user.uuid}))

    def test_follow_by_non_login_user(self):
        """
        非ログインユーザがフォローしようとすると
        ログインページに遷移させられるかテスト
        """

        response = self.client.post(reverse('accounts:follow', kwargs={'pk': self.followed_user.uuid}), follow=True)

        message = get_response_message(response)
        expected_message = 'ログインしてください。'

        self.assertTrue(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(message, expected_message)
        self.assertRedirects(response, '/accounts/login/?next=/accounts/follow/{}/'.format(self.followed_user.uuid))

    def test_user_cannot_follow_myself(self):
        """
        自分自身をフォローできないこと
        フラッシュメッセージが表示されることをテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        response = self.client.post(reverse('accounts:follow', kwargs={'pk': self.user.uuid}), follow=True)
        is_relation_created = Relation.objects.filter(user=self.user).exists()

        message = get_response_message(response)
        expected_message = '自分をフォローすることはできません。'

        self.assertFalse(is_relation_created)
        self.assertEqual(message, expected_message)
        self.assertRedirects(response, reverse('accounts:detail', kwargs={'pk': self.user.uuid}))

    def test_success_url(self):
        """
        処理成功後のページ遷移が正しく行われることをテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        template_name = 'accounts:list'

        data = {
            'template_name': template_name
        }

        response = self.client.post(reverse('accounts:follow', kwargs={
                                    'pk': self.followed_user.uuid}), data, follow=True)

        self.assertRedirects(response, reverse(template_name))


class TestCustomUserUnfollowView(TestCase):
    """
    ユーザのフォロー解除を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()
        self.unfollowed_user = CustomUserFactory(email='unfollowed_user@example.com')
        self.relation = Relation(user=self.user, followed=self.unfollowed_user)
        self.relation.save()

    def test_unfollow(self):
        """
        ユーザのフォロー解除できるかテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        response = self.client.post(reverse('accounts:unfollow', kwargs={'pk': self.unfollowed_user.uuid}), follow=True)

        is_relation_deleted = Relation.objects.filter(user=self.user, followed=self.unfollowed_user).exists()

        message = get_response_message(response)
        expected_message = self.unfollowed_user.username + 'のフォローを解除しました。'

        self.assertTrue(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(is_relation_deleted)
        self.assertEqual(message, expected_message)
        self.assertRedirects(response, reverse('accounts:detail', kwargs={'pk': self.unfollowed_user.uuid}))

    def test_unfollow_by_non_login_user(self):
        """
        非ログインユーザがアンフォローしようとすると
        ログインページに遷移させられるかテスト
        """

        response = self.client.post(reverse('accounts:unfollow', kwargs={'pk': self.unfollowed_user.uuid}), follow=True)

        message = get_response_message(response)
        expected_message = 'ログインしてください。'

        self.assertTrue(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(message, expected_message)
        self.assertRedirects(response, '/accounts/login/?next=/accounts/unfollow/{}/'.format(self.unfollowed_user.uuid))

    def test_success_url(self):
        """
        処理成功後のページ遷移が正しく行われることをテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        template_name = 'accounts:list'

        data = {
            'template_name': template_name
        }

        response = self.client.post(reverse('accounts:unfollow', kwargs={
                                    'pk': self.unfollowed_user.uuid}), data, follow=True)

        self.assertRedirects(response, reverse(template_name))


class TestCustomUserListView(TestCase):
    """
    ユーザの一覧表示を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()
        self.user_count = 5
        self.username = 'テストユーザ'

        for num in range(self.user_count):
            username = self.username + str(num)
            email = 'unfollowed_user' + str(num) + '@example.com'
            CustomUserFactory(username=username, email=email)

    def test_get(self):
        """
        自分以外のユーザが一覧表示されることをテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        response = self.client.get(reverse('accounts:list'), follow=True)

        self.assertEqual(len(response.context.get('customuser_list')), self.user_count)

    def test_get_by_non_login_user(self):
        """
        非ログインユーザでも一覧表示されることをテスト
        """

        response = self.client.get(reverse('accounts:list'), follow=True)

        self.assertEqual(len(response.context.get('customuser_list')), self.user_count + 1)

    def test_get_search(self):
        """
        ユーザ名に検索ワードが含まれるユーザが表示されることをテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        data = {
            'username': self.username}

        response = self.client.get(reverse('accounts:list'), data, follow=True)

        self.assertEqual(len(response.context.get('customuser_list')), self.user_count)

    def test_get_search_with_no_result(self):
        """
        検索ワードが含まれるユーザがいない場合にユーザが表示されないこと
        フラッシュメッセージが表示されることをテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        data = {
            'username': 'hogehoge'}

        response = self.client.get(reverse('accounts:list'), data, follow=True)

        message = get_response_message(response)
        expected_message = '検索結果は０件です。'

        self.assertEqual(len(response.context.get('customuser_list')), 0)
        self.assertEqual(message, expected_message)

    def test_get_search_by_non_login_user(self):
        """
        非ログインユーザもユーザ検索ができること
        ユーザ名に検索ワードが含まれるユーザが表示されることをテスト
        """

        data = {
            'username': self.username}

        response = self.client.get(reverse('accounts:list'), data, follow=True)

        self.assertEqual(len(response.context.get('customuser_list')), self.user_count)

    def test_context_data(self):
        """
        テンプレートに渡されるcontextの内容が正しいことをテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        other = CustomUserFactory(email='followed_user@example.com')

        follow_relation = Relation(user=self.user, followed=other)
        follow_relation.save()

        followed_relation = Relation(user=other, followed=self.user)
        followed_relation.save()

        response = self.client.get(reverse('accounts:list'), follow=True)

        self.assertTrue(response.context.get('form'))
        self.assertTrue(response.context.get('follow_list'))
        self.assertTrue(response.context.get('follower_list'))


class TestCustomUserRegisterView(TestCase):
    """
    ユーザの新規登録を行うビュークラスのテスト
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()

    def test_get_register_page(self):
        """
        ユーザ登録画面に遷移することをテスト
        """

        response = self.client.get(reverse('account_signup'), follow=True)

        self.assertTemplateUsed(response, 'account/signup.html')

    def test_get_register_page_by_login_user(self):
        """
        ログイン済みユーザがユーザ登録画面へGETリクエストを行うと
        書籍検索画面にリダイレクトされることをテスト
        """

        self.client.login(email='test@example.com', password='defaultpassword')

        response = self.client.get(reverse('account_signup'), follow=True)

        self.assertRedirects(response, reverse('book:search'))

    def test_signup(self):
        """
        ユーザの新規登録ができることをテスト
        登録ボタン押下後にメール送信画面に遷移することをテスト
        """

        data = {
            'email': 'test2@example.com',
            'username': 'test2-user',
            'profile_pic': '',
            'password1': 'test-password',
            'password2': 'test-password'
        }

        response = self.client.post(reverse('account_signup'), data, follow=True)

        is_user_created = CustomUser.objects.filter(username='test2-user').exists()

        self.assertTrue(is_user_created)
        self.assertRedirects(response, reverse('account_email_verification_sent'))
