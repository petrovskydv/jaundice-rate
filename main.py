import aiohttp
import asyncio

import pymorphy2
from anyio import create_task_group

from adapters.inosmi_ru import sanitize
from text_tools import split_by_words, calculate_jaundice_rate


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


def get_charged_words_from_file(path):
    with open(path, 'r') as file:
        words = file.readlines()
    return list(map(lambda word: word.strip(), words))


async def process_article(charged_words, morph, session, article, rates: list):
    html = await fetch(session, article)
    clean_plaintext = sanitize(html, plaintext=True)
    words = split_by_words(morph, clean_plaintext)
    rate = calculate_jaundice_rate(words, charged_words)

    rates.append({
        'article': article,
        'words_count': len(words),
        'rate': rate
    })


async def main():
    morph = pymorphy2.MorphAnalyzer()
    charged_words = get_charged_words_from_file('charged_dict/negative_words.txt')
    charged_words.extend(get_charged_words_from_file('charged_dict/positive_words.txt'))

    TEST_ARTICLES = [
        'https://inosmi.ru/20230204/neft-260327000.html',
        'https://inosmi.ru/20230204/ssha-260319321.html',
        'https://inosmi.ru/20230204/yuzhnaya-koreya-260307651.html',
        'https://inosmi.ru/20230204/molo-260328162.html',
        'https://inosmi.ru/20230204/surrogatnoe-materinstvo-260325860.html',
        'https://inosmi.ru/20230204/iran_afganistan-260325637.html',
    ]

    rates = []

    async with aiohttp.ClientSession() as session:
        async with create_task_group() as tg:
            for article in TEST_ARTICLES:
                tg.start_soon(process_article, charged_words, morph, session, article, rates)

    print(rates)


if __name__ == '__main__':
    asyncio.run(main())
