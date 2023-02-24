import asyncio
import dataclasses
import logging
import time
from contextlib import contextmanager
from enum import Enum

from aiohttp import InvalidURL, ClientResponseError, ClientSession
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
