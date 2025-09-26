from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClientForm, MessageForm
from .models import Client, Message


def client_list(request):
    clients = Client.objects.all().order_by("-created_at")
    context = {
        "clients": clients,
        "total_count": clients.count(),
        "active_count": Client.objects.filter(is_active=True).count(),
    }
    return render(request, "mailing/client_list.html", context)


def home_page(request):
    return render(request, "mailing/home.html")


@login_required
def message_list(request):
    """Список всех сообщений"""
    message_list = Message.objects.all().order_by('-created_at')

    # Поиск по теме или содержанию
    search_query = request.GET.get('search', '')
    if search_query:
        message_list = message_list.filter(
            models.Q(subject__icontains=search_query) |
            models.Q(body__icontains=search_query)
        )

    # Фильтр по активности
    is_active_filter = request.GET.get('is_active', '')
    if is_active_filter in ['true', 'false']:
        message_list = message_list.filter(is_active=(is_active_filter == 'true'))

    # Пагинация
    paginator = Paginator(message_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Вычисляем статистику
    total_count = message_list.count()
    active_count = Message.objects.filter(is_active=True).count()
    inactive_count = total_count - active_count  # ← Вычисляем здесь!

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'is_active_filter': is_active_filter,
        'total_count': total_count,
        'active_count': active_count,
        'inactive_count': inactive_count,  # ← Передаем готовое значение
    }
    return render(request, 'mailing/message_list.html', context)


@login_required
def message_create(request):
    """Создание нового сообщения"""
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save()
            messages.success(request, f'Сообщение "{message.subject}" успешно создано!')
            return redirect("mailing:message_list")
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
    message = get_object_or_404(Message, pk=pk)

    if request.method == "POST":
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            message = form.save()
            messages.success(
                request, f'Сообщение "{message.subject}" успешно обновлено!'
            )
            return redirect("mailing:message_list")
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
    message = get_object_or_404(Message, pk=pk)

    if request.method == "POST":
        message_subject = message.subject
        message.delete()
        messages.success(request, f'Сообщение "{message_subject}" успешно удалено!')
        return redirect("mailing:message_list")

    return render(request, "mailing/message_confirm_delete.html", {"message": message})


@login_required
def message_detail(request, pk):
    """Просмотр деталей сообщения"""
    message = get_object_or_404(Message, pk=pk)
    return render(request, "mailing/message_detail.html", {"message": message})
