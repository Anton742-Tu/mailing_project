from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import ClientForm, MailingForm, MessageForm
from .models import Client, Mailing, MailingLog, Message
from .services import send_mailing


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # автоматический вход после регистрации
            return redirect('home')  # на главную страницу
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "mailing/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Статистика по заданию: рассылки, активные рассылки, уникальные клиенты
        context["total_mailings"] = Mailing.objects.filter(owner=user).count()
        context["active_mailings"] = Mailing.objects.filter(
            owner=user, status="launched"
        ).count()
        context["unique_clients"] = Client.objects.filter(owner=user).count()

        return context


# Views для клиентов
@login_required
def client_list(request):
    """Список всех клиентов"""
    clients = Client.objects.filter(owner=request.user).order_by("-created_at")

    # Поиск по email или имени
    search_query = request.GET.get("search", "")
    if search_query:
        clients = clients.filter(
            models.Q(email__icontains=search_query)
            | models.Q(full_name__icontains=search_query)
        )

    # Пагинация
    paginator = Paginator(clients, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "total_count": clients.count(),
        "active_count": Client.objects.filter(
            owner=request.user, is_active=True
        ).count(),
    }
    return render(request, "mailing/client_list.html", context)


@login_required
def client_create(request):
    """Создание нового клиента"""
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.owner = request.user
            client.save()
            print(f"Создан клиент: {client.email}, owner: {client.owner}")  # отладка
            messages.success(request, f'Клиент "{client.email}" успешно создан!')
            return redirect("client_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = ClientForm()

    return render(
        request,
        "mailing/client_form.html",
        {"form": form, "title": "Создать клиента"},
    )


@login_required
def client_edit(request, pk):
    """Редактирование клиента"""
    client = get_object_or_404(Client, pk=pk, owner=request.user)

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Клиент "{client.email}" успешно обновлен!')
            return redirect("client_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = ClientForm(instance=client)

    return render(
        request,
        "mailing/client_form.html",
        {"form": form, "title": "Редактировать клиента", "client": client},
    )


@login_required
def client_delete(request, pk):
    """Удаление клиента"""
    client = get_object_or_404(Client, pk=pk, owner=request.user)

    if request.method == "POST":
        client_email = client.email
        client.delete()
        messages.success(request, f'Клиент "{client_email}" успешно удален!')
        return redirect("client_list")

    return render(request, "mailing/client_confirm_delete.html", {"client": client})


@login_required
def client_detail(request, pk):
    """Просмотр деталей клиента"""
    client = get_object_or_404(Client, pk=pk, owner=request.user)
    return render(request, "mailing/client_detail.html", {"client": client})


# Views для сообщений
@login_required
def message_list(request):
    """Список всех сообщений"""
    # Сначала получаем базовый queryset
    message_list = Message.objects.all().order_by("-created_at")

    # Поиск по теме или содержанию
    search_query = request.GET.get("search", "")
    if search_query:
        message_list = message_list.filter(
            Q(subject__icontains=search_query)
            | Q(body__icontains=search_query)  # ← Используем Q вместо models.Q
        )

    # Фильтр по активности
    is_active_filter = request.GET.get("is_active", "")
    if is_active_filter == "true":
        message_list = message_list.filter(is_active=True)
    elif is_active_filter == "false":
        message_list = message_list.filter(is_active=False)

    # Пагинация
    paginator = Paginator(message_list, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Вычисляем статистику
    total_count = message_list.count()
    active_count = Message.objects.filter(is_active=True).count()
    inactive_count = total_count - active_count

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "is_active_filter": is_active_filter,
        "total_count": total_count,
        "active_count": active_count,
        "inactive_count": inactive_count,
    }
    return render(request, "mailing/message_list.html", context)


@login_required
def message_create(request):
    """Создание нового сообщения"""
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.owner = request.user
            message.save()
            messages.success(request, f'Сообщение "{message.subject}" успешно создано!')
            return redirect("message_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = MessageForm()

    return render(
        request,
        "mailing/message_form.html",
        {"form": form, "title": "Создать сообщение"},
    )


@login_required
def message_edit(request, pk):
    """Редактирование сообщения"""
    message = get_object_or_404(Message, pk=pk, owner=request.user)

    if request.method == "POST":
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            message = form.save()
            messages.success(
                request, f'Сообщение "{message.subject}" успешно обновлено!'
            )
            return redirect("message_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = MessageForm(instance=message)

    return render(
        request,
        "mailing/message_form.html",
        {"form": form, "title": "Редактировать сообщение", "message": message},
    )


@login_required
def message_delete(request, pk):
    """Удаление сообщения"""
    message = get_object_or_404(Message, pk=pk, owner=request.user)

    if request.method == "POST":
        message_subject = message.subject
        message.delete()
        messages.success(request, f'Сообщение "{message_subject}" успешно удалено!')
        return redirect("message_list")

    return render(request, "mailing/message_confirm_delete.html", {"message": message})


@login_required
def message_detail(request, pk):
    """Просмотр деталей сообщения"""
    message = get_object_or_404(Message, pk=pk, owner=request.user)
    return render(request, "mailing/message_detail.html", {"message": message})


# View для аутентификации и главной страницы
class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = "/"


# View для рассылок
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    context_object_name = "mailings"
    template_name = "mailing/mailing_list.html"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing_list")


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.object

        # Статистика по логам
        logs = MailingLog.objects.filter(mailing=mailing)
        success_count = logs.filter(status="success").count()
        failed_count = logs.filter(status="failed").count()
        total_count = mailing.clients.count()

        context["logs"] = logs
        context["success_count"] = success_count
        context["failed_count"] = failed_count
        context["total_count"] = total_count
        context["success_rate"] = (
            (success_count / total_count * 100) if total_count > 0 else 0
        )

        return context


@login_required
def send_mailing_now(request, pk):
    """Ручная отправка рассылки через обычный запрос"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

    try:
        success, message = send_mailing(mailing.id)
        if success:
            messages.success(request, f'Рассылка отправлена: {message}')
        else:
            messages.error(request, f'Ошибка отправки: {message}')
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')

    # Возвращаем на страницу рассылки
    return redirect('mailing_detail', pk=pk)
