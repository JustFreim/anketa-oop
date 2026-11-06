# Журнал анкет: хранит принятые и бракованные, читает и сохраняет файлы

from people import AnketaError, parse_line


class Registry:
    """Журнал: содержит анкеты (композиция), сам анкетой не является."""

    def __init__(self):
        self.people = []    # принятые анкеты (объекты Student и Teacher)
        self.bad = []       # брак: (номер строки, строка, причина)
        self.total = 0      # всего строк в файле
        self.empty = 0      # из них пустых

    def add(self, person):
        self.people.append(person)

    def load(self, filename):
        """Читает файл. Возвращает False, если файла нет."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            return False
        self.total = len(lines)
        for num, line in enumerate(lines, 1):
            if line.strip() == "":
                self.empty += 1
                continue
            try:
                self.add(parse_line(line))
            except AnketaError as e:
                self.bad.append((num, line.strip(), str(e)))
        return True

    def sorted_people(self):
        return sorted(self.people)

    def stat_by_role(self):
        stat = {}
        for p in self.people:
            stat[p.role()] = stat.get(p.role(), 0) + 1
        return stat

    def stat_by_group(self):
        stat = {}
        for p in self.people:
            group = p.group_name()
            if group:
                stat[group] = stat.get(group, 0) + 1
        return stat

    def save_ok(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            for p in self.sorted_people():
                row = [p.role(), p.fio, p.mail, p.phone, p.extra()]
                f.write(";".join(row) + "\n")

    def save_errors(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            for num, line, reason in self.bad:
                f.write(f"строка {num}: {reason}\n    {line}\n")

    def __len__(self):
        return len(self.people)

    def __iter__(self):
        return iter(self.people)


if __name__ == "__main__":
    # проверка модуля при прямом запуске: python registry.py
    reg = Registry()
    print("файл найден:", reg.load("data/anketa.txt"))
    print("принято:", len(reg), "| брака:", len(reg.bad))
