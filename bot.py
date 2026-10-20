import telebot
from config import TOKEN
import json

bot = telebot.TeleBot(TOKEN)

# Har bir foydalanuvchining alohida vazifalar ro'yxati
royxatlar = {}




def royxat(message):
    with open("telegram_bot.json", 'w') as t:
        json.dump(royxatlar, t, indent=4)
    return royxatlar.setdefault(message.chat.id, [])


@bot.message_handler(commands=["start", "help"])
def start(message):
    matn = (
        "📝 ToDo Bot\n\n"
        "/add matn — vazifa qo'shish\n"
        "/list — vazifalarni ko'rish\n"
        "/done 0 — vazifani bajarilgan qilish\n"
        "/del 0 — vazifani o'chirish"
    )
    bot.reply_to(message, matn)


@bot.message_handler(commands=["add"])
def add(message):
    matn = message.text.partition(" ")[2].strip()

    if not matn:
        bot.reply_to(message, "Format: /add Dars qilish")
        return

    r = royxat(message)
    r.append({"matn": matn, "bajarildi": False})

    idx = len(r) - 1
    bot.reply_to(message, f"✅ #{idx} qo'shildi: {matn}")


@bot.message_handler(commands=["list"])
def royxatni_korsat(message):
    r = royxat(message)

    if not r:
        bot.reply_to(message, "📭 Ro'yxat bo'sh. /add bilan vazifa qo'shing.")
        return

    qatorlar = []


    for i, vazifa in enumerate(r):
        belgi = "✅" if vazifa["bajarildi"] else "⬜"
        qatorlar.append(f"#{i} {belgi} {vazifa['matn']}")


    bot.reply_to(message, "\n".join(qatorlar))



@bot.message_handler(commands=["done"])
def done(message):
    qismlar = message.text.split(maxsplit=1)

    if len(qismlar) != 2 or not qismlar[1].isdigit():
        bot.reply_to(message, "Format: /done 0")
        return

    idx = int(qismlar[1])
    r = royxat(message)

    if idx >= len(r):
        bot.reply_to(message, "❌ Bunday raqamli vazifa topilmadi.")
        return

    if r[idx]["bajarildi"]:
        bot.reply_to(message, "Bu vazifa allaqachon bajarilgan ✅")
        return

    r[idx]["bajarildi"] = True
    bot.reply_to(message, f"✅ #{idx} bajarildi!")


@bot.message_handler(commands=["del"])
def delete(message):
    qismlar = message.text.split(maxsplit=1)

    if len(qismlar) != 2 or not qismlar[1].isdigit():
        bot.reply_to(message, "Format: /del 0")
        return

    idx = int(qismlar[1])
    r = royxat(message)

    if idx >= len(r):
        bot.reply_to(message, "❌ Bunday raqamli vazifa topilmadi.")
        return

    ochirilgan = r.pop(idx)
    bot.reply_to(
        message,
        f"🗑 O'chirildi: {ochirilgan['matn']}"
    )


@bot.message_handler(func=lambda message: True)
def boshqa(message):
    bot.reply_to(message, "Tushunmadim 🤔 Buyruqlar uchun /help yozing.")




if __name__ == "__main__":
    print("Bot ishga tushdi!")
    bot.infinity_polling()
