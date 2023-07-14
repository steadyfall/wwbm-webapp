# Generated by Django 4.2.3 on 2023-07-14 09:42

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import game.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("name", models.CharField(max_length=81)),
            ],
            options={
                "verbose_name": "category",
                "verbose_name_plural": "categories",
            },
        ),
        migrations.CreateModel(
            name="ChosenOption",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_chosen",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
            ],
            options={
                "verbose_name": "chosen option",
                "verbose_name_plural": "chosen options",
            },
        ),
        migrations.CreateModel(
            name="Level",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "level_number",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(16),
                        ],
                        verbose_name="Level",
                    ),
                ),
                (
                    "money",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(10000000),
                        ],
                        verbose_name="Prize Money",
                    ),
                ),
            ],
            options={
                "verbose_name": "lifeline",
                "verbose_name_plural": "lifelines",
            },
        ),
        migrations.CreateModel(
            name="Option",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
                ("text", models.CharField(max_length=250)),
                (
                    "hits",
                    models.ManyToManyField(
                        related_name="users_clicked",
                        through="game.ChosenOption",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "option",
                "verbose_name_plural": "options",
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
                ("text", models.TextField(max_length=666)),
                (
                    "question_type",
                    models.CharField(
                        choices=[
                            ("MULTIPLE", "Multiple"),
                            ("TRUEFALSE", "True or False"),
                        ],
                        default="MULTIPLE",
                        max_length=20,
                    ),
                ),
                (
                    "difficulty",
                    models.CharField(
                        choices=[
                            ("UNASSIGNED", "Unassigned"),
                            ("EASY", "Easy"),
                            ("MEDIUM", "Medium"),
                            ("HARD", "Hard"),
                        ],
                        default="UNASSIGNED",
                        max_length=20,
                    ),
                ),
                (
                    "asked_to",
                    models.ManyToManyField(
                        related_name="questions_asked", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "correct_option",
                    models.ForeignKey(
                        default=game.models.Option.get_default_pk,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="questions_correct",
                        to="game.option",
                    ),
                ),
                (
                    "falls_under",
                    models.ManyToManyField(
                        related_name="all_questions", to="game.category"
                    ),
                ),
                (
                    "incorrect_options",
                    models.ManyToManyField(
                        related_name="related_questions", to="game.option"
                    ),
                ),
                (
                    "who_added",
                    models.ForeignKey(
                        default=game.models.get_sentinel_user,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="created_questions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "question",
                "verbose_name_plural": "questions",
            },
        ),
        migrations.CreateModel(
            name="QuestionOrder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_chosen",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="game.question"
                    ),
                ),
            ],
            options={
                "verbose_name": "ordering of question in session",
                "verbose_name_plural": "ordering of questions in session",
            },
        ),
        migrations.CreateModel(
            name="Session",
            fields=[
                (
                    "session_id",
                    models.CharField(
                        default="W8yII472",
                        editable=False,
                        max_length=8,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "score",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100000000),
                        ],
                        verbose_name="Money Won",
                    ),
                ),
                (
                    "correct_qns",
                    models.ManyToManyField(
                        related_name="sessions_correct_in", to="game.question"
                    ),
                ),
                (
                    "current_level",
                    models.ForeignKey(
                        default=game.models.Level.get_default_pk,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="sessions_currently",
                        to="game.level",
                    ),
                ),
                (
                    "current_question",
                    models.ForeignKey(
                        default=game.models.Question.get_default_pk,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="sessions_current_question_in",
                        to="game.question",
                    ),
                ),
                (
                    "lifeline_qns",
                    models.ManyToManyField(
                        related_name="sessions_used_lifeline_in", to="game.question"
                    ),
                ),
                (
                    "questions_asked",
                    models.ManyToManyField(
                        related_name="sessions_asked_in",
                        through="game.QuestionOrder",
                        to="game.question",
                    ),
                ),
                (
                    "session_user",
                    models.ForeignKey(
                        on_delete=models.SET(game.models.get_sentinel_user),
                        related_name="initiated_sessions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "wrong_qn",
                    models.ForeignKey(
                        default=game.models.Question.get_default_pk,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="sessions_wrong_in",
                        to="game.question",
                    ),
                ),
            ],
            options={
                "verbose_name": "session",
                "verbose_name_plural": "sessions",
            },
        ),
        migrations.AddField(
            model_name="questionorder",
            name="session",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="game.session"
            ),
        ),
        migrations.AddField(
            model_name="chosenoption",
            name="option",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="game.option"
            ),
        ),
        migrations.AddField(
            model_name="chosenoption",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
