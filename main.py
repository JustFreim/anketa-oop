# Обработчик анкет на классах: запуск и вывод

from registry import Registry

INPUT_FILE = "data/anketa.txt"
OK_FILE = "ok.txt"
ERR_FILE = "errors.txt"

W_FIO = 28          # ширины колонок таблицы
W_ROLE = 15
W_EXTRA = 16


def fit(text, width):
    if len(text) > width:
        return text[:width - 1] + "~"
    return text


def print_table(registry):
    line = "-" * (5 + W_FIO + W_ROLE + W_EXTRA + 18)
    print(f"{'№':>3}  {'ФИО':<{W_FIO}}{'Роль':<{W_ROLE}}"
          f"{'Группа/кафедра':<{W_EXTRA}}Телефон")
    print(line)
    for i, p in enumerate(registry.sorted_people(), 1):
        print(f"{i:>3}  {fit(p.fio, W_FIO - 1):<{W_FIO}}"
              f"{p.role():<{W_ROLE}}"
              f"{fit(p.extra(), W_EXTRA - 1):<{W_EXTRA}}"
              f"{p.masked_phone()}")
    print(line)


def print_bad(registry):
    print("Отклонено строк:", len(registry.bad))
    for num, line, reason in registry.bad:
        print(f"  строка {num}: {reason}")
        print("      " + line)


def print_stat(registry):
    print(f"Всего строк в файле: {registry.total} "
          f"(пустых пропущено: {registry.empty})")
    print(f"Принято: {len(registry)} | Отклонено: {len(registry.bad)}")
    print("\nПо ролям:")
    for role, count in sorted(registry.stat_by_role().items()):
        print(f"  {role:<15}{count}")
    print("\nПо группам:")
    for group, count in sorted(registry.stat_by_group().items()):
        print(f"  {group:<15}{count}")


def main():
    registry = Registry()
    if not registry.load(INPUT_FILE):
        print("Файл", INPUT_FILE, "не найден. Положите его в папку data/")
        return
    print_table(registry)
    print()
    print_bad(registry)
    print()
    print_stat(registry)
    registry.save_ok(OK_FILE)
    registry.save_errors(ERR_FILE)
    print(f"\nСохранено: {OK_FILE} и {ERR_FILE}")


if __name__ == "__main__":
    main()
