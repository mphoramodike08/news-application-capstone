"""Database models for the news application."""

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class CustomUser(AbstractUser):
    """Application user with a role and optional subscription relationships."""

    ROLE_CHOICES = [
        ("reader", "Reader"),
        ("journalist", "Journalist"),
        ("editor", "Editor"),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="reader")
    subscribed_journalists = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="journalist_followers"
    )

    def clean(self):
        """Keep reader-only subscriptions off non-reader accounts."""
        super().clean()
        if self.role != "reader" and self.pk:
            self.subscribed_journalists.clear()
            self.subscribed_publishers.clear()

    def save(self, *args, **kwargs):
        """Normalise e-mail addresses before saving."""
        if self.email:
            self.email = self.email.lower().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a readable label for admin and templates."""
        return self.username


class Publisher(models.Model):
    """Curated publication that can have editors, journalists, and subscribers."""

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    subscribers = models.ManyToManyField(
        CustomUser, blank=True, related_name="subscribed_publishers"
    )
    editors = models.ManyToManyField(
        CustomUser, blank=True, related_name="managed_publishers"
    )
    journalists = models.ManyToManyField(
        CustomUser, blank=True, related_name="publisher_memberships"
    )

    def __str__(self):
        """Return the publisher name in admin and templates."""
        return self.name


class Article(models.Model):
    """News article submitted by a journalist and approved by an editor."""

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="articles"
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="articles",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        """Ensure an article is independent or belongs to one publisher only."""
        super().clean()
        if self.author_id and self.author.role != "journalist":
            raise ValidationError("Only journalists can be article authors.")

    @property
    def publication_label(self):
        """Return a readable publication label for templates and serializers."""
        return self.publisher.name if self.publisher else "Independent"

    def __str__(self):
        """Return the article title in admin and templates."""
        return self.title


class Newsletter(models.Model):
    """Curated collection of articles authored by a journalist or editor."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="newsletters",
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="newsletters"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    articles = models.ManyToManyField("Article", blank=True, related_name="newsletters")

    def clean(self):
        """Keep newsletter ownership aligned to the allowed roles."""
        super().clean()
        if self.author_id and self.author.role not in ["journalist", "editor"]:
            raise ValidationError(
                "Only journalists and editors can create newsletters."
            )

    def __str__(self):
        """Return the newsletter title in admin and templates."""
        return self.title
