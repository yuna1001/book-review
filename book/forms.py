from django import forms

from .models import Comment


class BookSearchForm(forms.Form):
    """
    書籍の検索を行うフォームクラス
    """
    search_word = forms.CharField(label='書籍名', required=True, max_length=50)


class CommentCreateForm(forms.ModelForm):
    """
    コメントの投稿を行うフォームクラス
    """
    class Meta:
        model = Comment
        fields = ('title', 'score', 'content',)
