from django.core.serializers.json import DjangoJSONEncoder

from game.models import Question


class QuestionEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Question):
            data = {}
            data["categories"] = [cat.name for cat in obj.falls_under.all()]
            data["difficulty"] = obj.get_difficulty_display()
            data["question"] = obj.text
            data["correct_answer"] = obj.correct_option.text
            data["incorrect_answers"] = [
                option.text for option in obj.incorrect_options.all()
            ]
            return data
        return super().default(obj)
