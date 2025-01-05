import json, logging
from itertools import islice
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
        Extract questions from a JSON file a JSON file generated via `manage.py fetchqns` command and adds them to the database.
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
        parser.add_argument(
            "--force-update",
            action="store_true",
            help="Forcefully update existing questions.",
        )

    def handle(self, *args, **options):
        def lazy_list_generator(l):
            for obj in l:
                yield obj

        json_file = options["json_file"]
        enable_logging = options.get("enable_logging", False)
        force_update = options.get("force_update")

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

            incorrect_options = []
            for incorrect_answer in item["incorrect_answers"]:
                option = Option.objects.get(text=incorrect_answer)
                incorrect_options.append(option)

            if item["category"] not in category_mapping:
                category = Category.objects.get(name=item["category"])
                category_mapping[item["category"]] = category
            else:
                category = category_mapping[item["category"]]

            if Question.objects.filter(text=item["question"]).exists():
                question = Question.objects.get(text=item["question"])
                if force_update:
                    question.correct_option = Option.objects.get(
                        text=item["correct_answer"]
                    )
                    question.question_type = (
                        Question.MULTIPLE
                    )  # Assuming all are multiple type
                    question.difficulty = item["difficulty"].upper()
                    question.falls_under.add(category)
                    question.incorrect_options.set(incorrect_options)
                    question.save()
                    self.logger.info(
                        f"^ Updated question : ({item['difficulty'].upper()}) {item['question']}"
                    )
                else:
                    self.logger.info(
                        f"- Unchanged question : ({item['difficulty'].upper()}) {item['question']}"
                    )
                item["question"] = ""
                continue
            else:
                self.logger.info(
                    f"+ Added question : ({item['difficulty'].upper()}) {item['question']}"
                )
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

            item["incorrect_answers"] = incorrect_options

        if questions_to_create:
            batch_size = 90
            questions_generator = lazy_list_generator(questions_to_create)
            while True:
                questions_batch = list(islice(questions_generator, batch_size))
                if not questions_batch:
                    break
                Question.objects.bulk_create(questions_batch, batch_size)

            data = list(
                filter(lambda x: True if len(x["question"]) > 0 else False, data)
            )

            for question, item in zip(questions_to_create, data):
                category = category_mapping[item["category"]]
                question.falls_under.add(category)
                question.incorrect_options.set(item["incorrect_answers"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully added {len(questions_to_create)} questions."
            )
        )
