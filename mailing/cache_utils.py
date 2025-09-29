from functools import wraps

from django.core.cache import cache
from django.utils.decorators import method_decorator


def cache_page(timeout=300):
    """
    Правильный декоратор для кеширования view функций
    Кеширует только данные контекста, а не весь response
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Генерируем ключ кеша
            user_id = request.user.id if request.user.is_authenticated else "anonymous"
            cache_key = f"view_{view_func.__name__}_{request.path}_{user_id}"

            # Пробуем получить данные контекста из кеша
            cached_context = cache.get(cache_key)
            if cached_context is not None:
                # Если есть закешированный контекст, используем его
                response = view_func(request, *args, **kwargs)
                if hasattr(response, "context_data"):
                    response.context_data.update(cached_context)
                return response

            # Если нет в кеше - выполняем view
            response = view_func(request, *args, **kwargs)

            # Сохраняем контекст в кеш (если это TemplateResponse)
            if hasattr(response, "context_data") and response.context_data:
                # Исключаем несериализуемые данные
                cacheable_context = {}
                for key, value in response.context_data.items():
                    try:
                        # Пробуем сериализовать для проверки
                        import pickle

                        pickle.dumps(value)
                        cacheable_context[key] = value
                    except (TypeError, pickle.PickleError):
                        # Пропускаем несериализуемые данные
                        continue

                cache.set(cache_key, cacheable_context, timeout)

            return response

        return _wrapped_view

    return decorator


def cache_context(timeout=300):
    """
    Декоратор для кеширования только контекста (без response)
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            cache_key = f"context_{view_func.__name__}_{request.path}_{request.user.id}"

            # Пробуем получить контекст из кеша
            cached_context = cache.get(cache_key)
            if cached_context is not None:
                # Возвращаем функцию с закешированным контекстом
                def response_with_cached_context():
                    response = view_func(request, *args, **kwargs)
                    if hasattr(response, "context_data"):
                        response.context_data.update(cached_context)
                    return response

                return response_with_cached_context()

            # Выполняем view и кешируем контекст
            response = view_func(request, *args, **kwargs)

            if hasattr(response, "context_data") and response.context_data:
                cache.set(cache_key, response.context_data, timeout)

            return response

        return _wrapped_view

    return decorator


# Упрощенные версии для методов моделей
def cache_model_method(timeout=300):
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            obj_id = getattr(self, "id", "no_id")
            cache_key = f"model_{self.__class__.__name__}_{method.__name__}_{obj_id}"

            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = method(self, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator


def get_cached_or_execute(key, func, timeout=300, *args, **kwargs):
    """Утилита: получает данные из кеша или выполняет функцию"""
    cached_data = cache.get(key)
    if cached_data is not None:
        return cached_data

    data = func(*args, **kwargs)
    cache.set(key, data, timeout)
    return data


def invalidate_user_cache(user_id):
    """
    Простая функция для инвалидации кеша пользователя
    """
    from django.core.cache import cache

    # Удаляем все ключи связанные с пользователем
    keys_to_delete = [
        f"user_stats_{user_id}",
        f"home_stats_{user_id}",
        f"view_statistics_{user_id}",
    ]

    for key in keys_to_delete:
        cache.delete(key)

    print(f"✅ Кеш пользователя {user_id} инвалидирован")


def invalidate_mailing_cache(mailing_id):
    """
    Простая функция для инвалидации кеша рассылки
    """
    from django.core.cache import cache

    keys_to_delete = [
        f"mailing_{mailing_id}",
        f"model_Mailing_get_success_count_{mailing_id}",
        f"model_Mailing_get_failed_count_{mailing_id}",
        f"model_Mailing_get_total_attempts_{mailing_id}",
    ]

    for key in keys_to_delete:
        cache.delete(key)

    print(f"✅ Кеш рассылки {mailing_id} инвалидирован")
