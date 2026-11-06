import pytest

from people import AnketaError, Person, Student, Teacher, parse_line
from registry import Registry


def make_student():
    return Student("  иванов   иВАН петрович ", " IvAnov@Mail.Ru ",
                   "+7 (921) 111-22-33", " 09 С33 ")


def test_person_normalizes_data():
    p = Person("  иванов   иВАН петрович ", " IvAnov@Mail.Ru ", "89211112233")
    assert p.fio == "Иванов Иван Петрович"
    assert p.mail == "ivanov@mail.ru"
    assert p.phone == "+7 (921) 111-22-33"


def test_person_bad_fio():
    with pytest.raises(AnketaError, match="меньше двух слов"):
        Person("сидоров", "sidorov@mail.ru", "89211112233")


def test_person_bad_mail():
    with pytest.raises(AnketaError, match="почта неверная"):
        Person("сидоров иван", "kuznetsov.mail.ru", "89211112233")


def test_person_bad_phone():
    with pytest.raises(AnketaError, match="цифр 7"):
        Person("сидоров иван", "a@mail.ru", "+7921123")


def test_masked_and_short():
    s = make_student()
    assert s.masked_phone() == "+7 (921) ***-**-33"
    assert s.short_fio() == "Иванов И. П."


def test_roles_are_polymorphic():
    s = make_student()
    t = Teacher("петров пётр", "petrov@voenmeh.ru", "89217654321", "Кафедра И9")
    assert (s.role(), s.extra()) == ("студент", "09с33")
    assert (t.role(), t.extra()) == ("преподаватель", "Кафедра И9")


def test_student_empty_group():
    with pytest.raises(AnketaError, match="группа не указана"):
        Student("иванов иван", "a@mail.ru", "89211112233", "  ")


def test_teacher_empty_department():
    with pytest.raises(AnketaError, match="кафедра не указана"):
        Teacher("иванов иван", "a@mail.ru", "89211112233", "")


def test_sorting_by_fio():
    a = Person("яковлев яков", "a@mail.ru", "89211112233")
    b = Person("абрамов абрам", "b@mail.ru", "89211112233")
    assert sorted([a, b]) == [b, a]


def test_parse_line_types():
    s = parse_line("s;иванов иван;ivanov@mail.ru;89211112233;09с33")
    t = parse_line("T;петров пётр;petrov@voenmeh.ru;89217654321;Кафедра И9")
    assert isinstance(s, Student) and isinstance(t, Teacher)


def test_parse_line_errors():
    with pytest.raises(AnketaError, match="неизвестный тип: x"):
        parse_line("x;иванов иван;ivanov@mail.ru;89211112233;09с33")
    with pytest.raises(AnketaError, match="полей 4 вместо 5"):
        parse_line("s;иванов иван;ivanov@mail.ru;89211112233")


def test_registry_load_and_stat(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text(
        "s;иванов иван;ivanov@mail.ru;89211112233;09с33\n"
        "\n"
        "t;петров пётр;petrov@voenmeh.ru;89217654321;Кафедра И9\n"
        "x;кто то;a@b.ru;89211112233;что-то\n",
        encoding="utf-8")
    reg = Registry()
    assert reg.load(str(f)) is True
    assert len(reg) == 2
    assert reg.empty == 1
    assert reg.bad[0][0] == 4
    assert reg.stat_by_role() == {"студент": 1, "преподаватель": 1}
    assert reg.stat_by_group() == {"09с33": 1}


def test_registry_missing_file():
    assert Registry().load("net-takogo-faila.txt") is False
