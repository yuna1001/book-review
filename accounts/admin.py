from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Relation


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        ('User Infomation', {
            'fields': (
                'username', 'email', 'profile_pic', 'created', 'modified'
            ),
        },),
        ('Authorization', {
            'fields': (
                'is_staff',
            )
        }),
    )

    list_display = ('uuid', 'username', 'email', 'created', 'is_staff')
    list_display_links = ('uuid',)
    list_filter = ('created',)
    search_fields = ('username', 'email')
    list_editable = ('username', 'email', 'is_staff')


class RelationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created', 'modified')
    list_display_links = ('pk',)
    list_filter = ('user', 'followed', 'created')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Relation, RelationAdmin)
