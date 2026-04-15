"""Service helpers for notifications and internal API callbacks."""

import requests
from django.conf import settings
from django.core.mail import send_mail


def notify_article_approved(article):
    """Notify subscribers by email and log the approval to the internal API."""
    publisher_emails = []
    journalist_emails = []

    if article.publisher_id:
        publisher_emails = list(
            article.publisher.subscribers.values_list("email", flat=True)
        )

    journalist_emails = list(
        article.author.journalist_followers.values_list("email", flat=True)
    )

    recipient_list = [email for email in set(publisher_emails + journalist_emails) if email]

    if recipient_list:
        send_mail(
            subject=f"Approved article: {article.title}",
            message=article.content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=True,
        )

    payload = {
        "article_id": article.id,
        "title": article.title,
        "publisher": article.publisher.name if article.publisher else "Independent",
        "author": article.author.username,
        "approved": True,
    }

    try:
        requests.post(settings.APPROVED_ARTICLE_CALLBACK_URL, json=payload, timeout=5)
    except requests.RequestException:
        pass
