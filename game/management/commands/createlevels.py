import logging
from time import perf_counter
from game.models import Level

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


levels = [
    (-1, 0),
    (0, 0),
    (1, 100),
    (2, 200),
    (3, 300),
    (4, 500),
    (5, 1000),
    (6, 2000),
    (7, 4000),
    (8, 8000),
    (9, 16000),
    (10, 32000),
    (11, 64000),
    (12, 125_000),
    (13, 250_000),
    (14, 500_000),
    (15, 1_000_000),
    (16, 0),
]


class Command(BaseCommand):
    help = "USE ONLY WHEN INITIALIZING THE APP! Creates levels for the app in the database. (for Level model)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--enable-logging", action="store_true", help="Enable logging completely."
        )

    def _handle_existing_level(self, level_number):
        self.stdout.write(
            self.style.WARNING(f"Level '{level_number}' already exists. Skipping...")
        )
        self.logger.warning(f"Level '{level_number}' already exists with prize money.")

    def _handle_created_level(self, level_number):
        self.logger.info(f"+ Added level: {level_number}")

    def handle(self, *args, **options):
        enable_logging = options.get("enable_logging", False)

        # Configure logger based on argument
        self.logger = configure_logger(enable_logging)

        start = perf_counter()
        count = 0
        for level_number, level_money in levels:
            level_exists = Level.objects.filter(level_number=level_number).exists()

            if level_exists:
                self._handle_existing_level(level_number)
            else:
                Level.objects.create(level_number=level_number, money=level_money)
                self._handle_created_level(level_number)
                count += 1

        end = perf_counter()
        msg = f"{count} levels created in {end-start} seconds."
        self.logger.info(msg)
        self.stdout.write(self.style.SUCCESS(msg))
