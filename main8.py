#клиент к серверу анкет

import json
import client
from client import ServerNedostupen
from people import AnketaError, Person, Student, Teacher
from registry import Registry

FALLBACK_FILE = "anketa.txt" #запасной источник данных
REPORT_FILE = "otchet.json"

W_FIO = 28 #ширины колонок таблицы
W_ROLE = 15
W_EXTRA = 16

def fit(text, width):
    if len(text) > width:
        return text[:width - 1] + "~"
    return text

def text_of(value):
    """поле словаря как строка: нет поля или null - пустая строка"""
    if value is None:
        return ""
    return str(value)

def from_dict(d):
    """словарь с сервера - Student или Teacher, иначе AnketaError"""
    if not isinstance(d, dict):
        raise AnketaError("запись пришла не словарём")
    fio = text_of(d.get("fio"))
    mail = text_of(d.get("mail"))
    phone = text_of(d.get("phone"))
    kind = text_of(d.get("tip")).strip().lower()
    if kind == "s":
        return Student(fio, mail, phone, text_of(d.get("gruppa")))
    if kind == "t":
        return Teacher(fio, mail, phone, text_of(d.get("kafedra")))
    raise AnketaError("неизвестный тип: " + text_of(d.get("tip")))

def build_registry(anketi):
    """превращает список словарей в журнал. брак - с номером и причиной"""
    registry = Registry()
    registry.total = len(anketi)
    for i, d in enumerate(anketi, 1):
        nomer = d.get("nomer", i) if isinstance(d, dict) else i
        try:
            registry.add(from_dict(d))
        except AnketaError as e:
            who = d.get("fio", "") if isinstance(d, dict) else ""
            registry.bad.append((nomer, text_of(who), str(e)))
    return registry

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

def print_bad(registry, label):
    print("Отклонено:", len(registry.bad))
    for nomer, who, reason in registry.bad:
        print(f"  {label}{nomer} {who}: {reason}")

def print_roles(registry):
    print("По ролям (после проверки):")
    for role, count in sorted(registry.stat_by_role().items()):
        print(f"  {role:<15}{count}")

def print_compare(registry, stat):
    """статистика сервера рядом со своей"""
    mine = registry.stat_by_role()
    theirs = stat.get("po_rolyam", {})
    print(f"{'':<16}{'сервер':>8}{'принято у нас':>16}")
    print(f"{'всего':<16}{stat.get('vsego', '?'):>8}{len(registry):>16}")
    for role in sorted(set(theirs) | set(mine)):
        print(f"{role:<16}{theirs.get(role, 0):>8}{mine.get(role, 0):>16}")
    print("Сервер считает все записи и ничего не проверяет, "
          "поэтому чисел у него больше.")

def check_mails(registry):
    """шлёт почту каждой принятой анкеты на /proverka и возвращает словарь"""
    result = {}
    for p in registry.sorted_people():
        ok = client.proverit_pochtu(p.mail)
        result[p.mail] = ok
        print(f"  {p.mail:<24}{'принята' if ok else 'не принята'}")
    return result

def save_report(registry, source, stat, mails):
    report = {
        "istochnik": source,
        "vsego_zapisey": registry.total,
        "prinyato": len(registry),
        "otkloneno": len(registry.bad),
        "po_rolyam": registry.stat_by_role(),
        "statistika_servera": stat,
        "proverka_pochty": mails,
        "prinyatye": [
            {"fio": p.fio, "rol": p.role(), "mail": p.mail,
             "phone": p.phone, "extra": p.extra()}
            for p in registry.sorted_people()],
        "brak": [
            {"nomer": nomer, "zapis": who, "prichina": reason}
            for nomer, who, reason in registry.bad],
    }
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

def main():
    stat = None
    mails = {}
    try:
        anketi = client.vzyat_anketi()
        source = "сервер " + client.BASE
        registry = build_registry(anketi)
        label = "№"
        print(f"С сервера получено записей: {len(anketi)}")
    except ServerNedostupen as e:
        print("Сервер недоступен:", e)
        print("Переключаюсь на запасной файл:", FALLBACK_FILE)
        registry = Registry()
        if not registry.load(FALLBACK_FILE):
            print(f"Запасного файла {FALLBACK_FILE} тоже нет. "
                  "Данных взять неоткуда, работа завершена.")
            return
        source = "запасной файл " + FALLBACK_FILE
        label = "строка "
        print(f"Из файла прочитано строк: {registry.total} "
              f"(пустых пропущено: {registry.empty})")

    print("Источник данных:", source)
    print()
    print_table(registry)
    print(f"Принято: {len(registry)} | Отклонено: {len(registry.bad)}")
    print()
    print_bad(registry, label)
    print()
    print_roles(registry)

    if source.startswith("сервер"):
        print()
        try:
            stat = client.vzyat_statistiku()
            print("Статистика сервера и наша:")
            print_compare(registry, stat)
        except ServerNedostupen as e:
            print("Статистику получить не удалось:", e)
        print()
        print("Проверка почты на сервере:")
        try:
            mails = check_mails(registry)
        except ServerNedostupen as e:
            print("Проверку почты прервал сбой сервера:", e)

    save_report(registry, source, stat, mails)
    print(f"\nИтог сохранён в {REPORT_FILE}")

if __name__ == "__main__":
    main()
