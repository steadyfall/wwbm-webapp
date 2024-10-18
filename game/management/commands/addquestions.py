import json, logging
from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured
from game.models import Question, Option, Category
from django.utils import timezone
from django.contrib.auth import get_user_model


def configure_logger(enable_logging):
    logger = logging.getLogger(__name__)

    if enable_logging:
        logger.setLevel(logging.INFO)  # Set the default log level to INFO

        # Clear any previous handlers
        if logger.hasHandlers():
            logger.handlers.clear()

        # Set logging to console or file based on the argument
        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        logging.disable(logging.CRITICAL)  # Disable all logging

    return logger


class Command(BaseCommand):
    help = """
        Extract questions from a JSON file a JSON file generated via `manage.py fetchdb` command and adds them to the database.
        Ensure that `manage.py createcategories` and `manage.py extractoptions` commands have been run before running this command.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = None

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file", type=str, help="Path to the JSON file containing questions."
        )
        parser.add_argument(
            "--enable-logging", action="store_true", help="Enable logging completely."
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]
        enable_logging = options.get("enable_logging", False)

        # Configure logger based on argument
        self.logger = configure_logger(enable_logging)

        try:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise ImproperlyConfigured(f"File '{json_file}' not found.")
        except json.JSONDecodeError:
            raise ImproperlyConfigured(f"File '{json_file}' is not a valid JSON file.")

        user = get_user_model().objects.get(username="admin")
        questions_to_create = []
        category_mapping = {}

        for item in data:
            """
            keys of every object: [
                'type', 'difficulty', 'category',
                'question', 'correct_answer', 'incorrect_answers'
            ]
            """
            item["category"] = item["category"].replace("&amp;", "&")

            self.logger.info(
                f"who_added={user.username}, \
date_added={timezone.now()}, \
falls_under={item['category']}, \
text={item['question']}, \
question_type=MULTIPLE, \
difficulty={item['difficulty'].upper()}, \
correct_option={item['correct_answer']}, \
incorrect_answers={item['incorrect_answers']}"
            )

            question = Question(
                who_added=user,
                date_added=timezone.now(),
                text=item["question"],
                question_type=Question.MULTIPLE,
                difficulty=item["difficulty"].upper(),
                correct_option=Option.objects.get(text=item["correct_answer"]),
            )
            questions_to_create.append(question)

            incorrect_options = []
            for incorrect_answer in item["incorrect_answers"]:
                option = Option.objects.get(text=incorrect_answer)
                incorrect_options.append(option)
            item["incorrect_answers"] = incorrect_options

            if item["category"] not in category_mapping:
                category = Category.objects.get(name=item["category"])
                category_mapping[item["category"]] = category

        Question.objects.bulk_create(questions_to_create)

        for question, item in zip(questions_to_create, data):
            category = category_mapping[item["category"]]
            question.falls_under.add(category)
            question.incorrect_options.set(item["incorrect_answers"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully added {len(questions_to_create)} questions."
            )
        )
