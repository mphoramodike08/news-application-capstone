"""Views for the news application web interface and REST API."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .forms import ArticleForm, NewsletterForm, PublisherForm, RegistrationForm
from .models import Article, CustomUser, Newsletter, Publisher
from .permissions import ArticlePermission
from .serializers import ArticleSerializer, NewsletterSerializer, PublisherSerializer
from .services import notify_article_approved


def role_required(*roles):
    """Restrict a view to authenticated users with one of the allowed roles."""

    def decorator(view_func):
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if request.user.role not in roles:
                return HttpResponseForbidden(
                    "You do not have permission to access this page."
                )
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


def home(request):
    """Show approved public content on the landing page."""
    articles = Article.objects.filter(approved=True).select_related(
        "author", "publisher"
    )
    newsletters = Newsletter.objects.select_related(
        "author", "publisher"
    ).prefetch_related("articles")
    return render(
        request,
        "newsapp/home.html",
        {"articles": articles, "newsletters": newsletters},
    )


def register(request):
    """Register a new user and send them to the login page."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Account created successfully for {user.username}. Please log in.",
            )
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "newsapp/register.html", {"form": form})


@login_required
def dashboard(request):
    """Render role-specific dashboard content."""
    user = request.user

    if user.role == "editor":
        user_articles = Article.objects.all().select_related("author", "publisher")
        user_newsletters = Newsletter.objects.all().select_related(
            "author", "publisher"
        )
    elif user.role == "reader":
        subscribed_publishers = user.subscribed_publishers.all()
        subscribed_journalists = user.subscribed_journalists.all()

        user_articles = (
            Article.objects.filter(approved=True)
            .filter(
                Q(publisher__in=subscribed_publishers)
                | Q(author__in=subscribed_journalists)
            )
            .select_related("author", "publisher")
            .distinct()
        )

        user_newsletters = (
            Newsletter.objects.filter(
                Q(publisher__in=subscribed_publishers)
                | Q(author__in=subscribed_journalists)
            )
            .select_related("author", "publisher")
            .distinct()
        )
    else:
        user_articles = Article.objects.filter(author=user).select_related("publisher")
        user_newsletters = Newsletter.objects.filter(author=user).select_related(
            "publisher"
        )

    publishers = Publisher.objects.all()
    journalists = CustomUser.objects.filter(role="journalist")
    return render(
        request,
        "newsapp/dashboard.html",
        {
            "user_articles": user_articles,
            "user_newsletters": user_newsletters,
            "publishers": publishers,
            "journalists": journalists,
        },
    )


@role_required("journalist")
def article_create(request):
    """Allow journalists to create articles."""
    if request.method == "POST":
        form = ArticleForm(request.POST, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "Article created.")
            return redirect("dashboard")
    else:
        form = ArticleForm(user=request.user)

    return render(
        request,
        "newsapp/article_form.html",
        {"form": form, "title": "Create Article"},
    )


@role_required("journalist", "editor")
def article_update(request, pk):
    """Allow journalists to edit their own articles and editors to edit all."""
    article = get_object_or_404(Article, pk=pk)
    if request.user.role == "journalist" and article.author != request.user:
        return HttpResponseForbidden(
            "You do not have permission to edit this article."
        )

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article, user=request.user)
        if form.is_valid():
            updated_article = form.save(commit=False)
            if request.user.role != "editor":
                updated_article.approved = article.approved
                updated_article.approved_at = article.approved_at
            updated_article.save()
            messages.success(request, "Article updated.")
            return redirect("dashboard")
    else:
        form = ArticleForm(instance=article, user=request.user)
    return render(
        request,
        "newsapp/article_form.html",
        {"form": form, "title": "Edit Article"},
    )


@role_required("journalist", "editor")
def article_delete(request, pk):
    """Allow journalists to delete their own articles and editors to delete all."""
    article = get_object_or_404(Article, pk=pk)
    if request.user.role == "journalist" and article.author != request.user:
        return HttpResponseForbidden(
            "You do not have permission to delete this article."
        )
    if request.method == "POST":
        article.delete()
        messages.success(request, "Article deleted.")
        return redirect("dashboard")
    return render(
        request,
        "newsapp/confirm_delete.html",
        {"object": article, "type": "article"},
    )


@role_required("editor")
def article_approve(request, pk):
    """Approve a pending article and trigger the notification workflow."""
    article = get_object_or_404(Article, pk=pk)
    article.approved = True
    article.approved_at = timezone.now()
    article.save(update_fields=["approved", "approved_at"])
    notify_article_approved(article)
    messages.success(request, "Article approved.")
    return redirect("dashboard")


@role_required("editor")
def publisher_create(request):
    """Allow editors to create publishers and manage assigned teams."""
    if request.method == "POST":
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save()
            publisher.editors.add(request.user)
            messages.success(request, "Publisher created.")
            return redirect("dashboard")
    else:
        form = PublisherForm(initial={"editors": [request.user.id]})
    return render(
        request,
        "newsapp/publisher_form.html",
        {"form": form, "title": "Create Publisher"},
    )


