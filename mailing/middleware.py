from django.middleware.common import CommonMiddleware
from django.utils.cache import patch_cache_control


class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Добавляем заголовки кеширования для разных типов контента
        if hasattr(response, "headers"):
            path = request.path

            # Статические файлы - кешируем надолго
            if path.startswith("/static/") or path.startswith("/media/"):
                patch_cache_control(response, public=True, max_age=3600 * 24, immutable=True)  # 24 часа

            # HTML страницы - кешируем ненадолго
            elif response.get("Content-Type", "").startswith("text/html"):
                if not any(
                    [
                        path.startswith("/admin/"),
                        path.startswith("/login/"),
                        path.startswith("/manager/"),
                        request.user.is_authenticated,
                    ]
                ):
                    patch_cache_control(response, public=True, max_age=300, must_revalidate=True)  # 5 минут

        return response
