from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Электронная почта *',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.ru',
            'autocomplete': 'email'
        }),
        error_messages={
            'required': 'Пожалуйста, введите email',
            'invalid': 'Введите корректный email'
        }
    )

    username = forms.CharField(
        max_length=30,
        required=True,
        label='Логин *',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Придумайте логин',
            'autocomplete': 'username'
        }),
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_]{3,30}$',
                message='Логин должен содержать от 3 до 30 символов (буквы, цифры, подчеркивание)'
            )
        ],
        error_messages={
            'required': 'Пожалуйста, придумайте логин',
            'max_length': 'Логин не может быть длиннее 30 символов'
        }
    )

    first_name = forms.CharField(
        max_length=30,
        required=False,
        label='Имя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя',
            'autocomplete': 'given-name'
        })
    )

    last_name = forms.CharField(
        max_length=30,
        required=False,
        label='Фамилия',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваша фамилия',
            'autocomplete': 'family-name'
        })
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 123-45-67',
            'autocomplete': 'tel'
        }),
        validators=[
            RegexValidator(
                regex='^[0-9+\-()\s]{7,30}$',
                message='Номер телефона должен содержать от 7 до 30 цифр и символов +()- и пробелов'
            )
        ]
    )

    password1 = forms.CharField(
        label='Пароль *',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Придумайте надежный пароль',
            'autocomplete': 'new-password'
        }),
        error_messages={
            'required': 'Пожалуйста, придумайте пароль'
        }
    )

    password2 = forms.CharField(
        label='Подтверждение пароля *',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
            'autocomplete': 'new-password'
        }),
        error_messages={
            'required': 'Пожалуйста, подтвердите пароль'
        }
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем стандартные подсказки пароля Django
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

        # Добавляем обязательные поля звездочками в label
        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label}"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError('Пользователь с таким телефоном уже существует')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user