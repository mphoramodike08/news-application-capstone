"""Forms and role-group helpers for the news application."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import Article, CustomUser, Newsletter, Publisher


ROLE_GROUP_MAP = {
    "reader": "Reader",
    "journalist": "Journalist",
    "editor": "Editor",
}


def ensure_role_groups() -> None:
    """Create the default role groups and keep their permissions aligned."""
    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)
    permissions = {
        "view_article": Permission.objects.get(
            content_type=article_ct, codename="view_article"
        ),
        "add_article": Permission.objects.get(
            content_type=article_ct, codename="add_article"
        ),
        "change_article": Permission.objects.get(
            content_type=article_ct, codename="change_article"
        ),
        "delete_article": Permission.objects.get(
            content_type=article_ct, codename="delete_article"
        ),
        "view_newsletter": Permission.objects.get(
            content_type=newsletter_ct, codename="view_newsletter"
        ),
        "add_newsletter": Permission.objects.get(
            content_type=newsletter_ct, codename="add_newsletter"
        ),
        "change_newsletter": Permission.objects.get(
            content_type=newsletter_ct, codename="change_newsletter"
        ),
        "delete_newsletter": Permission.objects.get(
            content_type=newsletter_ct, codename="delete_newsletter"
        ),
    }

    reader_group, _ = Group.objects.get_or_create(name="Reader")
    reader_group.permissions.set(
        [permissions["view_article"], permissions["view_newsletter"]]
    )

    journalist_group, _ = Group.objects.get_or_create(name="Journalist")
    journalist_group.permissions.set(
        [
            permissions["view_article"],
            permissions["add_article"],
            permissions["change_article"],
            permissions["delete_article"],
            permissions["view_newsletter"],
            permissions["add_newsletter"],
            permissions["change_newsletter"],
            permissions["delete_newsletter"],
        ]
    )

    editor_group, _ = Group.objects.get_or_create(name="Editor")
    editor_group.permissions.set(
        [
            permissions["view_article"],
            permissions["change_article"],
            permissions["delete_article"],
            permissions["view_newsletter"],
            permissions["change_newsletter"],
            permissions["delete_newsletter"],
        ]
    )


class RegistrationForm(UserCreationForm):
    """Registration form that assigns the new user to the correct role group."""

    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "password1", "password2"]

    def clean_email(self):
        """Reject duplicate e-mail addresses during registration."""
        email = self.cleaned_data["email"].lower().strip()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this e-mail address already exists.")
        return email

    def save(self, commit=True):
        """Persist the user and synchronise their Django group membership."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            ensure_role_groups()
            user.groups.clear()
            user.groups.add(Group.objects.get(name=ROLE_GROUP_MAP[user.role]))
        return user


class ArticleForm(forms.ModelForm):
    """Form used by journalists and editors to create and edit article submissions."""

    class Meta:
        model = Article
        fields = ["title", "content", "publisher"]

    def __init__(self, *args, **kwargs):
        """Limit publisher choices to memberships for journalists."""
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["publisher"].required = False
        self.fields["publisher"].empty_label = "Independent article"
        if user and user.role == "journalist":
            self.fields["publisher"].queryset = user.publisher_memberships.all()


class PublisherForm(forms.ModelForm):
    """Form for editor-managed publisher records."""

    class Meta:
        model = Publisher
        fields = ["name", "description", "editors", "journalists"]

    def __init__(self, *args, **kwargs):
        """Limit relationship fields to users who match the required roles."""
        super().__init__(*args, **kwargs)
        self.fields["editors"].queryset = CustomUser.objects.filter(role="editor")
        self.fields["journalists"].queryset = CustomUser.objects.filter(
            role="journalist"
        )


class NewsletterForm(forms.ModelForm):
    """Form used to create or edit newsletters with role-aware article choices."""

    class Meta:
        model = Newsletter
        fields = ["title", "description", "publisher", "articles"]

    def __init__(self, *args, **kwargs):
        """Show only relevant articles for the active user in the selector."""
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["publisher"].required = False
        self.fields["publisher"].empty_label = "Independent newsletter"
        if user is not None:
            article_queryset = Article.objects.filter(author=user, approved=True)
            if user.role == "editor":
                article_queryset = Article.objects.filter(approved=True)
            self.fields["articles"].queryset = article_queryset
            if user.role == "journalist":
                self.fields["publisher"].queryset = user.publisher_memberships.all()
