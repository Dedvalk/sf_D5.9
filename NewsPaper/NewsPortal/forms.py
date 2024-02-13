from django import forms
from django.core.exceptions import ValidationError

from .models import Post, Author


class PostForm(forms.ModelForm):

    content = forms.CharField(min_length=20)
    class Meta:
       model = Post
       fields = [
           'title',
           'content',
           #'type',
           #'author',
           'categories'
       ]
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        # if content is not None and len(content) < 20:
        #     raise ValidationError({
        #         'content': 'Содержимое поста не может быть менее 20 символов.'
        #     })

        title = cleaned_data.get('title')
        if title == content:
            raise ValidationError({
                'content': 'Содержимое поста не должно быть идентичным его названию.'
            })

        return cleaned_data

