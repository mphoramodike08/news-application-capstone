# Generated manually to align the project models with the rubric and review feedback.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("newsapp", "0002_customuser_subscribed_journalists_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(max_length=254, unique=True, verbose_name="email address"),
        ),
        migrations.AlterField(
            model_name="publisher",
            name="name",
            field=models.CharField(max_length=150, unique=True),
        ),
        migrations.AlterField(
            model_name="article",
            name="publisher",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="articles",
                to="newsapp.publisher",
            ),
        ),
        migrations.RenameField(
            model_name="newsletter",
            old_name="content",
            new_name="description",
        ),
        migrations.RenameField(
            model_name="newsletter",
            old_name="created_by",
            new_name="author",
        ),
        migrations.AlterField(
            model_name="newsletter",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="newsletters",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="newsletter",
            name="publisher",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="newsletters",
                to="newsapp.publisher",
            ),
        ),
    ]
