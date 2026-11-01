import logging, os, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
import database as db
import game

logging.basicConfig(level=logging.INFO)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not db.get_player(u.id): db.create_player(u.id, u.username, u.first_name)
    await update.message.reply_text(
        f"🐱 خوش اومدی {u.first_name}!\n\n"
        "🔹 دستورات:\n"
        "میو / هاپ (پول) | منو | کار | خواب | روزانه\n"
        "بانک | سرقت بانک | تاس | فروشگاه\n"
        "خرید شمشیر | خرید زره | خرید سگ | رستوران\n\n"
        "🔸 روی پیام طرف ریپلای کن و بنویس:\n"
        "دزدی | ازدواج | کادو"
    )

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    text = update.message.text.lower().strip()
    
    if not db.get_player(u.id): db.create_player(u.id, u.username, u.first_name)
    p = db.get_player(u.id)
    
    if text in ["میو", "هاپ"]: await update.message.reply_text(game.do_meow(p))
    elif text in ["منو", "پروفایل"]: await update.message.reply_text(game.profile_text(p))
    elif text == "کار": await update.message.reply_text(game.do_work(p))
    elif text == "خواب": await update.message.reply_text(game.do_sleep(p))
    elif text == "روزانه": await update.message.reply_text(game.do_daily(p))
    elif text == "بانک": await update.message.reply_text(game.do_bank(p))
    elif text == "سرقت بانک": await update.message.reply_text(game.do_rob_bank(p))
    elif text == "تاس": await update.message.reply_text(game.do_dice(p))
    elif text == "فروشگاه": await update.message.reply_text(game.do_shop(p))
    elif text.startswith("خرید "):
        item = text.replace("خرید ", "").strip()
        await update.message.reply_text(game.buy_item(p, item))
    elif text == "رستوران": await update.message.reply_text(game.do_restaurant(p))
    
    elif text in ["دزدی", "ازدواج", "کادو"]:
        if not update.message.reply_to_message:
            await update.message.reply_text(f"⚠️ روی پیام طرف ریپلای کن!")
            return
        target = update.message.reply_to_message.from_user
        if target.id == u.id: return
            
        if text == "دزدی": await update.message.reply_text(game.do_steal(p, target.id, target.first_name))
        elif text == "ازدواج": await update.message.reply_text(game.do_marry(p, target.id, target.first_name))
        elif text == "کادو": await update.message.reply_text(game.do_gift(p, target.first_name))
    else: await update.message.reply_text("❓ متوجه نشدم. بنویس «منو».")

web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is running!"

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()

if __name__ == "__main__":
    db.init_db()
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)