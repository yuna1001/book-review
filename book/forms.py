from django import forms
from book.models import Comment


class BookSearchForm(forms.Form):
    book_name = forms.CharField(label='書籍名', required=True, max_length=255)


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('title', 'score', 'content',)
