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


if __name__ == "__main__":
    # проверка модуля при прямом запуске: python people.py
    p = Person("иванов иван петрович", "IvAnov@Mail.Ru", "89211112233")
    print(p, p.masked_phone(), p.short_fio())
    try:
        Person("сидоров", "sidorov@mail.ru", "89211112233")
    except AnketaError as e:
        print("не принято:", e)
