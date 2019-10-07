from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.views import generic


from .forms import CustomUserUpdateForm, CustomUserSearchForm
from book.models import Comment, Favorite, Wanted
from .models import CustomUser, Relation


class CustomLoginRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        '''LoginRequiredMixinの関数を上書き
            ログインしてない場合はフラッシュメッセージを表示させる
        '''
        if not request.user.is_authenticated:
            message = 'ログインしてください。'
            messages.info(request, message)
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class CustomUserDetailView(generic.DetailView):
    """
    CustomUserの詳細表示を行うビュークラス
    """
    model = get_user_model()
    template_name = 'accounts/customuser_detail.html'

    def get_context_data(self, **kwargs):
        """
        ユーザ詳細ページに表示する情報をcontextに追加する
        """
        context = super(CustomUserDetailView, self).get_context_data(**kwargs)

        user = self.get_object()

        favorite_list = Favorite.objects.filter(user=user)
        context['favorite_list'] = favorite_list

        wanted_list = Wanted.objects.filter(user=user)
        context['wanted_list'] = wanted_list

        comment_list = Comment.objects.filter(user=user)
        context['comment_list'] = comment_list

        following_list = Relation.objects.filter(user=user)
        context['following_list'] = following_list

        followed_list = Relation.objects.filter(followed__in=[user])
        context['followed_list'] = followed_list

        request_user_following_user_list = self.create_request_user_following_user_list()
        context['request_user_following_user_list'] = request_user_following_user_list

        return context

    def create_request_user_following_user_list(self):
        """
        ログインユーザの場合のみcontext用のフォローリストを作成する
        """
        if not self.request.user.is_authenticated:
            return []

        following_list = Relation.objects.filter(user=self.request.user)
        request_user_following_user_list = [relation.followed for relation in following_list]

        return request_user_following_user_list


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


class CustomUserFollowView(CustomLoginRequiredMixin, generic.View):
    """
    ユーザのフォローを行うビュークラス
    """

    def post(self, request, *args, **kwargs):
        """
        pkを元に対象のユーザをフォローする
        """

        user = self.request.user
        followed_user = CustomUser.objects.get(uuid=self.kwargs['pk'])

        relation = Relation(user=user, followed=followed_user)
        relation.save()

        return redirect(self.get_success_url())

    def get_success_url(self):
        template_name = self.request.POST.get('template_name')

        if template_name:
            return reverse(template_name)
        return reverse('accounts:detail', kwargs={'pk': self.kwargs['pk']})


class CustomUserUnfollowView(CustomLoginRequiredMixin, generic.View):
    """
    ユーザのフォロー解除を行うビュークラス
    """

    def post(self, request, *args, **kwargs):
        """
        pkを元に対象のユーザのフォローを解除する
        """

        user = self.request.user
        unfollowd_user = CustomUser.objects.get(uuid=self.kwargs['pk'])

        relation = Relation.objects.get(user=user, followed=unfollowd_user)
        relation.delete()

        return redirect(self.get_success_url())

    def get_success_url(self):
        template_name = self.request.POST.get('template_name')

        if template_name:
            return reverse(template_name)
        return reverse('accounts:detail', kwargs={'pk': self.kwargs['pk']})


class CustomUserListView(generic.ListView):
    """
    ユーザの一覧表示を行うビュークラス
    """
    model = CustomUser
    template_name = 'accounts/customuser_list.html'

    def get_queryset(self):
        """
        一覧表示するユーザ情報を取得する
        """

        queryset = super().get_queryset()

        search_word = self.request.GET.get('username')

        if search_word:
            queryset = queryset.filter(username__icontains=search_word)

        if not queryset:
            message = '検索結果は０件です。'
            messages.info(self.request, message)

        return queryset

    def get_context_data(self, **kwargs):
        """
        ユーザのフォロー・フォロワーのデータをcontextに追加
        """
        context = super(CustomUserListView, self).get_context_data(**kwargs)

        # 検索時は検索ワードを検索フォームに保持する
        if self.request.GET:
            form = CustomUserSearchForm(self.request.GET)
        else:
            form = CustomUserSearchForm()

        context['form'] = form

        if self.request.user.is_authenticated:
            follow_relation = Relation.objects.filter(user=self.request.user)
            follow_list = [follow.followed for follow in follow_relation]
            context['follow_list'] = follow_list

            follower_relation = Relation.objects.filter(followed=self.request.user)
            follower_list = [follower.user for follower in follower_relation]
            context['follower_list'] = follower_list

        return context
