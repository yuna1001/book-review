from django.contrib import admin

from .models import (Book, Comment, Favorite, Wanted)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 2


class BookAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
    list_display = ('uuid', 'title', 'price', 'created', 'modified')
    list_display_links = ('uuid',)
    list_filter = ['created']
    search_fields = ['title']
    list_editable = ['title', 'price']


class CommentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'title', 'score', 'content', 'created', 'modified')
    list_display_links = ('uuid',)
    list_filter = ['created', 'user__username', 'book__title']
    search_fields = ['title', 'content']
    list_editable = ['title', 'score', 'content']


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'user', 'book', 'created', 'modified')
    list_display_links = ('uuid',)
    list_filter = ('created', 'user__username', 'book__title')
    list_editable = ('user', 'book')


class WantedAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'user', 'book', 'created', 'modified')
    list_display_links = ('uuid',)
    list_filter = ('created', 'user__username', 'book__title')
    list_editable = ('user', 'book')


admin.site.register(Book, BookAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Wanted, WantedAdmin)
