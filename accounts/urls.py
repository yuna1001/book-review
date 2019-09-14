from django.urls import path

from .views import CustomUserUpdateView, CustomUserDetailView

app_name = 'accounts'

urlpatterns = [
    path('detail/<uuid:pk>/', CustomUserDetailView.as_view(), name='detail'),
    path('update/<uuid:pk>/', CustomUserUpdateView.as_view(), name='update'),
]
