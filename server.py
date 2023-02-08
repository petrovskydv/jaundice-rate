import dataclasses
import json
import logging
from http import HTTPStatus

import pymorphy2
from aiohttp import web, ClientSession
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp.web_response import json_response
from anyio import create_task_group

from main import process_article, get_charged_words_from_file


def encode_articles(articles):
    """Функция для сериализации датакласса в json"""
    encoded_articles = [dataclasses.asdict(article) for article in articles]
    return json.dumps(encoded_articles, indent=4)


async def handle(request):
    query = request.query.get('urls')
    if not query:
        raise HTTPBadRequest

    urls = query.split(',')
    if len(urls) > 10:
        return json_response({'error': 'too many urls in request, should be 10 or less'}, status=HTTPStatus.BAD_REQUEST)

    rates = []
    app = request.app

    async with ClientSession() as session:
        async with create_task_group() as tg:
            for article in urls:
                tg.start_soon(process_article, app['charged_words'], app['morph'], session, article, rates)

    return json_response(rates, dumps=encode_articles)


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

    morph = pymorphy2.MorphAnalyzer()
    charged_words = get_charged_words_from_file('charged_dict/negative_words.txt')
    charged_words.extend(get_charged_words_from_file('charged_dict/positive_words.txt'))

    app = web.Application()
    app.add_routes([
        web.get('/', handle),
    ])
    app['morph'] = morph
    app['charged_words'] = charged_words
    web.run_app(app, port=8888)


if __name__ == '__main__':
    main()
