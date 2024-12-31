# Ключевые особенности форм:
# 1. Управление публикацией через is_published и pub_date
# 2. Обработка изображений и дат
# 3. После автотестов: exclude вместо fields

from django import forms
from django.utils import timezone
from .models import Comment, Post

class CreatePostForm(forms.ModelForm):
    """Форма создания поста с предустановкой текущей даты"""
    pub_date = forms.DateTimeField(
        initial=timezone.now,
        required=True,
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
            },
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = Post
        fields = (
            "title",
            "image",
            "text",
            "pub_date",
            "location",
            "category",
            "is_published",
        )


class CreateCommentForm(forms.ModelForm):
    """Простая форма комментария только с текстовым полем"""
    class Meta:
        model = Comment
        fields = ("text",)
