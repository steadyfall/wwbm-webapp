import asyncio, aiohttp, random, json
import logging
from html import unescape
from time import perf_counter, time
from ._private import difficulty_choices, html_get

from django.core.management.base import BaseCommand


def configure_logger(enable_logging, log_to_file):
    logger = logging.getLogger(__name__)

    if enable_logging:
        logger.setLevel(logging.INFO)  # Set the default log level to INFO

        # Clear any previous handlers
        if logger.hasHandlers():
            logger.handlers.clear()

        # Set logging to console or file based on the argument
        handler = (
            logging.FileHandler("trivia_fetch.log")
            if log_to_file
            else logging.StreamHandler()
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        logging.disable(logging.CRITICAL)  # Disable all logging

    return logger


class Command(BaseCommand):
    help = "Fetch questions from OpenTriviaDB and generate a JSON file to insert them into DB."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mapped_difficulties = {
            "e": "easy",
            "m": "medium",
            "h": "hard",
        }
        self._difficulty_choices = difficulty_choices
        self._categories = list(x for x in range(9, 32 + 1)) + ["any"]
        self._category_text = '9-32 (both inclusive) or "any"'
        self.logger = None

    async def _category_lookup(self):
        categories = {}
        link = "https://opentdb.com/api_category.php"
        result = await html_get(link)
        if len(result["trivia_categories"]) == 0:
            self.logger.error(" | ".join([link, "Not Done"]))
            return None
        for cat in result["trivia_categories"]:
            categories[int(cat["id"])] = unescape(cat["name"])
        return categories

    async def _category_question_count_lookup(self, category_id: int) -> dict[str, int]:
        count = {}
        link = "https://opentdb.com/api_count.php?category=" + str(category_id)
        result = await html_get(link)
        if result["category_id"] != category_id:
            self.logger.error(" | ".join([link, "Not Done"]))
            return None
        question_count = result["category_question_count"]
        for cat in question_count.keys():
            type_count = cat.split("_")
            type_count = type_count[0 if len(type_count) == 3 else 1]
            count[type_count.lower()] = int(question_count[cat])
        return count

    async def _GET_query_initializer(self):
        global_parameters = ("amount", "category", "difficulty", "type")
        categories = await self._category_lookup()
        difficulty = ["easy", "medium", "hard", "any"]

        async def generator(amt, cat, diff, options_type, debug=False):
            self.logger.warning(f"PREV: {amt}, {cat}, {diff}, {options_type}")
            self.logger.warning(
                f"TYPE: {type(amt)}, {type(cat)}, {type(diff)}, {type(options_type)}"
            )

            parameters = list(global_parameters)
            amt = str(amt) if (isinstance(amt, int) and (10 <= amt <= 50)) else None
            cat = (
                str(cat)
                if (
                    (isinstance(cat, int) or isinstance(cat, str))
                    and (cat in tuple(categories.keys()))
                )
                else None
            )
            diff = diff if (isinstance(diff, str) and (diff in difficulty)) else None
            options_type = (
                options_type
                if (isinstance(options_type, str) and (options_type == "multiple"))
                else None
            )

            if not (amt and cat and diff and options_type):
                self.logger.warning(f"{amt}, {cat}, {diff}, {options_type}")
                raise TypeError() from None

            args = [amt, cat, diff, options_type]
            if isinstance(cat, str) and cat == "any":
                parameters.pop(1)
                args.pop(1)
            if isinstance(diff, str) and diff == "any":
                parameters.pop(1 if len(args) == 3 else 2)
                args.pop(1 if len(args) == 3 else 2)

            self.logger.warning(f"{args} | {type(args)}")

            if "category" in parameters:
                category_count = await self._category_question_count_lookup(int(cat))
                if "difficulty" not in parameters:
                    diff = "total"
                args[0] = (
                    str(category_count[diff] - 1)
                    if (int(amt) >= category_count[diff])
                    else args[0]
                )

            kv = "&".join(["=".join(i) for i in list(zip(parameters, args))])
            return "https://opentdb.com/api.php?" + kv

        return generator

    async def _fetch_question(self, session, url):
        async with session.get(url) as response:
            return await response.json()  # Assuming the response is JSON

    async def _fetch_questions(self, api_urls):
        def unescape_question(qn):
            qn["question"] = unescape(qn["question"])
            qn["correct_answer"] = unescape(qn["correct_answer"])
            qn["incorrect_answers"] = [unescape(ans) for ans in qn["incorrect_answers"]]
            return qn

        response_code_statuses = {
            1: "No Results",
            2: "Invalid Parameter",
            3: "Token Not Found",
            4: "Token Empty",
            5: "Rate Limit",
        }
        responses = []

        categories = await self._category_lookup()
        retrieved_categories = []

        async with aiohttp.ClientSession() as session:
            for api_url in api_urls:
                result = await self._fetch_question(session, api_url)
                rc = result["response_code"]
                if rc != 0:
                    self.logger.warning(
                        " | ".join([api_url, str(rc), response_code_statuses[rc]])
                    )
                else:
                    if "category=" in api_url:
                        cat_id = int(api_url.split("category=")[-1].split("&")[0])
                        retrieved_categories.append(categories[cat_id])
                    list_of_qns = list(result["results"])
                    list_of_qns = map(lambda q: unescape_question(q), list_of_qns)
                    responses.extend(list_of_qns)

                await asyncio.sleep(5)  # Wait 5 seconds between requests

        msg = f"Added categories ({len(retrieved_categories)}): {', '.join(retrieved_categories)}"
        self.logger.info(msg)
        self.stdout.write(self.style.NOTICE(msg))
        return responses

    async def _handle(self, queries, amount, category, difficulty):
        GET_query_generator = await self._GET_query_initializer()
        query_coroutines = [
            GET_query_generator(a, b, c, d)
            for a, b, c, d in list(
                zip(amount, category, difficulty, ["multiple"] * queries)
            )
        ]

        start = perf_counter()
        query_links = await asyncio.gather(*query_coroutines)
        end = perf_counter()
        msg = f"Questions generated in {end-start} seconds."
        self.logger.info(msg)
        self.stdout.write(self.style.SUCCESS(msg))

        start = perf_counter()
        responses = await self._fetch_questions(query_links)
        with open(f"fetched_questions_{time()}.json", "w") as f:
            json.dump(responses, f, indent=4)
        end = perf_counter()
        msg = f"Questions fetched in {end-start} seconds."
        self.logger.info(msg)
        self.stdout.write(self.style.SUCCESS(msg))

    def add_arguments(self, parser):
        parser.add_argument(
            "queries",
            nargs="?",
            type=int,
            default=10,
            help="Number of queries to make.",
        )

        parser.add_argument(
            "-a",
            "--amount",
            metavar="amt",
            nargs="?",
            type=int,
            default=0,
            help="Number of questions from each category/difficulty.",
        )

        parser.add_argument(
            "-c",
            "--category",
            metavar="",
            nargs="*",
            type=str,
            choices=self._categories,
            default="any",
            help="Categories available to pull from. Allowed values include: "
            + self._category_text,
        )

        parser.add_argument(
            "-d",
            "--difficulty",
            metavar="",
            nargs="?",
            type=str,
            choices=self._difficulty_choices,
            default="all",
            help="Difficulty of questions to pull from. Allowed values include: "
            + ", ".join(self._difficulty_choices)
            + ". "
            + "If not written, then any difficulties will be included.",
        )

        """
        parser.add_argument(
            '-b', '--binary',
            action='store_true',
            help='Fetch binary-decision questions. (skip this flag if only MCQ questions are wanted)'
        )
        """

        parser.add_argument(
            "--log-to-file",
            action="store_true",
            help="Log output to the console instead of a file.",
        )

        parser.add_argument(
            "--enable-logging", action="store_true", help="Enable logging."
        )

    def handle(self, *args, **options):
        queries = options.get("queries", None)
        amount = options.get("amount", None)
        category = options.get("category", None)
        difficulty = options.get("difficulty", None)
        # binary = options.get('binary', None)
        log_to_file = options.get("log_to_file", False)
        enable_logging = options.get("enable_logging", False)

        # Configure logger based on argument
        self.logger = configure_logger(enable_logging, log_to_file)

        amount = list(range(10, 20)) if (amount == 0) else [amount]

        category = (
            self._categories
            if (category == "any")
            else list(map(lambda x: int(x), category))
        )

        difficulty = (
            ["easy", "medium", "hard", "any"]
            if (difficulty == "all")
            else [self._mapped_difficulties[d] for d in difficulty]
        )

        amount = random.choices(amount, k=queries)
        category = random.choices(category, k=queries)
        difficulty = random.choices(difficulty, k=queries)

        asyncio.run(self._handle(queries, amount, category, difficulty))
