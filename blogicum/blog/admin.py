# Ключевые особенности админ.панели:
# 1. Регистрация всех моделей в админке с настройкой отображения
# 2. Оптимизация через list_editable и list_filter
# 3. После автотестов: подсчет комментариев, расширенные поля

from django.contrib import admin
from .models import Category, Location, Post, Comment

class LocationAdmin(admin.ModelAdmin):
    """Быстрое управление публикацией локаций"""
    list_display = (
        "name",
        "is_published",
        "created_at",
    )
    list_editable = ("is_published",)

class CategoryAdmin(admin.ModelAdmin):
    """Управление категориями с проверкой slug"""
    list_display = (
        "title",
        "description",
        "slug",
        "is_published",
        "created_at",
    )
    list_editable = ("is_published",)

class PostAdmin(admin.ModelAdmin):
    """Полная информация о постах с фильтрацией"""
    list_display = (
        "title",
        "author",
        "category",
        "location",
        "is_published",
        "pub_date",
        "comment_count",
    )
    list_editable = ("is_published",)
    list_filter = (
        "category",
        "location",
    )

    @admin.display(description="Комментариев")
    def comment_count(self, post):
        """Оптимизированный подсчет комментариев через related_name"""
        return post.comments.count()

admin.site.register(Post, PostAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment)
