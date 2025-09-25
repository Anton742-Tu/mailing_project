from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    """Форма для создания и редактирования клиента"""

    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.com',
                'required': True
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович',
                'required': True
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Дополнительная информация о клиенте...',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'email': 'Email адрес',
            'full_name': 'Ф.И.О.',
            'comment': 'Комментарий',
            'is_active': 'Активный клиент'
        }
        help_texts = {
            'email': 'Уникальный email адрес клиента',
            'is_active': 'Снимите отметку для временного отключения клиента'
        }

    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get('email')
        if email:
            # При редактировании исключаем текущий объект из проверки
            if self.instance.pk:
                if Client.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Клиент с таким email уже существует')
            else:
                if Client.objects.filter(email=email).exists():
                    raise forms.ValidationError('Клиент с таким email уже существует')
        return email
