"""Частотный словарь слов в файле — упрощённый вариант проекта из ПР5."""


def chastota(filename):
    """Читает файл и возвращает словарь: слово -> сколько раз встретилось."""
    f = open(filename, "r", encoding="utf-8")
    text = f.read()
    f.close()

    stat = {}
    for word in text.lower().split():
        word = word.strip(".,!?;:()\"'")
        if word == "":
            continue
        stat[word] = stat.get(word, 0) + 1
    return stat
