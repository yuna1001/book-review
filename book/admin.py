from django.contrib import admin
from book.models import Book, Comment, Favorite, Wanted


admin.site.register(Book)
admin.site.register(Comment)
admin.site.register(Favorite)
admin.site.register(Wanted)
