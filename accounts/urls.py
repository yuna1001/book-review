from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('detail/<uuid:pk>/', views.CustomUserDetailView.as_view(), name='detail'),
    path('update/<uuid:pk>/', views.CustomUserUpdateView.as_view(), name='update'),
    path('follow/<uuid:pk>/', views.CustomUserFollowView.as_view(), name='follow'),
    path('unfollow/<uuid:pk>/', views.CustomUserUnfollowView.as_view(), name='unfollow'),
    path('list/', views.CustomUserListView.as_view(), name='list'),
]
