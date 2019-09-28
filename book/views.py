import json
import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, reverse
from django.views import generic


import environ
import requests

from .forms import (BookSearchForm, CommentCreateForm)
from .models import (Book, Favorite, Wanted, Comment)


env = environ.Env()
env.read_env(os.path.join(settings.BASE_DIR, '.env'))


class OnlyOwnerMixin(UserPassesTestMixin):
    """
    レコード所有者にのみ権限を付与するパーミッション定義クラス
    """
    raise_exception = True  # 他ユーザの投稿を編集・削除しようとすると403ページに遷移

    def test_func(self):
        """
        レコードのuserのpkとリクエストuserのpkを比較
        """
        user = self.request.user
        obj = self.get_object()

        return user.pk == obj.user.pk


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


class BookSearchView(generic.View):
    """
    書籍検索を行うビュークラス
    """

    endpoint_url = 'https://app.rakuten.co.jp/services/api/BooksBook/Search/20170404?'

    param = {}
    param['affiliateId'] = env('affiliate_id')
    param['applicationId'] = env('application_id')
    param['elements'] = 'isbn,title,author,publisherName,itemCaption,itemPrice,affiliateUrl,largeImageUrl,salesDate'

    template_name = 'book/book_search.html'

    def get(self, request, *args, **kwargs):
        context = {
            'form': BookSearchForm(),
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        入力された検索ワードを元にAPIをコールする
        """

        form = BookSearchForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        search_word = form.cleaned_data['search_word']
        self.param['title'] = search_word

        response = requests.get(self.endpoint_url, self.param)
        response_json = json.loads(response.text)
        items_list = response_json.get('Items')

        """
        検索結果に書籍データがあれば、レンダリング用のbook_listに追加する
        DBに登録済みの書籍は表示しないようbook_listに入れない
        """
        saved_book_list = Book.objects.all()
        book_list = []
        if items_list:
            for book in items_list:
                book = book.get('Item')
                book_list.append(book)

        if saved_book_list:
            for saved_book in saved_book_list:
                for i, book in enumerate(book_list):
                    if book.get('isbn') == saved_book.isbn:
                        book_list.pop(i)

        return render(self.request, self.template_name, {'form': form, 'book_list': book_list})


class BookAddView(CustomLoginRequiredMixin, generic.View):
    """
    書籍の登録を行うビュークラス
    """

    def post(self, request, *args, **kwargs):
        """
        POSTされた書籍情報を元にDBに登録する
        """

        # <input type=hidden>の要素の値を取得
        book_isbn = request.POST.get('book_isbn')
        book_title = request.POST.get('book_title')
        book_author = request.POST.get('book_author')
        book_image_url = request.POST.get('book_image_url')
        book_description = request.POST.get('book_description')
        book_price = request.POST.get('book_price')
        book_publisher = request.POST.get('book_publisher')
        book_published_date = request.POST.get('book_published_date')
        book_affiliate_url = request.POST.get('book_affiliate_url')

        book = Book(
            isbn=book_isbn,
            title=book_title,
            author=book_author,
            image_url=book_image_url,
            description=book_description,
            price=book_price,
            publisher=book_publisher,
            published_date=book_published_date,
            affiliate_url=book_affiliate_url
        )
        book.save()

        message = book_title + 'を登録しました。'
        messages.info(request, message)

        # Bookのget_absolute_url()で指定しているurlにリダイレクト
        return redirect(book)


class BookDetailView(generic.DetailView):
    """
    書籍の詳細表示を行うビュークラス
    """

    model = Book

    def get_context_data(self, **kwargs):
        """
        次の内容をcontextに含める
        書籍に紐づくコメント・コメント用フォーム
        ログインユーザが書籍をお気に入り・読みたいに追加しているか(bool)
        """
        context = super(BookDetailView, self).get_context_data(**kwargs)

        book = context.get("object")
        context['comment_list'] = Comment.objects.filter(book=book)

        context['form'] = CommentCreateForm()

        if self.request.user.is_authenticated:
            added_favorite = Favorite.objects.filter(user=self.request.user, book=book).exists()
            if added_favorite:
                favorite = Favorite.objects.get(user=self.request.user, book=book)
                context['favorite'] = favorite

            added_wanted = Wanted.objects.filter(user=self.request.user, book=book).exists()
            if added_wanted:
                wanted = Wanted.objects.get(user=self.request.user, book=book)
                context['wanted'] = wanted

        return context

    def post(self, request, *args, **kwargs):
        """
        コメントをDBに保存する
        """
        if not self.request.user.is_authenticated:
            message = 'ログインしてください。'
            messages.info(request, message)
            return redirect(reverse('book:detail', kwargs={'pk': self.kwargs['pk']}))

        form = CommentCreateForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            user = self.request.user
            book = get_object_or_404(Book, uuid=self.kwargs['pk'])

            comment.user = user
            comment.book = book
            comment.save()

            message = 'コメントを投稿しました。'
            messages.info(request, message)
        else:
            message = 'コメントの投稿に失敗しました。'
            messages.info(request, message)

        return self.get_success_url()

    def get_success_url(self):
        """
        書籍の詳細ページに遷移する
        """
        return redirect(reverse('book:detail', kwargs={'pk': self.kwargs['pk']}))


class FavoriteAddView(CustomLoginRequiredMixin, generic.View):
    """
    お気に入りの追加を行うビュークラス
    """

    def post(self, request, *args, **kwargs):
        """
        お気に入りをDBに追加する
        """

        user = request.user
        book_uuid = request.POST.get('book_uuid')
        book = get_object_or_404(Book, uuid=book_uuid)

        favorite = Favorite(user=user, book=book)
        favorite.save()

        book.fav_count += 1
        book.save()

        message = book.title + 'をお気に入りに追加しました。'
        messages.info(request, message)

        """
        処理成功後はお気に入りの追加を行ったページに遷移させる
        """

        template_name = request.POST.get('template_name')
        if template_name == 'book_list':
            return redirect(reverse('book:list'))
        if template_name == 'book_fav_lanking':
            return redirect(reverse('book:favorite_lanking'))
        if template_name == 'book_wanted_lanking':
            return redirect(reverse('book:wanted_lanking'))

        return redirect(reverse('book:detail', kwargs={'pk': book_uuid}))


class WantedAddView(CustomLoginRequiredMixin, generic.View):
    """
    読みたいの追加を行うビュークラス
    """

    def post(self, request, *args, **kwargs):
        """
        読みたいをDBに追加する
        """

        user = request.user
        book_uuid = request.POST.get('book_uuid')
        book = get_object_or_404(Book, uuid=book_uuid)

        wanted = Wanted(user=user, book=book)
        wanted.save()

        book.wanted_count += 1
        book.save()

        message = book.title + 'を読みたいに追加しました。'
        messages.info(request, message)

        """
        処理成功後は読みたいの追加を行ったページに遷移させる
        """
        template_name = request.POST.get('template_name')
        if template_name == 'book_list':
            return redirect(reverse('book:list'))
        if template_name == 'book_fav_lanking':
            return redirect(reverse('book:favorite_lanking'))
        if template_name == 'book_wanted_lanking':
            return redirect(reverse('book:wanted_lanking'))

        return redirect(reverse('book:detail', kwargs={'pk': book_uuid}))


class BookListView(generic.ListView):
    """
    書籍の一覧表示を行うビュークラス
    """
    model = Book

    def get_queryset(self):
        """
        検索キーワードに該当する書籍データを返す
        """

        queryset = super().get_queryset()

        search_word = self.request.GET.get('search_word')

        if search_word:
            queryset = queryset.filter(
                Q(title__icontains=search_word) |
                Q(description__icontains=search_word)
            )

        if not queryset:
            message = '検索結果は０件です。'
            messages.info(self.request, message)

        return queryset

    def get_context_data(self, **kwargs):
        """
        ユーザのお気に入り・読みたいのデータをcontextに追加
        """
        context = super(BookListView, self).get_context_data(**kwargs)

        form = BookSearchForm(self.request.GET)
        context['form'] = form

        # ログインユーザの場合は、
        # お気に入り登録済み書籍・読みたい登録済み書籍の変数をcontextに追加
        if self.request.user.is_authenticated:
            favorite_list = Favorite.objects.filter(user=self.request.user)
            fav_book_list = [fav.book for fav in favorite_list]
            context['fav_book_list'] = fav_book_list

            wanted_list = Wanted.objects.filter(user=self.request.user)
            wanted_book_list = [wanted.book for wanted in wanted_list]
            context['wanted_book_list'] = wanted_book_list

        return context


class FavoriteDeleteView(OnlyOwnerMixin, CustomLoginRequiredMixin, generic.DeleteView):
    """
    お気に入りの削除を行うビュークラス
    """
    model = Favorite

    def get_object(self):
        favorite_uuid = self.request.POST.get('favorite_uuid')
        favorite = Favorite.objects.get(uuid=favorite_uuid)
        return favorite

    def delete(self, request, *args, **kwargs):
        """
        対象のFavoriteを削除する
        """
        favorite = self.get_object()
        book = favorite.book

        if book.fav_count:
            book.fav_count -= 1
            book.save()

        favorite.delete()

        message = favorite.book.title + 'をお気に入りから削除しました。'
        messages.info(request, message)

        success_url = self.get_success_url()

        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        """
        処理成功後はお気に入りの削除を行ったページに遷移させる
        """

        template_name = self.request.POST.get('template_name')
        if template_name == 'book_list':
            return reverse('book:list')
        if template_name == 'customuser_detail':
            return reverse('accounts:detail', kwargs={'pk': str(self.request.POST['user_uuid'])})
        if template_name == 'book_fav_lanking':
            return reverse('book:favorite_lanking')
        if template_name == 'book_wanted_lanking':
            return reverse('book:wanted_lanking')

        return reverse('book:detail', kwargs={'pk': str(self.request.POST['book_uuid'])})


class WantedDeleteView(OnlyOwnerMixin, CustomLoginRequiredMixin, generic.DeleteView):
    """
    読みたいの削除を行うビュークラス
    """
    model = Wanted

    def get_object(self):
        wanted_uuid = self.request.POST.get('wanted_uuid')
        wanted = Wanted.objects.get(uuid=wanted_uuid)
        return wanted

    def delete(self, request, *args, **kwargs):
        """
        対象のWantedを削除する
        """
        wanted = self.get_object()
        book = wanted.book

        if book.wanted_count:
            book.wanted_count -= 1
            book.save()

        wanted.delete()

        message = wanted.book.title + 'を読みたいから削除しました。'
        messages.info(request, message)

        success_url = self.get_success_url()

        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        """
        処理成功後は読みたいの削除を行ったページに遷移させる
        """
        template_name = self.request.POST.get('template_name')
        if template_name == 'book_list':
            return reverse('book:list')
        if template_name == 'customuser_detail':
            return reverse('accounts:detail', kwargs={'pk': str(self.request.POST['user_uuid'])})
        if template_name == 'book_fav_lanking':
            return reverse('book:favorite_lanking')
        if template_name == 'book_wanted_lanking':
            return reverse('book:wanted_lanking')

        return reverse('book:detail', kwargs={'pk': str(self.request.POST['book_uuid'])})


# TODO コメント編集後のフラッシュメッセージを追加
class CommentUpdateView(OnlyOwnerMixin, CustomLoginRequiredMixin, generic.UpdateView):
    """
    コメントの編集を行うビュークラス
    """
    model = Comment
    form_class = CommentCreateForm
    template_name = 'book/comment_form.html'

    def get_object(self, queryset=None):
        """
        編集対象のコメントを習得する
        """
        if queryset is None:
            queryset = self.get_queryset()

        comment_uuid = self.kwargs['comment_pk']
        queryset = queryset.filter(uuid=comment_uuid)

        return queryset.get()

    def form_valid(self, form):
        """
        フォームの入力内容を元にコメントを更新する
        """
        comment = form.save(commit=False)
        user = self.request.user
        book = Book.objects.get(uuid=self.kwargs['book_pk'])

        comment.user = user
        comment.book = book

        comment.save()

        return redirect(self.get_success_url())

    def get_success_url(self):
        """
        処理成功後はコメントが紐づく書籍のページに遷移させる
        """

        return reverse('book:detail', kwargs={'pk': self.kwargs['book_pk']})


class CommentDeleteView(OnlyOwnerMixin, CustomLoginRequiredMixin, generic.DeleteView):
    """
    コメントの削除を行うビュークラス
    """
    model = Comment

    def get_object(self, queryset=None):
        """
        削除対象のコメントを習得する
        """
        if queryset is None:
            queryset = self.get_queryset()

        comment_uuid = self.kwargs['comment_pk']
        queryset = queryset.filter(uuid=comment_uuid)

        return queryset.get()

    def delete(self, request, *args, **kwargs):
        """
        コメントの削除とフラッシュメッセージを表示する
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()

        message = 'コメントを削除しました。'
        messages.info(request, message)

        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        """
        処理成功後はコメント削除を行ったページに遷移させる
        """

        template_name = self.request.POST.get('template_name')

        if template_name == 'customuser_detail':
            return reverse('accounts:detail', kwargs={'pk': str(self.request.POST['user_uuid'])})

        return reverse('book:detail', kwargs={'pk': self.kwargs['book_pk']})


class FavoriteLankingListView(generic.ListView):
    model = Book
    template_name = 'book/book_fav_lanking.html'

    def get_queryset(self):
        """
        お気に入り追加数で書籍を取得
        """

        queryset = Book.objects.filter(fav_count__gt=0).order_by('-fav_count')
        return queryset

    def get_context_data(self, **kwargs):
        """
        ユーザのお気に入り・読みたいのデータをcontextに追加
        """
        context = super(FavoriteLankingListView, self).get_context_data(**kwargs)

        # ログインユーザの場合は、
        # お気に入り登録済み書籍・読みたい登録済み書籍の変数をcontextに追加
        if self.request.user.is_authenticated:
            favorite_list = Favorite.objects.filter(user=self.request.user)
            fav_book_list = [fav.book for fav in favorite_list]
            context['fav_book_list'] = fav_book_list

            wanted_list = Wanted.objects.filter(user=self.request.user)
            wanted_book_list = [wanted.book for wanted in wanted_list]
            context['wanted_book_list'] = wanted_book_list

        return context


class WantedLankingListView(generic.ListView):
    model = Book
    template_name = 'book/book_wanted_lanking.html'

    def get_queryset(self):
        """
        読みたい追加数で書籍を取得
        """

        queryset = Book.objects.filter(wanted_count__gt=0).order_by('-wanted_count')
        return queryset

    def get_context_data(self, **kwargs):
        """
        ユーザのお気に入り・読みたいのデータをcontextに追加
        """
        context = super(WantedLankingListView, self).get_context_data(**kwargs)

        # ログインユーザの場合は、
        # お気に入り登録済み書籍・読みたい登録済み書籍の変数をcontextに追加
        if self.request.user.is_authenticated:
            favorite_list = Favorite.objects.filter(user=self.request.user)
            fav_book_list = [fav.book for fav in favorite_list]
            context['fav_book_list'] = fav_book_list

            wanted_list = Wanted.objects.filter(user=self.request.user)
            wanted_book_list = [wanted.book for wanted in wanted_list]
            context['wanted_book_list'] = wanted_book_list

        return context
