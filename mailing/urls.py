from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .views import (
    CustomLoginView,
    CustomLogoutView,
    HomeView,
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingListView,
    MailingUpdateView,
    client_create,
    client_delete,
    client_detail,
    client_edit,
    client_list,
    manager_dashboard,
    message_create,
    message_delete,
    message_detail,
    message_edit,
    message_list,
    send_mailing_now,
    statistics_view,
    toggle_mailing_active,
    toggle_user_active,
)

urlpatterns = [
    # Главная страница
    path("", HomeView.as_view(), name="home"),
    # Аутентификация
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    # Клиенты
    path("clients/", client_list, name="client_list"),
    path("clients/create/", client_create, name="client_create"),
    path("clients/<int:pk>/", client_detail, name="client_detail"),
    path("clients/<int:pk>/edit/", client_edit, name="client_edit"),
    path("clients/<int:pk>/delete/", client_delete, name="client_delete"),
    # Сообщения
    path('messages/', views.message_list, name='message_list'),
    path('messages/create/', views.message_create, name='message_create'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('messages/<int:pk>/edit/', views.message_edit, name='message_edit'),
    path('messages/<int:pk>/delete/', views.message_delete, name='message_delete'),
    # Рассылки
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailings/<int:pk>/send-now/", send_mailing_now, name="mailing_send_now"),
    # Статистика
    path("statistics/", statistics_view, name="statistics"),
    # URLs для менеджеров
    path("manager/", manager_dashboard, name="manager_dashboard"),
    path("manager/user/<int:user_id>/toggle/", toggle_user_active, name="toggle_user_active"),
    path("manager/mailing/<int:mailing_id>/toggle/", toggle_mailing_active, name="toggle_mailing_active"),
]
