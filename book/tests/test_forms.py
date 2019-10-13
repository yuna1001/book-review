from django.test import TestCase

from base.tests import factory


class TestBookSearchForm(TestCase):
    """
    書籍検索フォームのテストクラス
    """

    def setUp(self):
        """
        テストセットアップ
        """

        from book.forms import BookSearchForm
        self.form = BookSearchForm

    def test_form_is_valid(self):
        """
        フォームのバリデーションのテスト(正常系)
        """

        data = {
            'search_word': 'テスト',
        }

        form = self.form(data)

        self.assertTrue(form.is_valid())

    def test_form_is_invalid(self):
        """
        フォームのバリデーションのテスト(異常系)
        """

        data = {
            'search_word': ''
        }

        form = self.form(data)

        self.assertFalse(form.is_valid())
        self.assertIn('このフィールドは必須です。', form.errors.get('search_word'))


class TestCommentCreationForm(TestCase):
    """
    書籍検索フォームのテストクラス
    """

    def setUp(self):
        """
        テストセットアップ
        """
        from book.forms import CommentCreateForm
        self.form = CommentCreateForm

        self.book = factory.BookFactory(title='テストタイトル')

    def test_form_is_valid(self):
        """
        コメント投稿時のフォームのバリデーションのテスト(正常系)
        """

        data = {
            'title': 'テストタイトル',
            'score': 1.5,
            'content': 'テストコンテンツ'
        }

        form = self.form(data)

        self.assertTrue(form.is_valid())

    def test_form_is_invalid(self):
        """
        コメント投稿時のフォームのバリデーションのテスト(正常系)
        """

        data = {
            'title': '',
            'score': 1.5,
            'content': 'テストコンテンツ'
        }

        form = self.form(data)

        self.assertFalse(form.is_valid())
        self.assertIn('このフィールドは必須です。', form.errors.get('title'))

    def test_update_form_is_valid(self):
        """
        コメント編集時のフォームのバリデーションのテスト(正常系)
        """

        comment = factory.CommentFactory()

        data = {
            'title': 'テストタイトル',
            'score': 1.5,
            'content': 'テストコンテンツ'
        }

        form = self.form(data, instance=comment)

        self.assertTrue(form.is_valid())

    def test_update_form_is_invalid(self):
        """
        コメント投稿時のフォームのバリデーションのテスト(異常系)
        """

        comment = factory.CommentFactory()

        data = {
            'title': '',
            'score': 1.5,
            'content': 'テストコンテンツ'
        }

        form = self.form(data, instance=comment)

        self.assertFalse(form.is_valid())
        self.assertIn('このフィールドは必須です。', form.errors.get('title'))
