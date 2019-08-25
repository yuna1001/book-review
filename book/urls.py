from django.urls import path
from django.views.generic import TemplateView
from book.views import BookSearchView, BookAddView, BookDetailView, FavoriteAddView, WantedAddView

app_name = 'book'

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('search/', BookSearchView.as_view(), name='search'),
    path('add/', BookAddView.as_view(), name='add'),
    path('detail/<uuid:pk>/', BookDetailView.as_view(), name='detail'),
    path('favorite/', FavoriteAddView.as_view(), name='add_favorite'),
    path('wanted/', WantedAddView.as_view(), name='add_wanted'),
]
