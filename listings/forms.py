from django import forms
from .models import Search


class SearchForm(forms.ModelForm):
    class Meta:
        model = Search
        fields = ['title', 'url', 'category', 'brand', 'model']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Напр. Audi A4 2015'}),
            'url': forms.URLInput(attrs={'class': 'form-control-custom', 'placeholder': 'https://mobile.bg/...'}),
            'category': forms.Select(attrs={'class': 'form-control-custom'}),
            'brand': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Audi'}),
            'model': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'A4'}),
        }
        labels = {
            'title': 'Име на търсенето',
            'url': 'Линк от сайта (Mobile.bg / Dev.bg)',
            'category': 'Категория',
            'brand': 'Марка (за филтри)',
            'model': 'Модел (за филтри)',
        }