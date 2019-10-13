import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from PIL import Image

from base.tests.factory import CustomUserFactory


class TestCustomUserUpdateForm(TestCase):
    """
    カスタムユーザの更新フォームのテストクラス
    """

    def setUp(self):
        """
        テストセットアップ
        """

        from accounts.forms import CustomUserUpdateForm
        self.form = CustomUserUpdateForm

        self.user = CustomUserFactory(username='テストユーザ')

    def create_dummy_image(self):
        """
        フォームテスト用の画像オブジェクトの生成を行う
        """

        file_obj = io.BytesIO()  # メモリ上への仮保管先を生成
        width = 100
        height = 100
        img = Image.new("RGBA", (width, height), (100, 0, 0))  # 画像オブジェクトの生成
        img.save(file_obj, 'png')  # 仮保存先に保存
        file_obj.seek(0)  # 読み込み位置を先頭に
        file_obj.name = 'test.png'

        return file_obj

    def test_form_is_valid(self):
        """
        フォームのバリデーションのテスト(正常系)
        """

        data = {
            'username': 'テストユーザ2',
            'email': 'test2@example.com',
        }
        img = self.create_dummy_image()
        file_data = {'profile_pic': SimpleUploadedFile(img.name, img.read(), content_type='image/png',)}
        form = self.form(data, file_data, instance=self.user)

        self.assertTrue(form.is_valid())

    def test_form_is_invalid(self):
        """
        フォームのバリデーションのテスト(異常系)
        """

        data = {
            'username': '',
            'email': 'test',
        }

        form = self.form(data, instance=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn('このフィールドは必須です。', form.errors.get('username'))
        self.assertIn('有効なメールアドレスを入力してください。', form.errors.get('email'))


class CustomUserSearchForm(TestCase):
    """
    カスタムユーザの検索フォームのテストクラス
    """

    def setUp(self):
        """
        テストセットアップ
        """

        from accounts.forms import CustomUserSearchForm
        self.form = CustomUserSearchForm

        self.user = CustomUserFactory(username='テストユーザ')

    """
    def test_form_is_valid(self):

        data = {
            'username': 'テストユーザ',
        }

        form = self.form(data)
        print(form.errors)

        self.assertTrue(form.is_valid())
    """
