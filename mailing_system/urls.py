"""
URL configuration for mailing_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin, messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import include, path


# Функция для очистки кеша
def clear_cache_test(request):
    """Очистка кеша для тестирования"""
    if request.user.is_authenticated:
        cache_key = f"home_stats_{request.user.id}"
        cache.delete(cache_key)
        messages.success(request, "✅ Кеш очищен! Данные будут обновлены из базы.")
    return redirect("home")


urlpatterns = [
    # Админка
    path("admin/", admin.site.urls),
    # Приложение mailing
    path("", include("mailing.urls")),
    # Очистка кеша
    path("clear-cache/", clear_cache_test, name="clear_cache"),
    # Аутентификация
    path(
        "accounts/",
        include(
            [
                path(
                    "login/",
                    auth_views.LoginView.as_view(template_name="registration/login.html"),
                    name="login",
                ),
                path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
                path(
                    "password_reset/",
                    auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"),
                    name="password_reset",
                ),
                path(
                    "password_reset/done/",
                    auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
                    name="password_reset_done",
                ),
                path(
                    "reset/<uidb64>/<token>/",
                    auth_views.PasswordResetConfirmView.as_view(
                        template_name="registration/password_reset_confirm.html"
                    ),
                    name="password_reset_confirm",
                ),
                path(
                    "reset/done/",
                    auth_views.PasswordResetCompleteView.as_view(
                        template_name="registration/password_reset_complete.html"
                    ),
                    name="password_reset_complete",
                ),
            ]
        ),
    ),
]
