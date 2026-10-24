

import telebot
from telebot import types,custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

import db
from config import TOKEN

bot = telebot.TeleBot(TOKEN, state_storage=StateMemoryStorage())
TILLAR = {"uz": "🇺🇿 O'zbek", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}

class Royxat(StatesGroup):
    ism = State(); yosh = State(); til = State()

def menyu():
    mark = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mark.row("📝 Ro'yxat", "👤 Men")
    mark.row("📊 Statistika", "ℹ️ Yordam")
    return mark

def til_tugmalari():
    mark = types.InlineKeyboardMarkup(row_width=3)
    mark.add(*[types.InlineKeyboardButton(nom, callback_data=f"til_{kod}") for kod, nom in TILLAR.items()])
    return mark

@bot.message_handler(commands=["start"])
def start(message):
    u = db.user_ol(message.chat.id)
    matn = f"Salom, {u['ism']}! Siz ro'yxatdasiz ✅" if u else "Salom! Avval ro'yxatdan o'ting: 📝 Ro'yxat"
    bot.send_message(message.chat.id,matn,reply_markup=menyu())


@bot.message_handler(commands=["royxat"])
@bot.message_handler(func=lambda m: m.text == "📝 Ro'yxat")
def royxat(message):
    bot.set_state(message.from_user.id, Royxat.ism, message.chat.id)
    bot.send_message(message.chat.id, "Ismingiz? (/cancel — bekor qilish)",
                     reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(state=Royxat.ism)
def ism_qabul(message):
    ism = message.text.strip()

    if not ism:
        bot.send_message(message.chat.id, "Ismingizni kiriting:")
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["ism"] = ism

    bot.set_state(message.from_user.id, Royxat.yosh, message.chat.id)
    bot.send_message(message.chat.id, "Yoshingizni kiriting:")


@bot.message_handler(state=Royxat.yosh)
def yosh_qabul(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Son kiriting. Yoshingiz?")
        return

    yosh = int(message.text)

    if not 1 <= yosh <= 120:
        bot.send_message(message.chat.id, "Yosh 1 dan 120 gacha bo'lishi kerak.")
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["yosh"] = yosh

    bot.set_state(message.from_user.id, Royxat.til, message.chat.id)
    bot.send_message(
        message.chat.id,
        "Tilni tanlang:",
        reply_markup=til_tugmalari()
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("til_"), state=Royxat.til)
def til_tanlandi(call):
    til = call.data.split("_")[1]
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        ism, yosh = data["ism"], data["yosh"]
    db.user_saqla(call.message.chat.id, ism, yosh, til)      # 💾 users.json ga
    bot.delete_state(call.from_user.id, call.message.chat.id)  # dialog tugadi
    bot.answer_callback_query(call.id, "Saqlandi ✅")
    bot.edit_message_text(f"Til: {TILLAR[til]}", call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, f"✅ {ism}, {yosh} yosh — saqlandi!", reply_markup=menyu())



@bot.message_handler(state=Royxat.til)                      # til holatida matn yozsa
def til_matn(message):
    bot.send_message(message.chat.id, "Tugmalardan birini bosing 👆 (yoki /cancel)")




# ---------- bazadan o'qish ----------
@bot.message_handler(commands=['men'])
@bot.message_handler(func=lambda m: m.text == "👤 Men")
def men(message):
    u = db.user_ol(message.chat.id)
    if u is None:
        bot.reply_to(message, "Siz hali ro'yxatda yo'qsiz. 📝 Ro'yxat tugmasini bosing")
        return
    bot.reply_to(message, f"👤 {u['ism']}\n🎂 {u['yosh']} yosh\n🌐 {TILLAR.get(u['til'], u['til'])}")


@bot.message_handler(commands=['stat'])
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def stat(message):
    qatorlar = "\n".join(f"{TILLAR.get(t, t)}: {n} ta" for t, n in db.til_boyicha().items())
    bot.reply_to(message, f"👥 Jami: {db.jami()} ta foydalanuvchi\n{qatorlar}")


@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
def yordam(message):
    bot.reply_to(message, "/royxat — ro'yxatdan o'tish (3 qadam)\n/men — mening ma'lumotlarim\n"
                          "/stat — statistika\n/cancel — dialogni bekor qilish")


@bot.message_handler(func=lambda m: True)
def boshqa(message):
    bot.reply_to(message, "Tushunmadim 🤔 /help")

@bot.message_handler(state="*", commands=['cancel'])        # ISTALGAN holatda ishlaydi
def cancel(message):
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, "❌ Bekor qilindi", reply_markup=menyu())

@bot.callback_query_handler(func=lambda c: True)            # eski/boshqa tugmalar — holat mos kelmasa
def eski_tugma(call):
    bot.answer_callback_query(call.id, "Bu tugma eskirgan. /royxat bilan qaytadan boshlang")
if __name__ == "__main__":
    bot.add_custom_filter(custom_filters.StateFilter(bot))   # state= filtrini yoqish — SHART!
    print("Anketa bot ishga tushdi...")
    bot.infinity_polling()



