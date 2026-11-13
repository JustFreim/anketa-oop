import requests

BASE = "http://127.0.0.1:5000"

#H1
r = requests.get(BASE + "/")
print("код ответа:", r.status_code)
print("тип r.text:", type(r.text))
print("тип r.json():", type(r.json()))
print("название сервиса:", r.json()["servis"])
#H2
r = requests.get(BASE + "/anketi")
anketi = r.json()
print("пришло анкет:", len(anketi))
print("ФИО первой:", anketi[0]["fio"])
#H3
r = requests.get(BASE + "/anketi/99")
print("код ответа:", r.status_code)
print("r.ok:", r.ok)
if r.status_code == 404:
    print("сервер ответил:", r.json()["oshibka"])
#H4
r = requests.get(BASE + "/anketi", params={"tip": "t"})
print("адрес запроса:", r.url)
for a in r.json():
    print(a["fio"], "-", a["kafedra"])
#H5
for mail in ["ivanov@mail.ru", "kuznetsov.mail.ru"]:
    r = requests.post(BASE + "/proverka", json={"mail": mail})
    print(mail, "| код:", r.status_code, "| prinyato:", r.json()["prinyato"])
