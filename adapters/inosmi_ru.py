from bs4 import BeautifulSoup

from adapters.exceptions import ArticleNotFound
from adapters.html_tools import remove_buzz_attrs, remove_buzz_tags, remove_all_tags


def sanitize(html, plaintext=False):
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.select_one("div.layout-article")

    if not article:
        raise ArticleNotFound()

    article.attrs = {}

    buzz_blocks = [
        *article.select('.article__notice'),
        *article.select('.article__aggr'),
        *article.select('aside'),
        *article.select('.media__copyright'),
        *article.select('.article__meta'),
        *article.select('.article__info'),
        *article.select('.article__tags'),
    ]
    for el in buzz_blocks:
        el.decompose()

    remove_buzz_attrs(article)
    remove_buzz_tags(article)

    if not plaintext:
        text = article.prettify()
    else:
        remove_all_tags(article)
        text = article.get_text()
    return text.strip()
