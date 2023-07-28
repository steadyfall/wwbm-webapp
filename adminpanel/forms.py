from django.forms import ModelForm, Form
from game.models import Question, Session


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
