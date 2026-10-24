import json
FAYL = "users.json"

def yukla():                                   # fayl → lug'at
    try:
        with open(FAYL, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:                   # birinchi marta — fayl hali yo'q
        return {}

def saqla(users):                              # lug'at → fayl (butunlay qayta yoziladi)
    with open(FAYL, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)   # o'zbekcha harflar + chiroyli

def user_saqla(chat_id, ism, yosh, til):
    users = yukla()
    users[str(chat_id)] = {"ism": ism, "yosh": yosh, "til": til}   # bor bo'lsa — yangilanadi
    saqla(users)

def user_ol(chat_id):
    return yukla().get(str(chat_id))         # {"ism": "Ali", ...}  yoki  None

def jami():
    return len(yukla())

def til_boyicha():                             # {"uz": 2, "ru": 1}
    hisob = {}
    for u in yukla().values():
        hisob[u["til"]] = hisob.get(u["til"], 0) + 1
    return hisob

def user_ochir(chat_id):
    users = yukla()
    users.pop(str(chat_id), None)              # yo'q bo'lsa ham xato bermaydi
    saqla(users)