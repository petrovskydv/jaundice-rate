import pytest
from aiohttp import ClientSession

from main import process_article, Article, ProcessingStatus

FETCH_ERROR_ARTICLE = Article(
    url='https://inosmi.ru/not/exist.html',
    status=ProcessingStatus.FETCH_ERROR,
    words_count=None,
    rate=None
)
PARSING_ERROR_ARTICLE = Article(
    url='https://lenta.ru/brief/2021/08/26/afg_terror/',
    status=ProcessingStatus.PARSING_ERROR,
    words_count=None,
    rate=None
)


RIGHT_ARTICLE = Article(
    url='https://inosmi.ru/20230204/neft-260327000.html',
    status=ProcessingStatus.OK,
    words_count=774,
    rate=1.94
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'article_url, article',
    [
        (FETCH_ERROR_ARTICLE.url, FETCH_ERROR_ARTICLE),
        (PARSING_ERROR_ARTICLE.url, PARSING_ERROR_ARTICLE),
        (RIGHT_ARTICLE.url, RIGHT_ARTICLE)
    ]
)
async def test_parsing(article_url, article, analyzer, charged_words):
    articles = []
    async with ClientSession() as session:
        await process_article(charged_words, analyzer, session, article_url, articles)

    processed_article, = articles

    assert processed_article == article
