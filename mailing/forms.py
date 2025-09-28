from django import forms

from .models import Client, Mailing, Message


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
            raise forms.ValidationError("Тема письма должна содержать не менее 5 символов")
        return subject

    def clean_body(self):
        """Валидация тела письма"""
        body = self.cleaned_data.get("body")
        if len(body.strip()) < 10:
            raise forms.ValidationError("Тело письма должно содержать не менее 10 символов")
        return body


class MailingForm(forms.ModelForm):
    clients = forms.ModelMultipleChoiceField(
        queryset=Client.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Клиенты",
    )

    class Meta:
        model = Mailing
        fields = [
            "title",
            "message",
            "clients",
            "start_time",
            "end_time",
            "period",
            "is_active",
        ]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["message"].queryset = Message.objects.filter(owner=user)
            self.fields["clients"].queryset = Client.objects.filter(owner=user)
