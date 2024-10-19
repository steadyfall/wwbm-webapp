import logging
from time import perf_counter
from game.models import Lifeline

from django.core.management.base import BaseCommand


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


lifelines = [
    (
        "Fifty-50",
        "Two incorrect answers are eliminated, leaving the contestant with a choice between the correct answer and one remaining incorrect answer.",
    ),
    (
        "Audience Poll",
        "The audience members individually use four-button keypads to register the answer they believe is correct, and the percentage of votes for each answer is then shown to the host and contestant.",
    ),
    (
        "Expert Answer",
        "The contestant is given a probable answer by the expert appointed for the game, and the probability of their answer being correct is more than 50%.",
    ),
]


class Command(BaseCommand):
    help = "USE ONLY WHEN INITIALIZING THE APP! Creates lifelines for the app in the database. (for Lifeline model)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--enable-logging", action="store_true", help="Enable logging completely."
        )

    def handle(self, *args, **options):
        enable_logging = options.get("enable_logging", False)

        # Configure logger based on argument
        self.logger = configure_logger(enable_logging)

        start = perf_counter()
        count = 0
        for lifeline_name, lifeline_description in lifelines:
            lifeline_exists = Lifeline.objects.filter(name=lifeline_name).exists()

            if lifeline_exists:
                self.stdout.write(
                    self.style.WARNING(
                        f"Lifeline '{lifeline_name}' already exists. Skipping..."
                    )
                )
                self.logger.warning(
                    f"Lifeline '{lifeline_name}' already exists with description."
                )

            else:
                Lifeline.objects.create(
                    name=lifeline_name, description=lifeline_description
                )
                self.logger.info(f"+ Added lifeline: {lifeline_name}")
                count += 1

        end = perf_counter()
        msg = f"{count} lifelines created in {end-start} seconds."
        self.logger.info(msg)
        self.stdout.write(self.style.SUCCESS(msg))
