import pytest

from people import AnketaError, Person, Student, Teacher, parse_line

LINE_S = "s;иванов иван;ivanov@mail.ru;89211112233;09с33"
LINE_T = "t;петров пётр;petrov@voenmeh.ru;89217654321;Кафедра И9"


def make_student():
    return Student("иванов иван петрович", "ivanov@mail.ru",
                   "89211112233", "09с33")


def make_teacher():
    return Teacher("петров пётр сергеевич", "petrov@voenmeh.ru",
                   "89217654321", "Кафедра И9")


# ---------- ФИО ----------

@pytest.mark.parametrize("vvod, ozhidaem", [
    ("иванов иван", "Иванов Иван"),
    ("  петров   пётр ", "Петров Пётр"),
    ("СИДОРОВА АННА", "Сидорова Анна"),
    ("иВАНОВ иВАН пЕТРОВИЧ", "Иванов Иван Петрович"),
    ("кузнецов\tпавел", "Кузнецов Павел"),
])
def test_check_fio_privodit_k_odnomu_vidu(vvod, ozhidaem):
    assert Person.check_fio(vvod) == ozhidaem


def test_check_fio_odno_slovo_oshibka():
    with pytest.raises(AnketaError):
        Person.check_fio("сидоров")


# ---------- почта ----------

@pytest.mark.parametrize("vvod, ozhidaem", [
    ("IvAnov@Mail.Ru", "ivanov@mail.ru"),
    ("  petrov@VOENMEH.ru ", "petrov@voenmeh.ru"),
    ("ANNA@YANDEX.RU", "anna@yandex.ru"),
])
def test_check_mail_nizhniy_registr(vvod, ozhidaem):
    assert Person.check_mail(vvod) == ozhidaem


@pytest.mark.parametrize("vvod", [
    "kuznetsov.mail.ru",      # нет @
    "a@@mail.ru",             # две @
    "@mail.ru",               # пустое имя
    "ivanov@mailru",          # нет точки в домене
    "ivanov@.mail.ru",        # домен начинается с точки
    "ivanov@mail.ru.",        # домен кончается точкой
])
def test_check_mail_otklonyaet_plohie(vvod):
    with pytest.raises(AnketaError):
        Person.check_mail(vvod)


# ---------- телефон ----------

@pytest.mark.parametrize("vvod", [
    "89211112233",
    "+7 (921) 111-22-33",
    "8 921 111 22 33",
    "+79211112233",
])
def test_check_phone_odin_vid(vvod):
    assert Person.check_phone(vvod) == "+7 (921) 111-22-33"


@pytest.mark.parametrize("vvod", [
    "+7921123",               # мало цифр
    "892111122334",           # много цифр
    "+19215556677",           # первая цифра не 7 и не 8
    "нет телефона",           # цифр нет совсем
])
def test_check_phone_otklonyaet_plohie(vvod):
    with pytest.raises(AnketaError):
        Person.check_phone(vvod)


# ---------- методы объекта ----------

def test_masked_phone():
    assert make_student().masked_phone() == "+7 (921) ***-**-33"


def test_short_fio():
    assert make_student().short_fio() == "Иванов И. П."


def test_short_fio_bez_otchestva():
    p = Student("петрова анна", "a@mail.ru", "89211112233", "09с34")
    assert p.short_fio() == "Петрова А."


def test_student_i_teacher_otvechayut_po_raznomu():
    assert make_student().role() == "студент"
    assert make_teacher().role() == "преподаватель"


def test_student_bez_gruppy_oshibka():
    with pytest.raises(AnketaError):
        Student("иванов иван", "a@mail.ru", "89211112233", "  ")


def test_teacher_bez_kafedry_oshibka():
    with pytest.raises(AnketaError):
        Teacher("иванов иван", "a@mail.ru", "89211112233", "")


# ---------- разбор строки файла ----------

def test_parse_line_student():
    p = parse_line(LINE_S)
    assert isinstance(p, Student)
    assert p.fio == "Иванов Иван"
    assert p.extra() == "09с33"


def test_parse_line_teacher():
    p = parse_line(LINE_T)
    assert isinstance(p, Teacher)
    assert p.fio == "Петров Пётр"
    assert p.extra() == "Кафедра И9"


@pytest.mark.parametrize("stroka", [
    "x;иванов иван;ivanov@mail.ru;89211112233;09с33",    # неизвестный тип
    "s;иванов иван;ivanov@mail.ru;89211112233",          # мало полей
    "s;иванов иван;ivanov@mail.ru;89211112233;09с33;1",  # много полей
    "",                                                  # пустая строка
])
def test_parse_line_otklonyaet_plohuyu_stroku(stroka):
    with pytest.raises(AnketaError):
        parse_line(stroka)
