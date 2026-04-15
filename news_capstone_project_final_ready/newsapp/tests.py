"""Automated tests for the news application web app and API."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .forms import RegistrationForm, ensure_role_groups
from .models import Article, Newsletter, Publisher

User = get_user_model()


class NewsAppTests(TestCase):
    """End-to-end tests covering the required capstone behaviour."""

    def setUp(self):
        ensure_role_groups()
        self.client = APIClient()
        self.reader = User.objects.create_user(
            username="reader1",
            password="pass12345",
            role="reader",
            email="reader@example.com",
        )
        self.journalist = User.objects.create_user(
            username="journalist1",
            password="pass12345",
            role="journalist",
            email="journalist@example.com",
        )
        self.editor = User.objects.create_user(
            username="editor1",
            password="pass12345",
            role="editor",
            email="editor@example.com",
        )

        self.publisher = Publisher.objects.create(
            name="Daily News", description="General publisher"
        )
        self.publisher.editors.add(self.editor)
        self.publisher.journalists.add(self.journalist)
        self.reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.journalist)

        self.article = Article.objects.create(
            title="Draft Story",
            content="Story content",
            author=self.journalist,
            publisher=self.publisher,
            approved=False,
        )
        self.independent_article = Article.objects.create(
            title="Independent Story",
            content="Independent body",
            author=self.journalist,
            approved=True,
        )
        self.approved_article = Article.objects.create(
            title="Approved Story",
            content="Approved body",
            author=self.journalist,
            publisher=self.publisher,
            approved=True,
        )
        self.newsletter = Newsletter.objects.create(
            title="Weekly Brief",
            description="Top stories",
            author=self.journalist,
            publisher=self.publisher,
        )
        self.newsletter.articles.add(self.approved_article, self.independent_article)

    def test_reader_can_list_approved_articles_only(self):
        response = self.client.get("/api/articles/")
        self.assertEqual(response.status_code, 200)
        titles = [item["title"] for item in response.json()]
        self.assertIn("Approved Story", titles)
        self.assertIn("Independent Story", titles)
        self.assertNotIn("Draft Story", titles)

    def test_journalist_can_create_article(self):
        self.client.force_authenticate(user=self.journalist)
        response = self.client.post(
            "/api/articles/",
            {"title": "New Story", "content": "Body", "publisher": self.publisher.id},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["author"]["username"], self.journalist.username)

    def test_journalist_can_create_independent_article(self):
        self.client.force_authenticate(user=self.journalist)
        response = self.client.post(
            "/api/articles/",
            {"title": "Solo Story", "content": "Body", "publisher": None},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()["publisher"])

    def test_reader_cannot_create_article(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.post(
            "/api/articles/",
            {"title": "Blocked", "content": "Body", "publisher": self.publisher.id},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_journalist_cannot_approve_article_via_api(self):
        self.client.force_authenticate(user=self.journalist)
        response = self.client.put(
            f"/api/articles/{self.article.id}/",
            {
                "title": self.article.title,
                "content": self.article.content,
                "publisher": self.publisher.id,
                "approved": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.article.refresh_from_db()
        self.assertFalse(self.article.approved)

    @patch("newsapp.views.notify_article_approved")
    def test_editor_can_update_approve_and_delete_article_via_api(self, mock_notify):
        self.client.force_authenticate(user=self.editor)
        update_response = self.client.put(
            f"/api/articles/{self.article.id}/",
            {
                "title": "Edited Story",
                "content": "Updated",
                "publisher": self.publisher.id,
                "approved": True,
            },
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.article.refresh_from_db()
        self.assertTrue(self.article.approved)
        self.assertIsNotNone(self.article.approved_at)
        mock_notify.assert_called_once()

        delete_response = self.client.delete(f"/api/articles/{self.article.id}/")
        self.assertEqual(delete_response.status_code, 204)

    def test_reader_gets_only_subscribed_content(self):
        other_publisher = Publisher.objects.create(name="Other", description="Other")
        other_journalist = User.objects.create_user(
            username="otherjournalist",
            password="pass12345",
            role="journalist",
            email="other@example.com",
        )
        Article.objects.create(
            title="Other Story",
            content="Other body",
            author=other_journalist,
            publisher=other_publisher,
            approved=True,
        )
        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/articles/subscribed/")
        self.assertEqual(response.status_code, 200)
        titles = [item["title"] for item in response.json()]
        self.assertIn("Approved Story", titles)
        self.assertIn("Independent Story", titles)
        self.assertNotIn("Other Story", titles)

    @patch("newsapp.views.notify_article_approved")
    def test_editor_can_approve_article_from_web_view(self, mock_notify):
        self.client.force_login(self.editor)
        response = self.client.get(f"/articles/{self.article.id}/approve/")
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertTrue(self.article.approved)
        mock_notify.assert_called_once()

    def test_newsletter_endpoint_lists_newsletters(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/newsletters/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["title"], "Weekly Brief")
        self.assertEqual(len(response.json()[0]["articles"]), 2)

    def test_editor_can_create_publisher_but_reader_cannot(self):
        self.client.force_authenticate(user=self.reader)
        denied = self.client.post(
            "/api/publishers/",
            {"name": "Reader Pub", "description": "x"},
            format="json",
        )
        self.assertEqual(denied.status_code, 403)

        self.client.force_authenticate(user=self.editor)
        allowed = self.client.post(
            "/api/publishers/",
            {"name": "Editor Pub", "description": "x"},
            format="json",
        )
        self.assertEqual(allowed.status_code, 201)

    def test_registration_form_rejects_duplicate_email(self):
        form = RegistrationForm(
            data={
                "username": "reader2",
                "email": "reader@example.com",
                "role": "reader",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
