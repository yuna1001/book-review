from django import forms


class BookSearchForm(forms.Form):
    book_name = forms.CharField(label='書籍名', required=True, max_length=255)
