from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class OwnerRequiredMixin(LoginRequiredMixin):
    """Разрешает доступ только владельцу объекта"""

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для выполнения этого действия.")
        return redirect("home")


class OwnerOrManagerRequiredMixin(LoginRequiredMixin):
    """Разрешает доступ владельцу или менеджеру"""

    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        return obj.owner == user or user.groups.filter(name="Менеджер").exists()

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для выполнения этого действия.")
        return redirect("home")


class ManagerRequiredMixin(UserPassesTestMixin):
    """Разрешает доступ только менеджерам"""

    def test_func(self):
        return self.request.user.groups.filter(name="Менеджер").exists()

    def handle_no_permission(self):
        messages.error(self.request, "Эта страница доступна только менеджерам.")
        return redirect("home")
