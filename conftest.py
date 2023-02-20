import pytest
from pymorphy2 import MorphAnalyzer

from main import get_charged_words_from_file


@pytest.fixture(scope='session')
def analyzer():
    return MorphAnalyzer()


@pytest.fixture(scope='session')
def charged_words():
    charged_words = get_charged_words_from_file('charged_dict/negative_words.txt')
    charged_words.extend(get_charged_words_from_file('charged_dict/positive_words.txt'))
    return charged_words
