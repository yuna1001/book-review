from django.urls import path

from .views import CustomUserUpdateView, CustomUserDetailView, CustomUserFollowView, CustomUserUnfollowView, CustomUserListView

app_name = 'accounts'

urlpatterns = [
    path('detail/<uuid:pk>/', CustomUserDetailView.as_view(), name='detail'),
    path('update/<uuid:pk>/', CustomUserUpdateView.as_view(), name='update'),
    path('follow/<uuid:pk>/', CustomUserFollowView.as_view(), name='follow'),
    path('unfollow/<uuid:pk>/', CustomUserUnfollowView.as_view(), name='unfollow'),
    path('list/', CustomUserListView.as_view(), name='list'),
]
