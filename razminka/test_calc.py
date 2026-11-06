import pytest

from calc import skidka, srednee, summa


# P1. Первый тест
def test_summa_polozhitelnye():
    assert summa(2, 3) == 5


def test_summa_s_nulem():
    assert summa(0, 7) == 7


# P2. Тест к функции скидки
def test_skidka_10_procentov():
    assert skidka(1000, 10) == 900


# P3. Тесты на ошибку
def test_skidka_slishkom_bolshaya():
    with pytest.raises(ValueError):
        skidka(1000, 95)


def test_srednee_pustoy_spisok():
    with pytest.raises(ValueError):
        srednee([])


# P4. Параметризация
@pytest.mark.parametrize("chisla, ozhidaem", [
    ([5], 5),
    ([2, 4], 3),
    ([1, 2, 3, 4], 2.5),
    ([-2, 2], 0),
])
def test_srednee_neskolko_naborov(chisla, ozhidaem):
    assert srednee(chisla) == ozhidaem
