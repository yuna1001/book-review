from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views import generic

from .forms import CustomUserUpdateForm
from book.models import Comment, Favorite, Wanted
from .models import Relation


class CustomUserDetailView(generic.DetailView):
    """
    CustomUserの詳細表示を行うビュークラス
    """
    model = get_user_model()
    template_name = 'accounts/customuser_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CustomUserDetailView, self).get_context_data(**kwargs)

        user = self.get_object()

        comment_list = Comment.objects.filter(user=user)
        context['comment_list'] = comment_list

        favorite_list = Favorite.objects.filter(user=user)
        context['favorite_list'] = favorite_list

        wanted_list = Wanted.objects.filter(user=user)
        context['wanted_list'] = wanted_list

        following_list = Relation.objects.filter(user=user)
        context['following_list'] = following_list

        return context


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
