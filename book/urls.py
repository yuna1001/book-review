from django.urls import path

from . import views

app_name = 'book'

urlpatterns = [
    path('', views.AboutTemplateView.as_view(), name='about'),
    path('termsofservice/', views.TermsOfServiceTemplateView.as_view(), name='terms_of_service'),
    path('privacypolicy/', views.PrivacyPolicyTemplateView.as_view(), name='privacy_policy'),
    path('list/', views.BookListView.as_view(), name='list'),
    path('search/', views.BookSearchView.as_view(), name='search'),
    path('add/', views.BookAddView.as_view(), name='add'),
    path('detail/<uuid:pk>/', views.BookDetailView.as_view(), name='detail'),
    path('detail/<uuid:book_pk>/update/<uuid:comment_pk>/', views.CommentUpdateView.as_view(), name='update_comment'),
    path('detail/<uuid:book_pk>/delete/<uuid:comment_pk>/', views. CommentDeleteView.as_view(), name='delete_comment'),
    path('favorite/add', views.FavoriteAddView.as_view(), name='add_favorite'),
    path('favorite/delete/', views.FavoriteDeleteView.as_view(), name='delete_favorite'),
    path('lanking/favorite/', views.FavoriteLankingListView.as_view(), name='favorite_lanking'),
]
