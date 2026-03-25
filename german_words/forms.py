from django import forms


class SnippetForm(forms.Form):
    first_five = forms.CharField(
        label='Первые 5 слов отрывка',
        max_length=200
    )
    last_five = forms.CharField(
        label='Последние 5 слов отрывка',
        max_length=200
    )