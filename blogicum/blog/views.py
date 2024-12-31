# Ключевые особенности контроллеров:
# 1. Безопасность через LoginRequiredMixin и проверки авторства
# 2. Оптимизация запросов (select_related, prefetch_related)
# 3. После автотестов: миксины, проверки в dispatch/delete

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.db.models import Count
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CreateCommentForm, CreatePostForm
from .models import Category, Comment, Post, User
from .mixins import CommentEditMixin, PostsEditMixin, PostsQuerySetMixin

PAGINATED_BY = 10


class PostDeleteView(PostsEditMixin, LoginRequiredMixin, DeleteView):
    """Безопасное удаление с проверкой авторства"""
    success_url = reverse_lazy("blog:index")

    def delete(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        if self.request.user != post.author:
            return redirect("blog:index")

        return super().delete(request, *args, **kwargs)


class PostUpdateView(PostsEditMixin, LoginRequiredMixin, UpdateView):
    """Проверяет авторство в dispatch для предотвращения изменения чужих постов"""
    form_class = CreatePostForm

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        if self.request.user != post.author:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(PostsEditMixin, LoginRequiredMixin, CreateView):
    """Автоматически устанавливает текущего пользователя как автора"""
    form_class = CreatePostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            "blog:profile",
            kwargs={
                "username": self.request.user.username,
            },
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Привязывает комментарий к посту и автору через form_valid"""
    model = Comment
    form_class = CreateCommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["pk"])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.kwargs["pk"]})


class CommentDeleteView(CommentEditMixin, LoginRequiredMixin, DeleteView):
    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.kwargs["pk"]})

    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs["comment_pk"])
        if self.request.user != comment.author:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().delete(request, *args, **kwargs)


class CommentUpdateView(CommentEditMixin, LoginRequiredMixin, UpdateView):
    form_class = CreateCommentForm

    def dispatch(self, request, *args, **kwargs):
        if (
            self.request.user
            != Comment.objects.get(pk=self.kwargs["comment_pk"]).author
        ):
            return redirect("blog:post_detail", pk=self.kwargs["pk"])

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.kwargs["pk"]})


class AuthorProfileListView(PostsQuerySetMixin, ListView):
    """
    Различает отображение для автора и посетителей:
    автор видит все свои посты, посетители - только опубликованные
    """
    model = Post
    template_name = "blog/profile.html"
    paginate_by = PAGINATED_BY

    def get_queryset(self):
        if self.request.user.username == self.kwargs["username"]:
            return (
                self.request.user.posts.select_related(
                    "category",
                    "author",
                    "location",
                )
                .all()
                .annotate(comment_count=Count("comments"))
                .order_by('-pub_date')
            )

        return (
            super()
            .get_queryset()
            .filter(author__username=self.kwargs["username"])
            .annotate(comment_count=Count("comments"))
            .order_by('-pub_date')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(
            User, username=self.kwargs["username"]
        )
        return context


class BlogIndexListView(PostsQuerySetMixin, ListView):
    """Добавляет количество комментариев к каждому посту на главной"""
    model = Post
    template_name = "blog/index.html"
    context_object_name = "post_list"
    paginate_by = PAGINATED_BY

    def get_queryset(self):
        return super().get_queryset().annotate(comment_count=Count("comments"))


class BlogCategoryListView(PostsQuerySetMixin, ListView):
    """Проверяет публикацию категории через get_object_or_404"""
    model = Post
    template_name = "blog/category.html"
    context_object_name = "post_list"
    paginate_by = PAGINATED_BY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(category__slug=self.kwargs["category_slug"])
            .annotate(comment_count=Count("comments"))
        )


class PostDetailView(PostsQuerySetMixin, DetailView):
    """Оптимизирует загрузку комментариев через prefetch_related"""
    model = Post
    template_name = "blog/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CreateCommentForm()
        context["comments"] = (
            self.get_object().comments.prefetch_related("author").all()
        )
        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "comments",
            )
        )
