import asyncio
import dataclasses
import logging
import time
from contextlib import contextmanager
from enum import Enum

import pytest
from aiohttp import InvalidURL, ClientResponseError, ClientSession
from anyio import create_task_group
from async_timeout import timeout
from pymorphy2 import MorphAnalyzer

from adapters.exceptions import ArticleNotFound
from adapters.inosmi_ru import sanitize
from text_tools import split_by_words, calculate_jaundice_rate

TIMEOUT_IN_SECONDS = 3


class ProcessingStatus(str, Enum):
    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    TIMEOUT = 'TIMEOUT'


@dataclasses.dataclass
class Article:
    url: str
    status: ProcessingStatus
    words_count: int | None = None
    rate: float | None = None


@contextmanager
def timer():
    start = time.monotonic()
    yield lambda: time.monotonic() - start


async def fetch_article_text(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


def get_charged_words_from_file(path):
    with open(path, 'r') as file:
        words = file.readlines()
    return list(map(lambda word: word.strip(), words))


async def process_article(charged_words: list[str], morph: MorphAnalyzer, session: ClientSession, article,
                          rates: list) -> None:
    try:
        async with timeout(TIMEOUT_IN_SECONDS):
            article_text = await fetch_article_text(session, article)

        clean_plaintext = sanitize(article_text, plaintext=True)

        with timer() as counter:
            async with timeout(TIMEOUT_IN_SECONDS):
                words = await split_by_words(morph, clean_plaintext)
            rate = calculate_jaundice_rate(words, charged_words)

        rates.append(
            Article(
                status=ProcessingStatus.OK,
                url=article,
                words_count=len(words),
                rate=rate
            )
        )
        logging.info(f'finished in {counter():.4f} second(s)')
    except (InvalidURL, ClientResponseError):
        rates.append(Article(url=article, status=ProcessingStatus.FETCH_ERROR))
    except ArticleNotFound:
        rates.append(Article(url=article, status=ProcessingStatus.PARSING_ERROR))
    except asyncio.exceptions.TimeoutError:
        rates.append(Article(url=article, status=ProcessingStatus.TIMEOUT))


async def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

    morph = MorphAnalyzer()
    charged_words = get_charged_words_from_file('charged_dict/negative_words.txt')
    charged_words.extend(get_charged_words_from_file('charged_dict/positive_words.txt'))

    TEST_ARTICLES = [
        'https://inosmi.ru/20230204/neft-260327000.html',
        'https://inosmi.ru/20230204/ssha-260319321.html',
        'https://inosmi.ru/20230204/yuzhnaya-koreya-260307651.html',
        'https://inosmi.ru/20230204/molo-260328162.html',
        'https://inosmi.ru/20230204/surrogatnoe-materinstvo-260325860.html',
        'https://inosmi.ru/20230204/iran_afganistan-260325637.html',
        'https://inosmi.ru/not/exist.html',
        'skjbgskdbnvlsdbvnso',
        'https://lenta.ru/brief/2021/08/26/afg_terror/',
    ]

    rates = []

    'http://localhost:8888/?urls=https://inosmi.ru/20230204/neft-260327000.html,https://inosmi.ru/20230204/ssha-260319321.html,https://inosmi.ru/20230204/yuzhnaya-koreya-260307651.html,https://inosmi.ru/not/exist.html,https://lenta.ru/brief/2021/08/26/afg_terror/,asdgftaegdhjtehrs'

    async with ClientSession() as session:
        async with create_task_group() as tg:
            for article in TEST_ARTICLES:
                tg.start_soon(process_article, charged_words, morph, session, article, rates)

    # test_file_path = 'gogol_nikolay_taras_bulba_-_bookscafenet.txt'
    # with open(test_file_path, 'r') as file:
    #     test_text = file.read()
    #
    # with timer() as counter:
    #     try:
    #         async with timeout(TIMEOUT_IN_SECONDS):
    #             words = await split_by_words(morph, test_text)
    #         rate = calculate_jaundice_rate(words, charged_words)
    #     except asyncio.exceptions.TimeoutError:
    #         print('TimeoutError')
    #
    #
    # logging.info(f'finished in {counter():.4f} second(s)')


if __name__ == '__main__':
    asyncio.run(main())

fetch_error_article = Article(
    url='https://inosmi.ru/not/exist.html',
    status=ProcessingStatus.FETCH_ERROR,
    words_count=None,
    rate=None
)

parsing_error_article = Article(
    url='https://lenta.ru/brief/2021/08/26/afg_terror/',
    status=ProcessingStatus.PARSING_ERROR,
    words_count=None,
    rate=None
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'article_url,article',
    [(fetch_error_article.url, fetch_error_article), (parsing_error_article.url, parsing_error_article)]
)
async def test_parsing_error(article_url, article, analyzer, charged_words):
    articles = []
    async with ClientSession() as session:
        await process_article(charged_words, analyzer, session, article_url, articles)

    processed_article, = articles

    assert processed_article == article
