from django.contrib.auth import get_user_model
from django import forms
from django.forms.widgets import FileInput

from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm


class CustomSignupForm(SignupForm):
    """
    allauthの非ソーシャルログイン用のフォームクラス
    """
    profile_pic = forms.FileField(label=('プロフィール画像'), required=False)

    def save(self, request):
        """
        「user」を最後にreturnする必要がある。
        内部的にはadapterクラスを呼び出し、adapterクラスのsave_userを呼び出している。
        """
        user = super(CustomSignupForm, self).save(request)
        return user


class CustomSocialSignupForm(SocialSignupForm):
    """
    ソーシャルログイン用のフォームクラス
    """

    profile_pic = forms.FileField(label=('プロフィール画像'), required=False)

    def save(self, request):
        """
        「user」を最後にreturnする必要がある。
        内部的にはadapterクラスを呼び出し、adapterクラスのsave_userを呼び出している。
        """
        user = super(CustomSocialSignupForm, self).save(request)
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

        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['profile_pic'].widget = FileInput()


class CustomUserSearchForm(forms.ModelForm):
    """
    CustomUserの検索を行うフォームクラス
    """

    class Meta:
        model = get_user_model()
        fields = ('username',)
