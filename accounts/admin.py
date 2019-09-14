from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        ('User Infomation', {
            'fields': (
                'username', 'email', 'profile_pic'
            ),
        },),
        ('Authorization', {
            'fields': (
                'is_staff',
            )
        }),
    )

    list_display = ('uuid', 'username', 'email', 'is_staff')
    list_display_links = ('uuid',)
    list_filter = ('date_joined',)
    search_fields = ('username', 'email')
    list_editable = ('username', 'email', 'is_staff')


admin.site.register(CustomUser, CustomUserAdmin)
