from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views import generic

from .forms import CustomUserUpdateForm


class CustomUserDetailView(generic.DetailView):
    """
    CustomUserの詳細表示を行うビュークラス
    """
    model = get_user_model()
    template_name = 'accounts/customuser_detail.html'


class CustomUserUpdateView(generic.UpdateView):
    """
    CustomUserの更新を行うビュークラス
    """
    model = get_user_model()
    form_class = CustomUserUpdateForm
    template_name = 'accounts/customuser_form.html'

    def get_success_url(self):
        """
        処理成功後は対象のユーザ詳細ページに遷移させる
        """
        return reverse('accounts:detail', kwargs={'pk': self.request.user.uuid})
