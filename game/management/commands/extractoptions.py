import json, logging
from itertools import islice
from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured
from game.models import Option


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
    help = "Extracts all unique options from a JSON file generated via `manage.py fetchqns` command."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--enable-logging", action="store_true", help="Enable logging completely."
        )
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to the JSON file generated via `manage.py fetchdb` command",
        )

    def handle(self, *args, **options):
        def lazy_option_generator(options):
            for option in options:
                yield option

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

        unique_options = set()

        for entry in data:
            correct_answer = entry.get("correct_answer")
            incorrect_answers = entry.get("incorrect_answers", [])

            if correct_answer:
                unique_options.add(correct_answer)

            for answer in incorrect_answers:
                unique_options.add(answer)

        options_to_create = []
        for option_text in unique_options:
            if not Option.objects.filter(text=option_text).exists():
                options_to_create.append(Option(text=option_text))
                self.logger.info(f"+ Option ADDED: {option_text}")
            else:
                self.logger.warning(f"- Option EXISIS: {option_text}")

        if not options_to_create:
            self.logger.info("No new options to add.")
            self.stdout.write(self.style.SUCCESS("No new options to add."))

        batch_size = 100
        options_generator = lazy_option_generator(options_to_create)
        while True:
            options_batch = list(islice(options_generator, batch_size))
            if not options_batch:
                break
            Option.objects.bulk_create(options_batch, batch_size)

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(options_to_create)} unique options added to the database."
            )
        )
