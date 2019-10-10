from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Relation
from book.tests.factory import CustomUserFactory


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
        self.user = CustomUserFactory(username=self.test_username)

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
