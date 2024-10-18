import asyncio, requests, itertools

difficulty_choices = list(
    (
        "".join(x)
        for x in 
        itertools.chain.from_iterable(
            itertools.permutations("emh", r) 
            for r in 
            range(1, len("emh")+1)
        )
    )
)                   # regex : (?:([emh])(?!.*\1))+

def html_get_sync(link):
    result = requests.get(link)
    return result.json()

async def html_get(link):
    return await asyncio.to_thread(html_get_sync, link)
