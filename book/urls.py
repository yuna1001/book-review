from django.urls import path

from .views import (
    AboutTemplateView, TermsOfServiceTemplateView, PrivacyPolicyTemplateView, BookSearchView, BookAddView, BookDetailView, FavoriteAddView, WantedAddView, BookListView, FavoriteDeleteView, WantedDeleteView, CommentUpdateView, CommentDeleteView, FavoriteLankingListView, WantedLankingListView)

app_name = 'book'

urlpatterns = [
    path('', AboutTemplateView.as_view(), name='about'),
    path('termsofservice/', TermsOfServiceTemplateView.as_view(), name='terms_of_service'),
    path('privacypolicy/', PrivacyPolicyTemplateView.as_view(), name='privacy_policy'),
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
    path('lanking/favorite/', FavoriteLankingListView.as_view(), name='favorite_lanking'),
    path('lanking/wanted/', WantedLankingListView.as_view(), name='wanted_lanking'),
]
