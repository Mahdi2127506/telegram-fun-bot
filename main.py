import asyncio
import random
import os
import requests
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot import types

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = AsyncTeleBot(BOT_TOKEN)

def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("سنگ کاغذ قیچی", callback_data="menu_rps"),
        types.InlineKeyboardButton("فال حافظ", callback_data="menu_fal"),
        types.InlineKeyboardButton("جوک", callback_data="menu_joke"),
    )
    return kb

def rps_menu():
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("سنگ", callback_data="rps_rock"),
        types.InlineKeyboardButton("کاغذ", callback_data="rps_paper"),
        types.InlineKeyboardButton("قیچی", callback_data="rps_scissors"),
    )
    kb.add(types.InlineKeyboardButton("بازگشت", callback_data="back_main"))
    return kb

@bot.message_handler(commands=["start", "menu"])
async def start_cmd(message):
    await bot.reply_to(
        message,
        "سلام! من ربات سرگرمی هستم.\nاز منوی زیر یک گزینه انتخاب کن:",
        reply_markup=main_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data == "menu_rps")
async def rps_start(call):
    await bot.edit_message_text(
        "بازی سنگ کاغذ قیچی! انتخاب کن:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=rps_menu()
    )
    await bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("rps_"))
async def rps_play(call):
    user_choice = call.data.split("_")[1]
    bot_choice = random.choice(["rock", "paper", "scissors"])

    if user_choice == bot_choice:
        result = "مساوی"
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "paper" and bot_choice == "rock") or \
         (user_choice == "scissors" and bot_choice == "paper"):
        result = "تو بردی"
    else:
        result = "من بردم"

    choice_map = {"rock": "سنگ", "paper": "کاغذ", "scissors": "قیچی"}
    text = (
        f"انتخاب تو: {choice_map[user_choice]}\n"
        f"انتخاب من: {choice_map[bot_choice]}\n\n"
        f"نتیجه: {result}"
    )
    await bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=rps_menu()
    )
    await bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "menu_fal")
async def fal_start(call):
    await bot.edit_message_text(
        "در حال گرفتن فال...",
        call.message.chat.id,
        call.message.message_id
    )
    await bot.answer_callback_query(call.id)

    url = "https://api.codebazan.ir/fal/?type=json"
    try:
        res = requests.get(url, timeout=15)
        data = res.json()
        if data.get("Ok"):
            poem = data.get("Result1", "").strip()
            meaning = data.get("Result", "").strip()
            text = f"فال حافظ:\n\n{poem}\n\nتعبیر:\n{meaning}"
            if len(text) > 4000:
                text = text[:3990] + "..."
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("بازگشت", callback_data="back_main"))
            await bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=kb
            )
        else:
            await bot.edit_message_text(
                "خطا در دریافت فال.",
                call.message.chat.id,
                call.message.message_id
            )
    except Exception:
        await bot.edit_message_text(
            "در حال حاضر سرور فال پاسخ نمی‌دهد.",
            call.message.chat.id,
            call.message.message_id
        )

@bot.callback_query_handler(func=lambda call: call.data == "menu_joke")
async def joke_start(call):
    await bot.edit_message_text(
        "در حال گرفتن جوک...",
        call.message.chat.id,
        call.message.message_id
    )
    await bot.answer_callback_query(call.id)

    url = "http://api.codebazan.ir/jok/pa-na-pa"
    try:
        res = requests.get(url, timeout=15)
        joke = res.text.strip()
        if joke:
            kb = types.InlineKeyboardMarkup(row_width=1)
            kb.add(
                types.InlineKeyboardButton("جوک بعدی", callback_data="menu_joke"),
                types.InlineKeyboardButton("بازگشت", callback_data="back_main"),
            )
            await bot.edit_message_text(
                f"جوک:\n\n{joke}",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=kb
            )
        else:
            await bot.edit_message_text(
                "جوکی پیدا نشد.",
                call.message.chat.id,
                call.message.message_id
            )
    except Exception:
        await bot.edit_message_text(
            "در حال حاضر سرور جوک پاسخ نمی‌دهد.",
            call.message.chat.id,
            call.message.message_id
        )

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
async def back_main(call):
    await bot.edit_message_text(
        "منوی اصلی:\nیک گزینه انتخاب کن:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=main_menu()
    )
    await bot.answer_callback_query(call.id)

async def main():
    print("ربات روشن شد...")
    await bot.polling()

if __name__ == "__main__":
    asyncio.run(main())
