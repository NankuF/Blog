from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    """
    Form – позволяет создавать стандартные формы.
    ModelForm – дает возможность создавать формы по объектам моделей.
    Валидация определяется типом поля. Например EmailField - только корректные e-mail адреса.
    required=False - поле comments стало необязательным.
    widget=forms.Textarea - изначально CharField отображается в HTML как <input type="text">, заменил его на textarea.

    Для каждой формы нужна своя вьюха.
    """
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
