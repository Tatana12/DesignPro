import os
import re
from django import forms
from django.core.exceptions import ValidationError
from .models import User, Application


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

class ApplicationCreateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description', 'category', 'plan_image']
        labels = {
            'title': 'Название заявки',
            'description': 'Описание',
            'category': 'Категория',
            'plan_image': 'Фото помещения или его план (jpg, jpeg, png, bmp, до 2 МБ)',
        }
        error_messages = {
            'title': {'required': 'Введите название заявки.'},
            'description': {'required': 'Введите описание заявки.'},
            'category': {'required': 'Выберите категорию.'},
            'plan_image': {'required': 'Загрузите фото помещения или план.'},
        }

    def clean_plan_image(self):
        image = self.cleaned_data.get('plan_image')
        if image:
            # Проверка расширения файла
            ext = os.path.splitext(image.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            if ext not in valid_extensions:
                raise ValidationError('Недопустимый формат файла. Разрешены только: jpg, jpeg, png, bmp.')

            # Проверка размера файла (не более 2 МБ)
            max_size = 2 * 1024 * 1024
            if image.size > max_size:
                raise ValidationError('Размер файла не должен превышать 2 МБ.')

        return image

class ChangeStatusForm(forms.Form):
    STATUS_CHOICES = [
        ('in_progress', 'Принято в работу'),
        ('completed', 'Выполнено'),
    ]

    status = forms.ChoiceField(
        label='Новый статус',
        choices=STATUS_CHOICES,
        required=True
    )
    comment = forms.CharField(
        label='Комментарий (обязателен при статусе «Принято в работу»)',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    design_image = forms.ImageField(
        label='Изображение дизайна (обязательно при статусе «Выполнено»)',
        required=False
    )

    def clean_design_image(self):
        image = self.cleaned_data.get('design_image')
        if image:
            ext = os.path.splitext(image.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            if ext not in valid_extensions:
                raise ValidationError('Недопустимый формат файла. Разрешены только: jpg, jpeg, png, bmp.')

            max_size = 2 * 1024 * 1024
            if image.size > max_size:
                raise ValidationError('Размер файла не должен превышать 2 МБ.')
        return image

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        comment = cleaned_data.get('comment', '').strip()
        design_image = cleaned_data.get('design_image')

        if status == 'in_progress' and not comment:
            self.add_error('comment', 'Укажите комментарий при переводе заявки в работу.')

        if status == 'completed' and not design_image:
            self.add_error('design_image', 'Прикрепите изображение готового дизайна.')

        return cleaned_data
