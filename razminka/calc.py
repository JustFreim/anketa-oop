"""Небольшой модуль для разминки по тестам."""


def summa(a, b):
    """Складывает два числа."""
    return a + b


def skidka(cena, procent):
    """Цена со скидкой. Процент от 0 до 90."""
    if procent < 0 or procent > 90:
        raise ValueError("процент скидки должен быть от 0 до 90")
    return round(cena * (100 - procent) / 100, 2)


def srednee(chisla):
    """Среднее арифметическое. Пустой список — ошибка."""
    if len(chisla) == 0:
        raise ValueError("список пустой")
    return sum(chisla) / len(chisla)
