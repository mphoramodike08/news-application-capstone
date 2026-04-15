from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", LoginView.as_view(template_name="newsapp/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("articles/new/", views.article_create, name="article_create"),
    path("articles/<int:pk>/edit/", views.article_update, name="article_update"),
    path("articles/<int:pk>/delete/", views.article_delete, name="article_delete"),
    path("articles/<int:pk>/approve/", views.article_approve, name="article_approve"),
    path("publishers/new/", views.publisher_create, name="publisher_create"),
    path("publishers/<int:pk>/edit/", views.publisher_update, name="publisher_update"),
    path("publishers/<int:pk>/toggle-subscription/", views.toggle_publisher_subscription, name="toggle_publisher_subscription"),
    path("journalists/<int:pk>/toggle-subscription/", views.toggle_journalist_subscription, name="toggle_journalist_subscription"),
    path("newsletters/new/", views.newsletter_create, name="newsletter_create"),
    path("newsletters/<int:pk>/edit/", views.newsletter_update, name="newsletter_update"),
    path("newsletters/<int:pk>/delete/", views.newsletter_delete, name="newsletter_delete"),
    path("api/articles/", views.ArticleListCreateAPIView.as_view(), name="api_articles"),
    path("api/articles/subscribed/", views.subscribed_articles, name="api_subscribed_articles"),
    path("api/articles/<int:pk>/", views.ArticleDetailAPIView.as_view(), name="api_article_detail"),
    path("api/newsletters/", views.NewsletterListCreateAPIView.as_view(), name="api_newsletters"),
    path("api/publishers/", views.PublisherListCreateAPIView.as_view(), name="api_publishers"),
    path("api/approved/", views.approved_article_callback, name="api_approved"),
]
