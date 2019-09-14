from django.contrib.auth import get_user_model
from django import forms
from django.forms.widgets import FileInput


class CustomUserUpdateForm(forms.ModelForm):
    """
    CustomUserの更新を行うフォームクラス
    """
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'profile_pic')

    def __init__(self, *args, **kwargs):
        """
        ImageFieldのフォームに画像クリアのチェックボックスを
        表示させないよう、widgetをFileInputに変更
        """

        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['profile_pic'].widget = FileInput()
