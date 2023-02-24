import pytest
from pymorphy2 import MorphAnalyzer

from services.processor import get_charged_words_from_file


@pytest.fixture(scope='session')
def analyzer():
    return MorphAnalyzer()


@pytest.fixture(scope='session')
def charged_words():
    negative_words_path = '../charged_dict/negative_words.txt'
    positive_words_path = '../charged_dict/positive_words.txt'
    charged_words = get_charged_words_from_file(negative_words_path)
    charged_words.extend(get_charged_words_from_file(positive_words_path))
    return charged_words
