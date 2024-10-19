import asyncio, aiohttp
import logging
from html import unescape
from time import perf_counter
from ._private import html_get
from game.models import Category
from django.utils import timezone

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


class Command(BaseCommand):
    help = "USE ONLY WHEN INITIALIZING THE APP! Fetch categories from OpenTriviaDB and insert them into the database. (for Category model)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = None

    async def _category_lookup(self):
        categories = {}
        link = "https://opentdb.com/api_category.php"
        result = await html_get(link)
        if not result or len(result["trivia_categories"]) == 0:
            self.logger.error(f"Failed to fetch categories from {link}")
            return None

        for cat in result["trivia_categories"]:
            categories[int(cat["id"])] = unescape(cat["name"])
        return categories

    def add_arguments(self, parser):
        parser.add_argument(
            "--enable-logging", action="store_true", help="Enable logging completely."
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forcefully update categories, even if they exist.",
        )

    def handle(self, *args, **options):
        enable_logging = options.get("enable_logging", False)
        force_update = options.get("force", False)

        # Configure logger based on argument
        self.logger = configure_logger(enable_logging)

        start = perf_counter()
        categories = asyncio.run(self._category_lookup())
        end = perf_counter()
        msg = f"Categories retrieved in {end-start} seconds."
        self.logger.info(msg)
        self.stdout.write(self.style.SUCCESS(msg))

        if not categories:
            self.stdout.write(self.style.ERROR("No categories fetched from API."))
            return

        start = perf_counter()
        for _, category_name in categories.items():
            category_exists = Category.objects.filter(name=category_name).exists()

            if category_exists and not force_update:
                self.stdout.write(
                    self.style.WARNING(
                        f"Category '{category_name}' already exists. Skipping..."
                    )
                )
            else:
                category, created = Category.objects.update_or_create(
                    name=category_name, defaults={"date_created": timezone.now()}
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"+ Added category: {category_name}")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"^ Updated category: {category_name}")
                    )

        end = perf_counter()
        msg = f"Categories created/updated in {end-start} seconds."
        self.logger.info(msg)
        self.stdout.write(self.style.SUCCESS(msg))
