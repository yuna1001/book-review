from http import HTTPStatus
import random
import string

from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.urls import reverse

from .factory import CustomUserFactory
from ..models import CustomUser, Relation
from book.tests.factory import BookFactory, CommentFactory, FavoriteFactory, WantedFactory
from book.models import Book, Comment, Favorite, Wanted


def get_response_message(response):
    """
    Responseのフラッシュメッセージ取得関数
    """

    messages = list(response.context.get('messages'))

    return str(messages[0])


class TestCustomUserDetailView(TestCase):
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

        self.client.login(username=self.user.username, passwoer='defaultpassword')

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

        self.client.login(username=self.user, password='defaultpassword')

        another = CustomUserFactory(email='hoge@example.com')
        following_relation = Relation(user=self.user, followed=another)
        following_relation.save()

        response = self.client.get(reverse('accounts:detail', kwargs={'pk': self.user.uuid}), follow=True)

        self.assertIn(another, response.context.get('request_user_following_user_list'))


class TestCustomUserUpdateView(TestCase):

    def setUp(self):
        """
        テストセットアップ
        """

        self.user = CustomUserFactory()

    def test_update(self):
        """
        対象ユーザの更新のテスト
        """

        self.client.login(username=self.user.username, password='defaultpassword')

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

        self.client.login(username=self.user.username, password='defaultpassword')

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

        self.client.login(username=self.user.username, password='defaultpassword')

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

        self.client.login(username=self.user.username, password='defaultpassword')

        template_name = 'accounts:list'

        data = {
            'template_name': template_name
        }

        response = self.client.post(reverse('accounts:follow', kwargs={
                                    'pk': self.followed_user.uuid}), data, follow=True)

        self.assertRedirects(response, reverse(template_name))


class TestCustomUserUnfollowView(TestCase):

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
        self.client.login(username=self.user.username, password='defaultpassword')

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

        self.client.login(username=self.user.username, password='defaultpassword')

        template_name = 'accounts:list'

        data = {
            'template_name': template_name
        }

        response = self.client.post(reverse('accounts:unfollow', kwargs={
                                    'pk': self.unfollowed_user.uuid}), data, follow=True)

        self.assertRedirects(response, reverse(template_name))


class TestCustomUserListView(TestCase):

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

        self.client.login(username=self.user.username, password='defaultpassword')

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

        self.client.login(username=self.user.username, password='defaultpassword')

        data = {
            'search_word': self.username}

        response = self.client.get(reverse('accounts:list'), data, follow=True)

        self.assertEqual(len(response.context.get('customuser_list')), self.user_count)

    def test_get_search_by_non_login_user(self):
        """
        非ログインユーザもユーザ検索ができること
        ユーザ名に検索ワードが含まれるユーザが表示されることをテスト
        """

        data = {
            'search_word': self.username}

        response = self.client.get(reverse('accounts:list'), data, follow=True)

        self.assertEqual(len(response.context.get('customuser_list')), self.user_count + 1)

    def test_context_data(self):
        """
        テンプレートに渡されるcontextの内容が正しいことをテスト
        """

        self.client.login(username=self.user.username, password='defaultpassword')

        other = CustomUserFactory(email='followed_user@example.com')

        follow_relation = Relation(user=self.user, followed=other)
        follow_relation.save()

        followed_relation = Relation(user=other, followed=self.user)
        followed_relation.save()

        response = self.client.get(reverse('accounts:list'), follow=True)

        self.assertTrue(response.context.get('form'))
        self.assertTrue(response.context.get('follow_list'))
        self.assertTrue(response.context.get('follower_list'))


class TestRegisterView(TestCase):

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
        ログインユーザがユーザ登録画面へGETリクエストを行うと
        書籍検索画面にリダイレクトされることをテスト
        """

        self.client.login(username=self.user.username, password='defaultpassword')

        response = self.client.get(reverse('account_signup'), follow=True)

        self.assertRedirects(response, reverse('book:search'))
