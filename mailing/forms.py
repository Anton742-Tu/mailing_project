from django import forms

from .models import Client, Message


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment", "is_active"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body", "is_active"]
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите тему письма...",
                    "required": True,
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите текст сообщения...",
                    "rows": 6,
                    "required": True,
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "subject": "Тема письма",
            "body": "Тело письма",
            "is_active": "Активное сообщение",
        }
        help_texts = {
            "subject": "Краткое описание содержания письма",
            "body": "Основное содержание сообщения",
            "is_active": "Снимите отметку для временного отключения сообщения",
        }

    def clean_subject(self):
        """Валидация темы письма"""
        subject = self.cleaned_data.get("subject")
        if len(subject.strip()) < 5:
            raise forms.ValidationError(
                "Тема письма должна содержать не менее 5 символов"
            )
        return subject

    def clean_body(self):
        """Валидация тела письма"""
        body = self.cleaned_data.get("body")
        if len(body.strip()) < 10:
            raise forms.ValidationError(
                "Тело письма должно содержать не менее 10 символов"
            )
        return body
