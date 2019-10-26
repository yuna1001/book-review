from django.test import TestCase

from django.shortcuts import reverse

from base.tests import factory


class TestBook(TestCase):
    """
    Bookモデルのテストクラス
    """

    def setUp(self):
        """
        テストセットアップ
        """

        self.book_title = 'テストブック'
        self.book = factory.BookFactory(title=self.book_title)

    def test_str(self):
        """
        __str__のテスト
        """

        self.assertEqual(str(self.book), self.book_title)

    def test_get_absoulute_url(self):
        """
        get_absolute_url()のテスト
        """

        self.assertEqual(self.book.get_absolute_url(), reverse('book:detail', kwargs={'pk': self.book.uuid}))


class TestComment(TestCase):
    """
    Commentモデルのテストクラス
    """

    def test_str(self):
        """
        __str__のテスト
        """

        expected_title = 'テストタイトル'
        comment = factory.CommentFactory(title=expected_title)

        self.assertEqual(str(comment), expected_title)


class TestFavorite(TestCase):
    """
    Favoriteモデルのテストクラス
    """

    def test_str(self):
        """
        __str__のテスト
        """

        favorite = factory.FavoriteFactory()

        self.assertEqual(str(favorite), str(favorite.uuid))
