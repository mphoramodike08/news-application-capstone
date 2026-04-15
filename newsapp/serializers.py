"""DRF serializers for the news application API."""

from rest_framework import serializers

from .models import Article, CustomUser, Newsletter, Publisher


class UserSerializer(serializers.ModelSerializer):
    """Expose safe user information to API clients."""

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role"]


class PublisherSerializer(serializers.ModelSerializer):
    """Serialize publisher records."""

    class Meta:
        model = Publisher
        fields = ["id", "name", "description"]


class NewsletterSerializer(serializers.ModelSerializer):
    """Serialize newsletters and their related article ids."""

    author = UserSerializer(read_only=True)
    articles = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Article.objects.filter(approved=True)
    )

    class Meta:
        model = Newsletter
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "author",
            "publisher",
            "articles",
        ]
        read_only_fields = ["created_at", "author"]


class ArticleSerializer(serializers.ModelSerializer):
    """Serialize articles for list, detail, and create/update API flows."""

    author = UserSerializer(read_only=True)
    publisher_name = serializers.CharField(source="publication_label", read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "publisher",
            "publisher_name",
            "created_at",
            "approved",
            "approved_at",
        ]
        read_only_fields = ["created_at", "approved_at", "author"]

    def validate(self, attrs):
        """Restrict article approval changes to editors only."""
        request = self.context.get("request")
        if not request:
            return attrs

        approved = attrs.get("approved")
        if approved and request.user.role != "editor":
            raise serializers.ValidationError(
                {"approved": "Only editors can approve articles."}
            )
        return attrs
