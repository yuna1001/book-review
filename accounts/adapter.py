import requests

from django.core.files.base import ContentFile

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.utils import user_email, user_field
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    非ソーシャルアカウントユーザ用のアダプタクラス
    """

    def save_user(self, request, user, form, commit=True):
        """
        save_userをオーバライド
        ユーザ保存時の処理を定義
        """
        data = form.cleaned_data
        username = data.get('username')
        email = data.get('email')

        """
        django-allauth/allauth/account/utils.pyのuser_fieldを使用
        setattr(user, field, fieldの値)でuserのプロパティに値を入れている。
        """
        user_field(user, 'username', username)
        user_email(user, email)

        """
        プロフィール画像が選択されていれば登録する
        選択されていない場合は「no-image」を登録する
        """

        if request.FILES.get('profile_pic'):
            profile_pic_file = request.FILES.get('profile_pic')
            profile_pic_name = username + '_' + profile_pic_file.name

            user.profile_pic.save(profile_pic_name, profile_pic_file)

        if 'password1' in data:
            user.set_password(data.get('password1'))
        else:
            user.set_unusable_password()
        self.populate_username(request, user)

        if commit:
            user.save()
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    ソーシャルアカウントユーザ用のアダプタクラス
    """

    def save_user(self, request, sociallogin, form=None):

        user = sociallogin.user

        data = form.cleaned_data
        username = data.get('username')  # ソーシャルアカウントのユーザ名を自動で入れてくれる
        email = data.get('email')

        """
        django-allauth/allauth/account/utils.pyのuser_fieldを使用
        setattr(user, field, fieldの値)でuserのプロパティに値を入れている。
        """
        user_field(user, 'username', username)
        user_email(user, email)

        """
        画像が選択されていればそれをそれを登録する
        選択されていなければSNSのプロフィール画像を登録する
        """
        if request.FILES.get('profile_pic'):
            profile_pic_file = request.FILES.get('profile_pic')
            profile_pic_name = username + '_' + profile_pic_file.name

            user.profile_pic.save(profile_pic_name, profile_pic_file)
        else:
            profile_pic_url = sociallogin.account.extra_data.get(
                'profile_image_url_https', None)
            response = requests.get(profile_pic_url)

            profile_pic_name = username + '.jpg'

            user.profile_pic.save(profile_pic_name, ContentFile(response.content), save=True)

        user.set_unusable_password()
        get_account_adapter().populate_username(request, user)
        sociallogin.save(request)
        return user
