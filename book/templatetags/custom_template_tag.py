from django import template

from ..models import Favorite

register = template.Library()


@register.filter
def get_favorite_id(book, user):
    """
    書籍がお気に入りに含まれている場合に
    お気に入りのuuidを取得する。
    """
    favorite = Favorite.objects.get(user=user, book=book)
    return favorite.uuid


@register.simple_tag
def url_replace(request, field, value):
    """
    GETパラメータを一部置き換える
    """

    url_dict = request.GET.copy()
    url_dict[field] = value

    return url_dict.urlencode()
