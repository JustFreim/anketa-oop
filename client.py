#модуль запросов
import requests

BASE = "http://127.0.0.1:5000"
TIMEOUT = 3 #без таймаута программа однажды повиснет

class ServerNedostupen(Exception):
    """сервер не отвечает или сломался"""

def _zapros(metod, adres, **kwargs):
    """единственное место, где вызывается requests"""
    try:
        r = requests.request(metod, BASE + adres, timeout=TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError as e:
        raise ServerNedostupen("сервер не отвечает - он запущен?") from e
    except requests.exceptions.Timeout as e:
        raise ServerNedostupen(
            f"сервер не ответил за {TIMEOUT} с") from e
    if r.status_code >= 500:
        raise ServerNedostupen(f"ошибка на стороне сервера: {r.status_code}")
    return r

def _razobrat(r):
    """достаёт JSON из ответа. Если пришло что то другое - ServerNedostupen"""
    try:
        return r.json()
    except ValueError as e:
        raise ServerNedostupen("сервер прислал не JSON") from e

def vzyat_anketi():
    """все анкеты"""
    r = _zapros("GET", "/anketi")
    if r.status_code != 200:
        raise ServerNedostupen(f"неожиданный ответ сервера: {r.status_code}")
    data = _razobrat(r)
    if not isinstance(data, list):
        raise ServerNedostupen("сервер прислал не список анкет")
    return data

def vzyat_anketu(nomer):
    """одна анкета по номеру. Если такой нет - None"""
    r = _zapros("GET", f"/anketi/{nomer}")
    if r.status_code == 404:
        return None
    if r.status_code != 200:
        raise ServerNedostupen(f"неожиданный ответ сервера: {r.status_code}")
    return _razobrat(r)

def proverit_pochtu(mail):
    """отправляет почту на /proverka; True - сервер принял, False - нет"""
    r = _zapros("POST", "/proverka", json={"mail": mail})
    if r.status_code not in (200, 201):
        raise ServerNedostupen(f"неожиданный ответ сервера: {r.status_code}")
    return _razobrat(r).get("prinyato") is True

def vzyat_statistiku():
    """статистика сервера"""
    r = _zapros("GET", "/statistika")
    if r.status_code != 200:
        raise ServerNedostupen(f"неожиданный ответ сервера: {r.status_code}")
    return _razobrat(r)