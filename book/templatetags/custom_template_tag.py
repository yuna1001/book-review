from django import template

from ..models import Favorite, Wanted

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


@register.simple_tag
def url_replace(request, field, value):
    """
    GETパラメータを一部置き換える
    """

    url_dict = request.GET.copy()
    url_dict[field] = value

    return url_dict.urlencode() 
