from django import template

from book.models import Favorite, Wanted

register = template.Library()


@register.filter
def get_favorite_id(book, user):
    """
    書籍がお気に入りに含まれている場合に
    お気に入りのuuidを取得する。
    """
    favorite = Favorite.objects.get(user=user, book=book)
    return favorite.uuid


@register.filter
def get_wanted_id(book, user):
    """
    書籍が読みたいに含まれている場合に
    読みたいのuuidを取得する。
    """
    wanted = Wanted.objects.get(user=user, book=book)
    return wanted.uuid
