from django.urls import path
from django.views.generic import TemplateView

from book.views import (
    BookSearchView, BookAddView, BookDetailView, FavoriteAddView, WantedAddView, BookListView, FavoriteDeleteView, WantedDeleteView, CommentUpdateView, CommentDeleteView)

app_name = 'book'

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('list/', BookListView.as_view(), name='list'),
    path('search/', BookSearchView.as_view(), name='search'),
    path('add/', BookAddView.as_view(), name='add'),
    path('detail/<uuid:pk>/', BookDetailView.as_view(), name='detail'),
    path('detail/<uuid:book_pk>/update/<uuid:comment_pk>/', CommentUpdateView.as_view(), name='update_comment'),
    path('detail/<uuid:book_pk>/delete/<uuid:comment_pk>/', CommentDeleteView.as_view(), name='delete_comment'),
    path('favorite/add', FavoriteAddView.as_view(), name='add_favorite'),
    path('favorite/delete/', FavoriteDeleteView.as_view(), name='delete_favorite'),
    path('wanted/add', WantedAddView.as_view(), name='add_wanted'),
    path('wanted/delete/', WantedDeleteView.as_view(), name='delete_wanted'),
]