@role_required("editor")
def publisher_update(request, pk):
    """Allow editors to update publisher team assignments."""
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.method == "POST":
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            updated_publisher = form.save()
            updated_publisher.editors.add(request.user)
            messages.success(request, "Publisher updated.")
            return redirect("dashboard")
    else:
        form = PublisherForm(instance=publisher)
    return render(
        request,
        "newsapp/publisher_form.html",
        {"form": form, "title": "Edit Publisher"},
    )


@role_required("journalist", "editor")
def newsletter_create(request):
    """Allow journalists and editors to create newsletters."""
    if request.method == "POST":
        form = NewsletterForm(request.POST, user=request.user)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            form.save_m2m()
            messages.success(request, "Newsletter created.")
            return redirect("dashboard")
    else:
        form = NewsletterForm(user=request.user)
    return render(
        request,
        "newsapp/newsletter_form.html",
        {"form": form, "title": "Create Newsletter"},
    )


@role_required("journalist", "editor")
def newsletter_update(request, pk):
    """Allow journalists to edit their own newsletters and editors to edit all."""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.user.role == "journalist" and newsletter.author != request.user:
        return HttpResponseForbidden(
            "You do not have permission to edit this newsletter."
        )
    if request.method == "POST":
        form = NewsletterForm(request.POST, instance=newsletter, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Newsletter updated.")
            return redirect("dashboard")
    else:
        form = NewsletterForm(instance=newsletter, user=request.user)
    return render(
        request,
        "newsapp/newsletter_form.html",
        {"form": form, "title": "Edit Newsletter"},
    )


@role_required("journalist", "editor")
def newsletter_delete(request, pk):
    """Allow journalists to delete their own newsletters and editors to delete all."""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.user.role == "journalist" and newsletter.author != request.user:
        return HttpResponseForbidden(
            "You do not have permission to delete this newsletter."
        )
    if request.method == "POST":
        newsletter.delete()
        messages.success(request, "Newsletter deleted.")
        return redirect("dashboard")
    return render(
        request,
        "newsapp/confirm_delete.html",
        {"object": newsletter, "type": "newsletter"},
    )


@role_required("reader")
def toggle_publisher_subscription(request, pk):
    """Subscribe or unsubscribe a reader from a publisher."""
    publisher = get_object_or_404(Publisher, pk=pk)
    if publisher in request.user.subscribed_publishers.all():
        request.user.subscribed_publishers.remove(publisher)
        messages.success(request, f"Unsubscribed from {publisher.name}.")
    else:
        request.user.subscribed_publishers.add(publisher)
        messages.success(request, f"Subscribed to {publisher.name}.")
    return redirect("dashboard")


@role_required("reader")
def toggle_journalist_subscription(request, pk):
    """Subscribe or unsubscribe a reader from a journalist."""
    journalist = get_object_or_404(CustomUser, pk=pk, role="journalist")
    if journalist in request.user.subscribed_journalists.all():
        request.user.subscribed_journalists.remove(journalist)
        messages.success(request, f"Unsubscribed from {journalist.username}.")
    else:
        request.user.subscribed_journalists.add(journalist)
        messages.success(request, f"Subscribed to {journalist.username}.")
    return redirect("dashboard")


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    """List approved articles or allow journalists to create articles."""

    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]

    def get_queryset(self):
        if self.request.method == "GET":
            return Article.objects.filter(approved=True).select_related(
                "author", "publisher"
            )
        return Article.objects.all().select_related("author", "publisher")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single article."""

    queryset = Article.objects.all().select_related("author", "publisher")
    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]

    def perform_update(self, serializer):
        article = self.get_object()
        approved = serializer.validated_data.get("approved", article.approved)
        approved_at = article.approved_at

        if approved and not article.approved:
            approved_at = timezone.now()

        updated_article = serializer.save(approved_at=approved_at)

        if approved and not article.approved:
            notify_article_approved(updated_article)


class NewsletterPermission(permissions.BasePermission):
    """Restrict newsletter creation to journalists and editors."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ["journalist", "editor"]
        )


class PublisherPermission(permissions.BasePermission):
    """Restrict publisher writes to editors."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user and request.user.is_authenticated and request.user.role == "editor"
        )


class NewsletterListCreateAPIView(generics.ListCreateAPIView):
    """List newsletters and allow editors or journalists to create them."""

    queryset = Newsletter.objects.all().select_related(
        "author", "publisher"
    ).prefetch_related("articles")
    serializer_class = NewsletterSerializer
    permission_classes = [NewsletterPermission]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PublisherListCreateAPIView(generics.ListCreateAPIView):
    """List publishers and allow only editors to create them."""

    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [PublisherPermission]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subscribed_articles(request):
    """Return approved articles from the reader's subscribed publishers and journalists."""
    articles = Article.objects.filter(approved=True).filter(
        Q(publisher__in=request.user.subscribed_publishers.all())
        | Q(author__in=request.user.subscribed_journalists.all())
    )
    articles = articles.distinct().select_related("author", "publisher")
    return Response(ArticleSerializer(articles, many=True).data)


@api_view(["POST"])
def approved_article_callback(request):
    """Receive the internal callback that logs approved article payloads."""
    return Response(
        {"message": "Approved article callback received", "payload": request.data},
        status=status.HTTP_201_CREATED,
    )
