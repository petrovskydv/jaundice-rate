import asyncio

import pymorphy2

from services.text_tools import split_by_words, calculate_jaundice_rate


def test_split_by_words():
    # Экземпляры MorphAnalyzer занимают 10-15Мб RAM т.к. загружают в память много данных
    # Старайтесь организовать свой код так, чтоб создавать экземпляр MorphAnalyzer заранее и в единственном числе
    morph = pymorphy2.MorphAnalyzer()

    assert asyncio.run(split_by_words(morph, 'Во-первых, он хочет, чтобы')) == ['во-первых', 'хотеть', 'чтобы']

    assert asyncio.run(split_by_words(morph, '«Удивительно, но это стало началом!»')) == ['удивительно', 'это', 'стать', 'начало']


def test_calculate_jaundice_rate():
    assert -0.01 < calculate_jaundice_rate([], []) < 0.01
    assert 33.0 < calculate_jaundice_rate(['все', 'аутсайдер', 'побег'], ['аутсайдер', 'банкротство']) < 34.0
