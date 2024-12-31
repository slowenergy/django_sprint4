# Настройка приложения:
# - Правильная регистрация в INSTALLED_APPS
# - Корректные имена для админки
# - Использование BigAutoField

from django.apps import AppConfig

class BlogConfig(AppConfig):
    """Основная конфигурация блога с русским именованием"""
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"
    verbose_name = "Блог"

# Конфигурация приложения:
# 1. Корректное наименование для админки
# 2. Правильная регистрация в INSTALLED_APPS
# 3. Настройка verbose_name для отображения

# ...rest of the apps.py code...
