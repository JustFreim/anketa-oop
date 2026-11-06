import pytest

from people import Student
from registry import Registry

# строки: 1, 3, 6 верные; 2, 5, 7 бракованные; 4 пустая
STROKI = """s;иванов иван;ivanov@mail.ru;89211112233;09с33
s;сидоров;sidorov@mail.ru;89210000000;09с34
t;петров пётр;petrov@voenmeh.ru;89217654321;Кафедра И9

s;кузнецов павел;kuznetsov.mail.ru;89211234567;09с34
s;петрова анна;petrova@yandex.ru;89217654321;09с33
x;кто то;a@b.ru;89211112233;что-то
"""


@pytest.fixture
def zhurnal(tmp_path):
    put = tmp_path / "anketa.txt"
    put.write_text(STROKI, encoding="utf-8")
    r = Registry()
    r.load(put)
    return r


def test_pustoy_zhurnal_dlina_nol():
    assert len(Registry()) == 0


def test_posle_zagruzki_tri_anketi(zhurnal):
    assert len(zhurnal) == 3


def test_v_brake_tri_zapisi(zhurnal):
    assert len(zhurnal.bad) == 3


def test_nomera_strok_braka(zhurnal):
    nomera = [num for num, stroka, prichina in zhurnal.bad]
    assert nomera == [2, 5, 7]


def test_load_nesushchestvuyushchiy_fayl(tmp_path):
    r = Registry()
    assert r.load(tmp_path / "net-takogo.txt") is False
    assert len(r) == 0


def test_stat_po_rolyam(zhurnal):
    assert zhurnal.stat_by_role() == {"студент": 2, "преподаватель": 1}


def test_stat_po_gruppam_tolko_studenty(zhurnal):
    assert zhurnal.stat_by_group() == {"09с33": 2}


def test_zhurnal_perebiraetsya_tsiklom_for(zhurnal):
    familii = []
    for p in zhurnal:
        familii.append(p.fio.split()[0])
    assert sorted(familii) == ["Иванов", "Петров", "Петрова"]


def test_sortirovka_po_alfavitu(zhurnal):
    familii = [p.fio.split()[0] for p in zhurnal.sorted_people()]
    assert familii == ["Иванов", "Петров", "Петрова"]


def test_save_ok_stroka_na_cheloveka(zhurnal, tmp_path):
    put = tmp_path / "ok.txt"
    zhurnal.save_ok(put)
    stroki = put.read_text(encoding="utf-8").splitlines()
    assert len(stroki) == 3
    assert stroki[0].startswith("студент;Иванов Иван;")


def test_save_errors_pishet_prichinu(zhurnal, tmp_path):
    put = tmp_path / "errors.txt"
    zhurnal.save_errors(put)
    tekst = put.read_text(encoding="utf-8")
    assert "строка 2: в ФИО меньше двух слов" in tekst
    assert "строка 7: неизвестный тип: x" in tekst
