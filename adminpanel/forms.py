from django.forms import ModelForm, Form
from game.models import Question, Option, Lifeline, Category


class QuestionForm(ModelForm):
    template_name = "adminpanel/formTemplates/question.html"

    class Meta:
        model = Question
        fields = [
            "who_added",
            "falls_under",
            "question_type",
            "difficulty",
            "text",
            "correct_option",
            "incorrect_options",
            "date_added",
        ]
        exclude = ["asked_to"]

class OptionForm(ModelForm):
    template_name = "adminpanel/formTemplates/option.html"

    class Meta:
        model = Option
        fields = [
            "text",
            "date_added",
        ]
        exclude = ["hits"]

class LifelineForm(ModelForm):
    template_name = "adminpanel/formTemplates/lifeline.html"

    class Meta:
        model = Lifeline
        fields = [
            "name",
            "date_created",
            "description",
        ]

class CategoryForm(ModelForm):
    template_name = "adminpanel/formTemplates/category.html"

    class Meta:
        model = Category
        fields = [
            "date_created",
            "name",
        ]