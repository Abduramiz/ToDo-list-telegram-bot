import telebot
from telebot import types
from config import TOKEN
import json

bot = telebot.TeleBot(TOKEN)
JADVAL = {"dushanba": "Python 15:00", "chorshanba": "Python 15:00", "juma": "Loyiha 15:00"}
SAVOL = ("Python'da ro'yxat qanday belgilanadi?", ["[ ]", "{ }", "( )"], 0)
anketa = {}

def asosiy_menyu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📅 Dars jadvali", "📝 Ro'yxatdan o'tish")
    markup.row("ℹ️ Yordam")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    ism = message.from_user.first_name
    bot.send_message(message.chat.id, f"Salom, <b>{ism}</b>! 👋\nMen <i>Ustudy</i> maktab botiman.\nBuyruqlar: /help",
                     parse_mode="HTML", reply_markup=asosiy_menyu())

@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
def yordam(message):
    bot.reply_to(message, "/start — boshlash\n/jadval — dars jadvali\n/jadval juma — bitta kun\n/royxat — ro'yxatdan o'tish\n/test — mini test")

# ... jadval(), royxat() + ism_qabul() + yosh_qabul(), test() + javob() — yuqoridagi bo'limlardagi kodlar ...

@bot.message_handler(content_types=['photo'])
def rasm(message):
    bot.reply_to(message, "📷 Rasm qabul qilindi! Chiroyli ekan.")

@bot.message_handler(content_types=['sticker'])
def stiker(message):
    bot.send_sticker(message.chat.id, message.sticker.file_id)

@bot.message_handler(content_types=['location'])
def joy(message):
    lat, lon = message.location.latitude, message.location.longitude
    bot.reply_to(message, f"📍 Siz shu yerdasiz: {lat:.4f}, {lon:.4f}")
    bot.send_location(message.chat.id, 41.3111, 69.2797)



@bot.message_handler(commands=['jadval'])
@bot.message_handler(func=lambda m: m.text == "📅 Dars jadvali")
def jadval(message):
    qismlar = message.text.split()                     # "/jadval juma" → ["/jadval", "juma"]
    if message.text.startswith("/") and len(qismlar) > 1:
        kun = qismlar[1].lower()
        bot.reply_to(message, f"{kun}: {JADVAL.get(kun, 'dars yo‘q')}")   # .get — yo'q kun uchun
    else:
        matn = "\n".join(f"{kun} — {dars}" for kun, dars in JADVAL.items())
        bot.reply_to(message, "📅 Dars jadvali:\n" + matn)

@bot.message_handler(commands=['test'])
def test(message):
    savol, variantlar, _ = SAVOL
    markup = types.InlineKeyboardMarkup()
    for i, v in enumerate(variantlar):
        markup.add(types.InlineKeyboardButton(v, callback_data=f"javob_{i}"))   # bosilganda shu matn keladi
    bot.send_message(message.chat.id, "🧠 " + savol, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("javob_"))
def javob(call):
    tanlangan = int(call.data.split("_")[1])
    togri = SAVOL[1][SAVOL[2]]
    if tanlangan == SAVOL[2]:
        bot.answer_callback_query(call.id, "To'g'ri! 🎉")                 # kichik popup
        bot.edit_message_text(f"✅ To'g'ri! Ro'yxat — {togri}",
                              call.message.chat.id, call.message.message_id)  # xabarni O'ZGARTIRADI
    else:
        bot.answer_callback_query(call.id, "Noto'g'ri 😅")
        bot.edit_message_text(f"❌ Noto'g'ri. To'g'ri javob: {togri}",
                              call.message.chat.id, call.message.message_id)

                                 # chat_id → {"ism": ...} — dialog paytida vaqtincha

@bot.message_handler(commands=['royxat'])
@bot.message_handler(func=lambda m: m.text == "📝 Ro'yxatdan o'tish")
def royxat(message):
    msg = bot.send_message(message.chat.id, "Ismingiz?", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, ism_qabul)       # KEYINGI xabar → ism_qabul

def tel_raqam(message):
    msg = bot.send_message(message.chat.id, "telifon raqam?", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, tel_qabul)

def tel_qabul(message):
    anketa[message.chat.id] = {"tel": message.text}
    msg = bot.send_message(message.chat.id, "Yoshingiz?")
    bot.register_next_step_handler(msg, yosh_qabul)

def ism_qabul(message):                                   # dekoratorsiz! faqat next_step orqali
    anketa[message.chat.id] = {"ism": message.text}
    msg = bot.send_message(message.chat.id, "Yoshingiz?")
    bot.register_next_step_handler(msg, yosh_qabul)


def yosh_qabul(message):
    if not message.text.isdigit():
        msg = bot.send_message(message.chat.id, "Son kiriting. Yoshingiz?")
        bot.register_next_step_handler(msg, yosh_qabul)  # yana shu qadam — to'g'ri yozguncha
        return
    a = anketa.pop(message.chat.id)
    a["yosh"] = int(message.text)
    with open("royxat.json", "a", encoding="utf-8") as f:
        f.write(json.dumps({"chat_id": message.chat.id, **a}, ensure_ascii=False) + "\n")
    bot.send_message(message.chat.id, f"✅ Rahmat, {a['ism']} {a['telifon']}! Ro'yxatga olindingiz.",
                                      reply_markup=asosiy_menyu())

@bot.message_handler(func=lambda m: True)                   # ENG OXIRIDA
def boshqa(message):
    bot.reply_to(message, "Tushunmadim 🤔 /help yoki tugmalardan foydalaning")

bot.infinity_polling()