from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Relation
from base.tests.factory import CustomUserFactory


class TestCustomUser(TestCase):
    """
    カスタムユーザモデルのテストクラス
    """

    def setUp(self):
        """
        テストセットアップ
        """
        self.model = get_user_model()
        self.test_username = 'テストユーザ'
        self.test_email = 'test@example.com'
        self.user = CustomUserFactory(username=self.test_username, email=self.test_email)

    def test_create_user(self):
        """
        create_user()でユーザを作成できることをテスト
        """

        user = get_user_model().objects.create_user(username='テストユーザ2', email='test2@example.com', password='pass')

        self.assertTrue(user)

    def test_create_user_with_same_username(self):
        """
        create_user()でユーザを作成する際に同一ユーザ名で作成できないことをテスト
        """

        self.assertRaises(Exception, get_user_model().objects.create_user,
                          username=self.test_username, email='test2@example.com', password='pass')

    def test_create_user_with_same_email(self):
        """
        create_user()でユーザを作成する際に同一Eメールで作成できないことをテスト
        """

        self.assertRaises(Exception, get_user_model().objects.create_user,
                          username='テストユーザ2', email=self.test_email, password='pass')

    def test_create_user_with_non_email(self):
        """
        create_user()でユーザを作成する際にEメール無しだとエラーが発生することをテスト
        """

        self.assertRaises(Exception, get_user_model().objects.create_user,
                          username='テストユーザ2', email='', password='pass', msg='Emailを入力してください')

    def test_create_superuser(self):
        """
        create_superuser()でユーザを作成できることをテスト
        """

        user = get_user_model().objects.create_superuser(username='テストユーザ2', email='test2@example.com', password='pass')

        self.assertTrue(user)

    def test_create_superuser_with_same_username(self):
        """
        create_superuser()でユーザを作成する際に同一ユーザ名で作成できないことをテスト
        """

        self.assertRaises(Exception, get_user_model().objects.create_superuser,
                          username=self.test_username, email='test2@example.com', password='pass')

    def test_create_superuser_with_same_email(self):
        """
        create_superuser()でユーザを作成する際に同一Eメールで作成できないことをテスト
        """

        self.assertRaises(Exception, get_user_model().objects.create_superuser,
                          username='テストユーザ2', email=self.test_email, password='pass')

    def test_create_superuser_with_is_staff_false(self):
        """
        create_superuser()でユーザを作成する際に
        is_staffがFalseの場合にエラーが発生することをテスト
        """

        self.assertRaises(Exception, get_user_model().objects.create_superuser,
                          username='テストユーザ2', email=self.test_email, password='pass', is_staff=False, msg='Superuser must have is_staff=True.')

    def test_create_superuser_with_is_superuser_false(self):
        """
        create_superuser()でユーザを作成する際に
        is_superuserがFalseの場合にエラーが発生することをテスト
        """

        self.assertRaises(Exception, get_user_model().objects.create_superuser,
                          username='テストユーザ2', email=self.test_email, password='pass', is_superuser=False, msg='Superuser must have is_superuser=True.')

    def test_filter_by_username(self):
        """
        ユーザ検索時のフィルタ関数のテスト
        """

        self.assertTrue(self.model.filter_by_username(self.test_username))
        self.assertFalse(self.model.filter_by_username('hoge'))

    def test_get_followers(self):
        """
        ユーザがフォローしているカスタムユーザのリストを取得する関数のテスト
        フォロー0人の場合は空リストが返ってくること
        フォローしているユーザがリストに含まれていること
        """

        self.assertFalse(self.user.get_followers())

        followed_user = CustomUserFactory(email='test2@example.com')
        follow_relation = Relation(user=self.user, followed=followed_user)
        follow_relation.save()

        self.assertIn(followed_user, self.user.get_followers())
