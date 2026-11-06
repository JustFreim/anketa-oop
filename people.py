# Анкеты: своё исключение и классы Person, Student, Teacher


class AnketaError(Exception):
    """Анкета не прошла проверку."""


class Person:
    """Общая часть анкеты: ФИО, почта, телефон и их проверки."""

    @staticmethod
    def check_fio(raw):
        """Возвращает ФИО в нормальном виде или бросает AnketaError."""
        parts = raw.split()
        if len(parts) < 2:
            raise AnketaError("в ФИО меньше двух слов")
        return " ".join(parts).title()

    @staticmethod
    def check_mail(raw):
        """Возвращает почту в нижнем регистре или бросает AnketaError."""
        mail = raw.strip().lower()
        bad = "почта неверная: " + raw.strip()
        if mail.count("@") != 1:
            raise AnketaError(bad)
        name, domain = mail.split("@")
        if name == "" or "." not in domain:
            raise AnketaError(bad)
        if domain.startswith(".") or domain.endswith("."):
            raise AnketaError(bad)
        return mail

    @staticmethod
    def check_phone(raw):
        """Возвращает телефон +7 (921) 111-22-33 или бросает ошибку."""
        digits = []
        for ch in raw:
            if ch.isdigit():
                digits.append(ch)
        d = "".join(digits)
        if len(d) != 11:
            raise AnketaError(
                f"телефон неверный: цифр {len(d)}, нужно 11")
        if d[0] not in "78":
            raise AnketaError("телефон неверный: номер должен "
                              "начинаться с 7 или 8")
        return f"+7 ({d[1:4]}) {d[4:7]}-{d[7:9]}-{d[9:]}"

    def __init__(self, fio, mail, phone):
        """Принимает сырые данные, приводит в порядок и проверяет."""
        self.fio = self.check_fio(fio)
        self.mail = self.check_mail(mail)
        self.phone = self.check_phone(phone)

    def masked_phone(self):
        return self.phone[:9] + "***-**-" + self.phone[-2:]

    def short_fio(self):
        parts = self.fio.split()
        result = parts[0]
        for word in parts[1:]:
            result += " " + word[0] + "."
        return result

    def role(self):
        return "—"

    def extra(self):
        return "—"

    def group_name(self):
        """Название группы. У тех, у кого группы нет, возвращает None."""
        return None

    def __str__(self):
        return f"{self.fio} ({self.role()})"

    def __lt__(self, other):
        return self.fio < other.fio


class Student(Person):
    """Студент: общая часть от Person и группа."""

    def __init__(self, fio, mail, phone, group):
        super().__init__(fio, mail, phone)
        self.group = "".join(group.split()).lower()
        if self.group == "":
            raise AnketaError("группа не указана")

    def role(self):
        return "студент"

    def extra(self):
        return self.group

    def group_name(self):
        return self.group


class Teacher(Person):
    """Преподаватель: общая часть от Person и кафедра."""

    def __init__(self, fio, mail, phone, department):
        super().__init__(fio, mail, phone)
        self.department = " ".join(department.split())
        if self.department == "":
            raise AnketaError("кафедра не указана")

    def role(self):
        return "преподаватель"

    def extra(self):
        return self.department


def parse_line(line):
    """Разбирает строку файла: возвращает Student или Teacher.

    Единственное место, где выбор класса зависит от типа анкеты.
    """
    fields = line.split(";")
    if len(fields) != 5:
        raise AnketaError(f"полей {len(fields)} вместо 5")
    kind = fields[0].strip().lower()
    if kind == "s":
        return Student(*fields[1:])
    if kind == "t":
        return Teacher(*fields[1:])
    raise AnketaError("неизвестный тип: " + fields[0].strip())


if __name__ == "__main__":
    # проверка модуля при прямом запуске: python people.py
    lines = [
        "s;иванов иван;ivanov@mail.ru;89211112233;09с33",
        "t;петров пётр;petrov@voenmeh.ru;89217654321;Кафедра И9",
        "x;неизвестный тип;a@b.ru;89211112233;что-то",
    ]
    for line in lines:
        try:
            p = parse_line(line)
            print(p, "|", p.extra())
        except AnketaError as e:
            print("не принято:", e)
