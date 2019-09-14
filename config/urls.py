from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('spinois/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('book.urls')),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
