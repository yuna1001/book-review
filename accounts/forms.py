from django.contrib.auth import get_user_model
from django import forms
from django.forms.widgets import FileInput

from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm


class CustomSignupForm(SignupForm):
    """
    allauthの非ソーシャルログイン用のフォームクラス
    """

    username = forms.CharField(label='ユーザ名', required=True, help_text='※必須')
    email = forms.EmailField(label='Eメール', required=True, help_text='※必須')
    profile_pic = forms.FileField(label='プロフィール画像', required=False, help_text='※任意')

    def save(self, request):
        """
        「user」を最後にreturnする必要がある。
        内部的にはadapterクラスを呼び出し、adapterクラスのsave_userを呼び出している。
        """

        user = super().save(request)
        return user


class CustomSocialSignupForm(SocialSignupForm):
    """
    ソーシャルログイン用のフォームクラス
    """

    username = forms.CharField(label='ユーザ名', required=True, help_text='※必須')
    email = forms.EmailField(label='Eメール', required=True, help_text='※必須')
    profile_pic = forms.FileField(label='プロフィール画像', required=False, help_text='※未選択の場合は、ソーシャルアカウントのプロフィール画像を設定します')

    def save(self, request):
        """
        「user」を最後にreturnする必要がある。
        内部的にはadapterクラスを呼び出し、adapterクラスのsave_userを呼び出している。
        """

        user = super().save(request)
        return user


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

        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].widget = FileInput()


class CustomUserSearchForm(forms.Form):
    """
    CustomUserの検索を行うフォームクラス
    """

    username = forms.CharField(label='ユーザ名', max_length=150)
