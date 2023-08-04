from django.core.serializers.json import DjangoJSONEncoder
from game.models import Question, Option, Category


class QuestionEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Question):
            data = {}
            data["categories"] = list(map(lambda cat: cat.name, obj.falls_under.all()))
            data["difficulty"] = obj.get_difficulty_display()
            data["question"] = obj.text
            data["correct_answer"] = obj.correct_option.text
            data["incorrect_answers"] = list(
                map(lambda option: option.text, obj.incorrect_options.all())
            )
            return data
        return super().default(obj)
