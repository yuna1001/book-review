from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {
            "fields": (
                'username', 'email'
            ),
        }),
    )

    list_display = ('uuid', 'username', 'email', 'is_staff')
    search_fields = ('username', 'email')


admin.site.register(CustomUser, CustomUserAdmin)
