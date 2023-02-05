import dataclasses
import json
import logging

import aiohttp
import pymorphy2
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp.web_response import json_response
from anyio import create_task_group

from main import process_article, get_charged_words_from_file


def json_encode(articles):
    return json.dumps([dataclasses.asdict(article) for article in articles], indent=4, )


async def handle(request):
    query = request.query.get('urls')
    if not query:
        raise HTTPBadRequest

    urls = query.split(',')
    if not urls or len(urls) > 10:
        raise HTTPBadRequest

    rates = []
    app = request.app

    async with aiohttp.ClientSession() as session:
        async with create_task_group() as tg:
            for article in urls:
                tg.start_soon(process_article, app['charged_words'], app['morph'], session, article, rates)

    return json_response(rates, dumps=json_encode)


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

    morph = pymorphy2.MorphAnalyzer()
    charged_words = get_charged_words_from_file('charged_dict/negative_words.txt')
    charged_words.extend(get_charged_words_from_file('charged_dict/positive_words.txt'))

    app = web.Application()
    app.add_routes([
        web.get('/', handle),
        web.get('/{name}', handle)
    ])
    app['morph'] = morph
    app['charged_words'] = charged_words
    web.run_app(app, port=8888)


if __name__ == '__main__':
    main()
