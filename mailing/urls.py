from django.urls import path

from . import views

app_name = "mailing"

urlpatterns = [
    path("", views.home_page, name="home"),
    path('clients/', views.client_list, name='client_list'),
    path("clients/create/", views.client_create, name="client_create"),
    path("clients/edit/<int:pk>/", views.client_edit, name="client_edit"),
    path("clients/delete/<int:pk>/", views.client_delete, name="client_delete"),
    path(
        "clients/toggle-active/<int:pk>/",
        views.client_toggle_active,
        name="client_toggle_active",
    ),
]
