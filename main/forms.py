import re
from django import forms
from django.core.exceptions import ValidationError
from .models import User


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        label='ФИО',
        max_length=255,
        required=True,
        error_messages={'required': 'Поле ФИО обязательно для заполнения.'}
    )
    username = forms.CharField(
        label='Логин',
        max_length=150,
        required=True,
        error_messages={'required': 'Поле Логин обязательно для заполнения.'}
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        error_messages={
            'required': 'Поле Email обязательно для заполнения.',
            'invalid': 'Введите корректный адрес электронной почты.'
        }
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        required=True,
        error_messages={'required': 'Поле Пароль обязательно для заполнения.'}
    )
    password_confirm = forms.CharField(
        label='Повтор пароля',
        widget=forms.PasswordInput,
        required=True,
        error_messages={'required': 'Повторите пароль.'}
    )
    agree = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        required=True,
        error_messages={'required': 'Необходимо дать согласие на обработку персональных данных.'}
    )

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if not re.match(r'^[А-Яа-яЁё\s\-]+$', full_name):
            raise ValidationError('ФИО должно содержать только кириллические буквы, пробелы и дефис.')
        return full_name

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not re.match(r'^[A-Za-z\-]+$', username):
            raise ValidationError('Логин должен содержать только латинские буквы и дефис.')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Введенные пароли не совпадают.')

        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        required=True,
        error_messages={'required': 'Введите логин.'}
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        required=True,
        error_messages={'required': 'Введите пароль.'}
    )
