import environ
import json
import os
import requests

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, reverse
from django.views import generic

from book.forms import BookSearchForm
from book.models import Book, Favorite, Wanted

env = environ.Env()
env.read_env(os.path.join(settings.BASE_DIR, '.env'))


class BookSearchView(generic.View):

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

        form = BookSearchForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        book_name = form.cleaned_data['book_name']
        self.param['title'] = book_name

        response = requests.get(self.endpoint_url, self.param)
        response_json = json.loads(response.text)
        items_list = response_json.get('Items')

        if items_list:
            book_list = []
            for book in items_list:
                book = book.get('Item')
                book_list.append(book)

            return render(self.request, self.template_name, {'form': form, 'book_list': book_list})
        return render(self.request, self.template_name, {'form': form})


class BookAddView(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
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
    model = Book


class FavoriteAddView(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        book_uuid = request.POST.get('book_uuid')
        book = get_object_or_404(Book, uuid=book_uuid)
        print(request.user)
        user = request.user

        favorite = Favorite(user=user, book=book)
        favorite.save()

        return redirect(reverse('book:detail', kwargs={'pk': book_uuid}))


class WantedAddView(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        book_uuid = request.POST.get('book_uuid')
        book = get_object_or_404(Book, uuid=book_uuid)
        print(request.user)
        user = request.user

        wanted = Wanted(user=user, book=book)
        wanted.save()

        return redirect(reverse('book:detail', kwargs={'pk': book_uuid}))
