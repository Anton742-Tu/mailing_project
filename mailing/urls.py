from django.urls import path

from . import views

app_name = "mailing"

urlpatterns = [
    # Главная страница и клиенты
    path("", views.home_page, name="home"),
    path("clients/", views.client_list, name="client_list"),
    # Сообщения
    path('messages/', views.message_list, name='message_list'),
    path('messages/create/', views.message_create, name='message_create'),
    path('messages/edit/<int:pk>/', views.message_edit, name='message_edit'),
    path('messages/delete/<int:pk>/', views.message_delete, name='message_delete'),
    path('messages/detail/<int:pk>/', views.message_detail, name='message_detail'),
]
