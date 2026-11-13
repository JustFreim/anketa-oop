from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.json.ensure_ascii = False #чтобы кириллица в js была читаемой

SPISOK = ["Иванов Иван", "Петров Пётр", "Сидорова Анна"]

@app.route("/")
def glavnaya():
    return "Учебное приложение работает"

@app.route("/privet/<imya>")
def privet(imya):
    return "Здравствуйте, " + imya + "!"

@app.route("/kvadrat/<int:chislo>")
def kvadrat(chislo):
    return f"{chislo} в квадрате = {chislo * chislo}"

@app.route("/spisok")
def spisok():
    return jsonify(SPISOK)

@app.route("/spisok/dlina")
def dlina():
    return jsonify({"dlina": len(SPISOK)})

@app.route("/spisok/<int:nomer>")
def odin(nomer):
    if nomer < 1 or nomer > len(SPISOK):
        return jsonify({"oshibka": "нет такого номера"}), 404
    return jsonify({"nomer": nomer, "fio": SPISOK[nomer - 1]})

@app.route("/dobavit", methods=["POST"])
def dobavit():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"oshibka": "ожидался JSON с полем fio"}), 400
    fio = str(data.get("fio", "")).strip()
    if fio == "":
        return jsonify({"oshibka": "ожидалось поле fio"}), 400
    SPISOK.append(fio)
    return jsonify({"dobavleno": fio}), 201

@app.route("/stranica")
def stranica():
    return render_template("razminka/spisok.html", spisok=SPISOK)

if __name__ == "__main__":
    app.run(port=5000)
