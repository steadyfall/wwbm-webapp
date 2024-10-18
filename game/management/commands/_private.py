import asyncio, requests, itertools
from html import unescape

difficulty_choices = list(
    (
        "".join(x)
        for x in itertools.chain.from_iterable(
            itertools.permutations("emh", r) for r in range(1, len("emh") + 1)
        )
    )
)  # regex : (?:([emh])(?!.*\1))+


def html_get_sync(link):
    result = requests.get(link)
    return result.json()


async def html_get(link):
    return await asyncio.to_thread(html_get_sync, link)


async def category_lookup():
    categories = {}
    link = "https://opentdb.com/api_category.php"
    result = await html_get(link)
    if len(result["trivia_categories"]) == 0:
        print(" | ".join([link, "Not Done"]))
        return None
    for cat in result["trivia_categories"]:
        categories[int(cat["id"])] = unescape(cat["name"])
    return categories
