#сайт обработчика анкет
import os

from flask import (Flask, abort, jsonify, redirect, render_template, request, url_for)
from werkzeug.exceptions import NotFound
from people import AnketaError, Student, Teacher
from registry import Registry

app = Flask(__name__)
app.json.ensure_ascii = False #кириллица в JSON остаётся читаемой

ANKETA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anketa.txt")

#файл читается один раз при старте, дальше все маршруты работают с журналом
zhurnal = Registry()
if not zhurnal.load(ANKETA_FILE):
    print("ВНИМАНИЕ: файл не найден, журнал пуст")

#помощники
def tekst(value):
    """значение из запроса как строка"""
    if value is None:
        return ""
    return str(value)

def sozdat_anketu(tip, fio, mail, phone, dopolnenie):
    """по типу создаёт Student или Teacher"""
    tip = tip.strip().lower()
    if tip == "s":
        return Student(fio, mail, phone, dopolnenie)
    if tip == "t":
        return Teacher(fio, mail, phone, dopolnenie)
    raise AnketaError("неизвестный тип анкеты: " + (tip or "не указан"))

def nomera():
    """номер, анкета в порядке поступления в журнал. Номер - место анкеты в журнале, а не в отсортированном списке, поэтому после добавления новых анкет старые номера не меняются"""
    return list(enumerate(zhurnal.people, 1))

def naiti(nomer):
    """анкета по номеру или None"""
    if 1 <= nomer <= len(zhurnal.people):
        return zhurnal.people[nomer - 1]
    return None

def v_slovar(nomer, p):
    """анкета в виде словаря для json"""
    student = p.group_name() is not None
    d = {"nomer": nomer, "tip": "s" if student else "t", "rol": p.role(),
         "fio": p.fio, "mail": p.mail, "phone": p.phone}
    d["gruppa" if student else "kafedra"] = p.extra()
    return d

def dlya_stranitsy(nomer, p):
    """то же, но с полями, нужными шаблонам"""
    d = v_slovar(nomer, p)
    d["extra"] = p.extra()
    d["gruppa"] = p.group_name()
    d["maska"] = p.masked_phone()
    return d

def alfavit(pary):
    """номер, анкета - словари для страницы, по алфавиту"""
    return [dlya_stranitsy(n, p) for n, p in sorted(pary, key=lambda t: t[1])]

#страницы
@app.route("/")
def index():
    return render_template("index.html", anketi=alfavit(nomera()),
                           gruppa=None, prinyato=len(zhurnal),
                           otkloneno=len(zhurnal.bad))

@app.route("/anketi/<int:nomer>")
def odna_anketa(nomer):
    p = naiti(nomer)
    if p is None:
        abort(404, description=f"Анкеты с номером {nomer} нет.")
    return render_template("anketa.html", a=dlya_stranitsy(nomer, p))

@app.route("/gruppa/<nazvanie>")
def gruppa_stranitsa(nazvanie):
    nazv = nazvanie.strip().lower()
    pary = [(n, p) for n, p in nomera() if p.group_name() == nazv]
    return render_template("index.html", anketi=alfavit(pary),
                           gruppa=nazvanie, prinyato=len(zhurnal),
                           otkloneno=len(zhurnal.bad))

@app.route("/statistika")
def statistika():
    return render_template(
        "statistika.html",
        prinyato=len(zhurnal), otkloneno=len(zhurnal.bad),
        vsego=zhurnal.total, pustyh=zhurnal.empty,
        po_rolyam=sorted(zhurnal.stat_by_role().items()),
        po_gruppam=sorted(zhurnal.stat_by_group().items()),
        brak=zhurnal.bad)

@app.route("/dobavit", methods=["GET", "POST"])
def forma_dobavleniya():
    if request.method == "GET":
        bylo = {"tip": "s", "fio": "", "mail": "", "phone": "",
                "dopolnenie": ""}
        return render_template("dobavit.html", bylo=bylo, oshibka=None)
    # сюда попадаем только при POST
    bylo = {pole: request.form.get(pole, "")
            for pole in ("tip", "fio", "mail", "phone", "dopolnenie")}
    try:
        p = sozdat_anketu(bylo["tip"], bylo["fio"], bylo["mail"],
                          bylo["phone"], bylo["dopolnenie"])
    except AnketaError as e:
        return render_template("dobavit.html", bylo=bylo,
                               oshibka=str(e)), 400
    zhurnal.add(p)
    return redirect(url_for("odna_anketa", nomer=len(zhurnal)))

#JSON
@app.route("/api/anketi")
def api_spisok():
    rol = request.args.get("rol")       # None, если не передали
    anketi = [v_slovar(n, p) for n, p in nomera()]
    if rol is not None:
        anketi = [d for d in anketi if d["rol"] == rol.strip().lower()]
    return jsonify(anketi)

@app.route("/api/anketi/<int:nomer>")
def api_odna(nomer):
    p = naiti(nomer)
    if p is None:
        abort(404, description=f"Анкеты с номером {nomer} нет.")
    return jsonify(v_slovar(nomer, p))

@app.route("/api/statistika")
def api_statistika():
    return jsonify({
        "prinyato": len(zhurnal),
        "otkloneno": len(zhurnal.bad),
        "vsego_strok": zhurnal.total,
        "pustyh_strok": zhurnal.empty,
        "po_rolyam": zhurnal.stat_by_role(),
        "po_gruppam": zhurnal.stat_by_group(),
    })

@app.route("/api/brak")
def api_brak():
    return jsonify([{"nomer": num, "tekst": line, "prichina": reason}
                    for num, line, reason in zhurnal.bad])

@app.route("/api/anketi", methods=["POST"])
def api_dobavit():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"oshibka": "ожидался JSON-объект с полями анкеты"}), 400
    tip = tekst(data.get("tip")).strip().lower()
    pole = "gruppa" if tip == "s" else "kafedra"
    try:
        p = sozdat_anketu(tip, tekst(data.get("fio")), tekst(data.get("mail")),
                          tekst(data.get("phone")), tekst(data.get(pole)))
    except AnketaError as e:
        return jsonify({"oshibka": str(e)}), 400
    zhurnal.add(p)
    return jsonify(v_slovar(len(zhurnal), p)), 201

#ошибки
@app.errorhandler(404)
def ne_naydeno(e):
    opisanie = e.description
    if opisanie == NotFound.description: #стандартный английский текст
        opisanie = "Такого адреса нет."
    if request.path.startswith("/api/"):
        return jsonify({"oshibka": opisanie}), 404
    return render_template("oshibka.html", soobshchenie=opisanie), 404

if __name__ == "__main__":
    app.run(port=5000)
