from django import forms
from book.models import Comment


class BookSearchForm(forms.Form):
    """
    書籍の検索を行うフォームクラス
    """
    book_name = forms.CharField(label='書籍名', required=True, max_length=255)


class CommentCreateForm(forms.ModelForm):
    """
    コメントの投稿を行うフォームクラス
    """
    class Meta:
        model = Comment
        fields = ('title', 'score', 'content',)
