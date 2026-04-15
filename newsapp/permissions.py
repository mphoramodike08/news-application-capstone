"""Custom permission classes for REST API access control."""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class ArticlePermission(BasePermission):
    """Enforce the task's article permissions for readers, journalists, and editors."""

    def has_permission(self, request, view):
        """Allow public reads, but restrict mutations to authorised roles."""
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return request.user.role == "journalist"
        return request.user.role in ["journalist", "editor"]

    def has_object_permission(self, request, view, obj):
        """Allow editors full control and journalists control of their own articles."""
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == "editor":
            return True
        return request.user.role == "journalist" and obj.author_id == request.user.id
