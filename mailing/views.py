from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Client
from .forms import ClientForm


@login_required
def client_list(request):
    """Список всех клиентов с пагинацией"""
    clients = Client.objects.all().order_by('-created_at')

    # Поиск по email или имени
    search_query = request.GET.get('search', '')
    if search_query:
        clients = clients.filter(
            models.Q(email__icontains=search_query) |
            models.Q(full_name__icontains=search_query)
        )

    # Фильтр по активности
    is_active_filter = request.GET.get('is_active', '')
    if is_active_filter in ['true', 'false']:
        clients = clients.filter(is_active=(is_active_filter == 'true'))

    # Пагинация
    paginator = Paginator(clients, 10)  # 10 клиентов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'is_active_filter': is_active_filter,
        'total_count': clients.count(),
        'active_count': Client.objects.filter(is_active=True).count(),
    }
    return render(request, 'mailing/client_list.html', context)


@login_required
def client_create(request):
    """Создание нового клиента"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Клиент "{client.full_name}" успешно создан!')
            return redirect('mailing:client_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ClientForm()

    return render(request, 'mailing/client_form.html', {
        'form': form,
        'title': 'Добавить клиента'
    })


@login_required
def client_edit(request, pk):
    """Редактирование клиента"""
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Данные клиента "{client.full_name}" обновлены!')
            return redirect('mailing:client_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ClientForm(instance=client)

    return render(request, 'mailing/client_form.html', {
        'form': form,
        'title': 'Редактировать клиента',
        'client': client
    })


@login_required
def client_delete(request, pk):
    """Удаление клиента"""
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        client_name = client.full_name
        client.delete()
        messages.success(request, f'Клиент "{client_name}" успешно удален!')
        return redirect('mailing:client_list')

    return render(request, 'mailing/client_confirm_delete.html', {
        'client': client
    })


@login_required
def client_toggle_active(request, pk):
    """Включение/выключение клиента"""
    if request.method == 'POST' and request.is_ajax():
        client = get_object_or_404(Client, pk=pk)
        client.is_active = not client.is_active
        client.save()

        return JsonResponse({
            'success': True,
            'is_active': client.is_active,
            'message': f'Клиент {"активирован" if client.is_active else "деактивирован"}'
        })

    return JsonResponse({'success': False}, status=400)
