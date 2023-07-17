from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from time import strftime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.contrib.auth import get_user_model


class Lifeline(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=81)
    description = models.TextField(max_length=1000, blank=False, null=False)

    class Meta:
        verbose_name = "lifeline"
        verbose_name_plural = "lifelines"

    def __str__(self):
        return self.name


class Level(models.Model):
    level_number = models.IntegerField(
        verbose_name="Level",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(16)],
    )
    money = models.IntegerField(
        verbose_name="Prize Money",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10_000_000)],
    )

    class Meta:
        verbose_name = "level"
        verbose_name_plural = "levels"

    @classmethod
    def get_default_pk(cls):
        level, created = cls.objects.get_or_create(level_number=0)
        return level.pk

    def print_money(self):
        return f"{self.money}"

    def __str__(self):
        return f"Level {self.level_number}"


class Category(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=81)

    @classmethod
    def get_default_pk(cls):
        category, created = cls.objects.get_or_create(name="None")
        return category.pk

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Option(models.Model):
    date_added = models.DateTimeField(default=timezone.now)
    text = models.CharField(max_length=250)
    hits = models.ManyToManyField(
        User, through="ChosenOption", related_name="users_clicked"
    )

    @classmethod
    def get_default_pk(cls):
        option, created = cls.objects.get_or_create(text="None")
        return option.pk

    class Meta:
        verbose_name = "option"
        verbose_name_plural = "options"

    def __str__(self):
        return self.text


class ChosenOption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    date_chosen = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "chosen option"
        verbose_name_plural = "chosen options"

    def __str__(self):
        produce = f'{self.user.__str__()} chose {self.option.__str__()} on {strftime("%d-%m-%Y %I:%M:%S %p", self.date_chosen)} UTC'
        return produce


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="deleted")[0].pk


class Question(models.Model):
    UNASSIGNED = "UNASSIGNED"
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    difficulty_choices = [
        (UNASSIGNED, UNASSIGNED.title()),
        (EASY, EASY.title()),
        (MEDIUM, MEDIUM.title()),
        (HARD, HARD.title()),
    ]

    MULTIPLE = "MULTIPLE"
    TRUE_FALSE = "TRUEFALSE"
    question_type_choices = [
        (MULTIPLE, MULTIPLE.title()),
        (TRUE_FALSE, "True or False"),
    ]

    who_added = models.ForeignKey(
        get_user_model(), default=get_sentinel_user, on_delete=models.SET_DEFAULT, related_name="created_questions", primary_key=False
    )
    date_added = models.DateTimeField(default=timezone.now)
    falls_under = models.ManyToManyField(Category, related_name="all_questions")
    text = models.TextField(max_length=666, blank=False, null=False)
    correct_option = models.ForeignKey(
        Option,
        default=Option.get_default_pk,
        on_delete=models.SET_DEFAULT,
        related_name="questions_correct",
    )
    incorrect_options = models.ManyToManyField(Option, related_name="related_questions")
    question_type = models.CharField(
        max_length=20, choices=question_type_choices, default=MULTIPLE
    )
    difficulty = models.CharField(
        max_length=20, choices=difficulty_choices, default=UNASSIGNED
    )
    asked_to = models.ManyToManyField(User, related_name="questions_asked")

    @classmethod
    def get_default_pk(cls):
        question, created = cls.objects.get_or_create(
            text="None",
            correct_option=Option.objects.get(pk=Option.get_default_pk()),
        )
        question.incorrect_options.set([Option.get_default_pk()]),
        return question.pk

    class Meta:
        verbose_name = "question"
        verbose_name_plural = "questions"

    def __str__(self):
        return f"{self.get_difficulty_display()} question under {', '.join([i.__str__() for i in self.falls_under.all()])}"


class Session(models.Model):
    session_id = models.CharField(
        primary_key=True, default=get_random_string(8), editable=False, max_length=8
    )
    date_created = models.DateTimeField(default=timezone.now)
    session_user = models.ForeignKey(
        get_user_model(), default=get_sentinel_user, on_delete=models.SET(get_sentinel_user), related_name="initiated_sessions"
    )
    current_level = models.ForeignKey(
        Level,
        default=Level.get_default_pk,
        on_delete=models.SET_DEFAULT,
        related_name="sessions_currently",
    )
    agreedToRules = models.BooleanField(verbose_name="Agreed to T&C", default=False)
    # Above will turn True if user agrees to terms and conditions given
    gameOver = models.BooleanField(verbose_name="Game over?", default=False)
    # Above will turn True if either user quits from the game or answers an question wrong
    score = models.IntegerField(
        verbose_name="Money Won",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100_000_000)],
    )
    current_question = models.ForeignKey(
        Question,
        default=Question.get_default_pk,
        on_delete=models.SET_DEFAULT,
        related_name="sessions_current_question_in",
    )
    questions_asked = models.ManyToManyField(
        Question, through="QuestionOrder", related_name="sessions_asked_in"
    )
    correct_qns = models.ManyToManyField(Question, related_name="sessions_correct_in")
    wrong_qn = models.ForeignKey(
        Question,
        default=Question.get_default_pk,
        on_delete=models.SET_DEFAULT,
        related_name="sessions_wrong_in",
    )
    lifeline_qns = models.ManyToManyField(
        Question, related_name="sessions_used_lifeline_in"
    )
    left_lifelines = models.ManyToManyField(Lifeline, related_name="sessions_unused")
    used_lifelines = models.ManyToManyField(Lifeline, related_name="sessions_used")

    """ def get_absolute_url(self):
        return reverse('session', kwargs={'session_id': self.session_id}) """

    @classmethod
    def get_unused_sessionId(cls):
        used_sessionId = {ssn.session_id for ssn in cls.objects.all()}
        newSessionId = get_random_string(8)
        while newSessionId in used_sessionId:
            newSessionId = get_random_string(8)
        return newSessionId

    class Meta:
        verbose_name = "session"
        verbose_name_plural = "sessions"

    def __str__(self):
        return f"{self.session_id}"


class QuestionOrder(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    date_chosen = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "ordering of question in session"
        verbose_name_plural = "ordering of questions in session"

    def __str__(self):
        produce = f'{self.session.session_id} - {self.question.__str__()} on {strftime("%d-%m-%Y %I:%M:%S %p", self.date_chosen)} UTC'
        return produce
