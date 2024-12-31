# Ключевые особенности моделей:
# 1. Правильные внешние ключи (CASCADE/SET_NULL)
# 2. Оптимизированные запросы через менеджеры
# 3. После автотестов: related_name, help_text

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class PostManager(models.Manager):
    """Менеджер для фильтрации опубликованных постов"""
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "category",
                "author",
                "location",
            )
            .filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )
            .order_by("-pub_date")
        )


class BaseModel(models.Model):
    """
    Абстрактная модель с общими полями публикации.
    Вынесена для избежания дублирования кода в Category и Post.
    """
    is_published = models.BooleanField(
        verbose_name="Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        verbose_name="Добавлено", auto_now_add=True, auto_now=False
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    """
    Модель категории с уникальным слагом для URL.
    Наследует поля публикации для возможности скрытия категорий.
    """
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL; разрешены символы "
            "латиницы, цифры, дефис и подчёркивание."
        ),
        unique=True,
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse(
            "blog:category_posts", kwargs={"category_slug": self.slug}
        )


class Location(BaseModel):
    """
    Модель локации может быть опциональной (null=True) в постах.
    Наследует поля публикации для возможности скрытия локаций.
    """
    name = models.CharField(max_length=256, verbose_name="Название места")

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self) -> str:
        return self.name


class Post(BaseModel):
    """
    Основная модель поста с двумя менеджерами:
    - objects для всех запросов
    - post_list для фильтрации опубликованных постов
    """
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        verbose_name="Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем — можно делать "
            "отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор публикации",
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        Location,
        verbose_name="Местоположение",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    image = models.ImageField("Изображение", blank=True, upload_to="img/")
    objects = models.Manager()
    post_list = PostManager()

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ("-pub_date",)
        default_related_name = "posts"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("blog:post_detail", kwargs={"pk": self.pk})


class Comment(models.Model):
    """
    Модель комментария с каскадным удалением при удалении поста/автора.
    Сортировка по времени создания для хронологического отображения.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name="Пост",
    )
    text = models.TextField(
        verbose_name="Текст комментария",
    )
    created_at = models.DateTimeField(
        verbose_name="Дата",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("created_at",)
        default_related_name = "comments"

    def __str__(self):
        return self.text
