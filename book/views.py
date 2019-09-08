import environ
import json
import os
import requests

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, reverse
from django.views import generic

from book.forms import (BookSearchForm, CommentCreateForm)
from book.models import (Book, Favorite, Wanted, Comment)

env = environ.Env()
env.read_env(os.path.join(settings.BASE_DIR, '.env'))


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

        book_name = form.cleaned_data['book_name']
        self.param['title'] = book_name

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


class BookAddView(LoginRequiredMixin, generic.View):
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

        # Bookのget_absolute_url()で指定しているurlにリダイレクト
        return redirect(book)


class BookDetailView(generic.DetailView):
    """
    書籍の詳細表示を行うビュークラス
    """

    model = Book

    def get_context_data(self, **kwargs):
        """
        書籍に紐づくコメントとコメント用のフォームを渡す
        """
        context = super(BookDetailView, self).get_context_data(**kwargs)
        book_uuid = self.kwargs.get('pk')
        context['comment_list'] = Comment.objects.filter(book=book_uuid)

        context['form'] = CommentCreateForm()
        return context

    # TODO 非ログインユーザにはコメントできないようにする。
    def post(self, request, *args, **kwargs):
        """
        コメントをDBに保存する
        """
        form = CommentCreateForm(request.POST)
        comment = form.save(commit=False)
        user = self.request.user
        book = get_object_or_404(Book, uuid=self.kwargs['pk'])

        comment.user = user
        comment.book = book
        comment.save()

        return self.get_success_url()

    def get_success_url(self):
        """
        書籍の詳細ページに遷移する
        """
        return redirect(reverse('book:detail', kwargs={'pk': self.kwargs['pk']}))


class FavoriteAddView(LoginRequiredMixin, generic.View):
    """
    お気に入りの追加を行うビュークラス
    """

    def post(self, request, *args, **kwargs):
        """
        お気に入りをDBに追加する
        """

        book_uuid = request.POST.get('book_uuid')
        book = get_object_or_404(Book, uuid=book_uuid)
        user = request.user

        favorite = Favorite(user=user, book=book)
        favorite.save()

        """
        処理成功後はお気に入り追加を行ったページに遷移させる
        """
        template_name = request.POST.get('template_name')
        if template_name == 'book_list':
            return redirect(reverse('book:list'))

        return redirect(reverse('book:detail', kwargs={'pk': book_uuid}))


class WantedAddView(LoginRequiredMixin, generic.View):
    """
    読みたいの追加を行うビュークラス
    """

    def post(self, request, *args, **kwargs):
        """
        読みたいをDBに追加する
        """
        book_uuid = request.POST.get('book_uuid')
        book = get_object_or_404(Book, uuid=book_uuid)
        user = request.user

        wanted = Wanted(user=user, book=book)
        wanted.save()

        """
        処理成功後はお気に入り追加を行ったページに遷移させる
        """
        template_name = request.POST.get('template_name')
        if template_name == 'book_list':
            return redirect(reverse('book:list'))

        return redirect(reverse('book:detail', kwargs={'pk': book_uuid}))


class BookListView(generic.ListView):
    """
    書籍の一覧表示を行うビュークラス
    """
    model = Book

    def get_context_data(self, **kwargs):
        """
        ログインユーザのお気に入り・読みたいのデータをcontextに追加
        """
        context = super(BookListView, self).get_context_data(**kwargs)

        favorite_list = Favorite.objects.filter(user=self.request.user)
        context['favorite_list'] = favorite_list

        wanted_list = Wanted.objects.filter(user=self.request.user)
        context['wanted_list'] = wanted_list

        return context


class FavoriteDeleteView(LoginRequiredMixin, generic.DeleteView):
    """
    お気に入りの削除を行うビュークラス
    """
    model = Favorite

    def get_success_url(self):
        return reverse('book:list')


class WantedDeleteView(LoginRequiredMixin, generic.DeleteView):
    """
    読みたいの削除を行うビュークラス
    """
    model = Wanted

    def get_success_url(self):
        return reverse('book:list')
