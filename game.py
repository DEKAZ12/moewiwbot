import random, time
import database as db

def profile_text(p):
    w = "🗡️ ندارد" if p['weapon'] == 0 else f"🗡️ لول {p['weapon']}"
    a = "🛡️ ندارد" if p['armor'] == 0 else f"🛡️ لول {p['armor']}"
    pet = "🐶 ندارد" if p['pet'] == 0 else "🐶 دارد"
    return (f"🐱 پروفایل {p['first_name']}\n━━━━━━━━━━\n"
            f"💰 پول: {p['money']:,} | 🏦 بانک: {p['bank']:,}\n"
            f"⭐ لول: {p['level']} | ✨ XP: {p['xp']}\n"
            f"⚡ انرژی: {p['energy']}/100\n"
            f"{w} | {a} | {pet}\n"
            f"💍 همسر: {'داره' if p['spouse_id'] else 'نداره'}")

def do_meow(p):
    now = int(time.time())
    if now - p['last_meow'] < 180: return f"⏱ {180 - (now - p['last_meow'])} ثانیه صبر کن."
    db.update_player(p['user_id'], last_meow=now)
    db.add_money(p['user_id'], 20)
    return f"🐶 هاپ! +۲۰ دلار."

def do_daily(p):
    now = int(time.time())
    if now - p['last_daily'] < 86400: return "⏱ تا فردا صبر کن."
    db.update_player(p['user_id'], last_daily=now, energy=100)
    db.add_money(p['user_id'], 300)
    return "🎁 جایزه روزانه: +۳۰۰ دلار و انرژی پر شد!"

def do_work(p):
    now = int(time.time())
    if p['energy'] < 20: return "😴 انرژی نداری! بنویس «خواب»."
    if now - p['last_work'] < 60: return f"⏱ {60 - (now - p['last_work'])} ثانیه صبر کن."
    earn = random.randint(20, 150)
    db.update_player(p['user_id'], last_work=now, energy=p['energy']-20)
    db.add_money(p['user_id'], earn)
    return f"💼 کار کردی! +{earn} دلار."

def do_sleep(p):
    now = int(time.time())
    if now - p['last_sleep'] < 300: return f"⏱ {300 - (now - p['last_sleep'])} ثانیه دیگه بیدار شو."
    db.update_player(p['user_id'], last_sleep=now, energy=100)
    return "😴 خوابیدی و انرژی پر شد!"

def do_bank(p):
    if p['money'] < 100: return "💸 حداقل ۱۰۰ دلار داری."
    amt = p['money'] // 2
    db.update_player(p['user_id'], money=p['money']-amt, bank=p['bank']+amt)
    return f"🏦 {amt} دلار به بانک منتقل شد."

def do_rob_bank(p):
    now = int(time.time())
    if p['energy'] < 50: return "😴 انرژی کمه! بنویس «خواب»."
    if now - p['last_steal'] < 300: return "🚔 پلیس بیداره! بعدا بیا."
    db.update_player(p['user_id'], last_steal=now, energy=p['energy']-50)
    if random.random() < 0.3:
        db.add_money(p['user_id'], 500)
        return "🏦 سرقت از بانک موفق! +۵۰۰ دلار."
    db.add_money(p['user_id'], -200)
    return "🚔 گیر افتادی! -۲۰۰ دلار."

def do_dice(p):
    if p['money'] < 50: return "💸 حداقل ۵۰ دلار."
    db.add_money(p['user_id'], -50)
    if random.randint(1, 6) > 3:
        db.add_money(p['user_id'], 100)
        return "🎲 بردی! +۱۰۰ دلار."
    return "🎲 باختی! -۵۰ دلار."

def do_shop(p):
    return ("🛒 فروشگاه:\n"
            "بزن «خرید شمشیر» (۵۰۰ دلار) - دزدی راحت‌تر\n"
            "بزن «خرید زره» (۵۰۰ دلار) - دزدی ازت سخت‌تر\n"
            "بزن «خرید سگ» (۱۰۰۰ دلار) - درآمد پسیو")

def buy_item(p, item):
    costs = {"شمشیر": 500, "زره": 500, "سگ": 1000}
    if item not in costs: return "❓ آیتم نیست."
    if p['money'] < costs[item]: return "💸 پول کافی نداری."
    db.add_money(p['user_id'], -costs[item])
    if item == "شمشیر": db.update_player(p['user_id'], weapon=p['weapon']+1)
    elif item == "زره": db.update_player(p['user_id'], armor=p['armor']+1)
    elif item == "سگ": db.update_player(p['user_id'], pet=1)
    return f"✅ {item} خریداری شد!"

def do_steal(p, victim_id, victim_name):
    now = int(time.time())
    if now - p['last_steal'] < 120: return "⏱ پلیس گشت می‌زنه."
    if p['energy'] < 30: return "😴 انرژی نداری!"
    db.update_player(p['user_id'], last_steal=now, energy=p['energy']-30)
    victim = db.get_player(victim_id)
    if not victim or victim['money'] < 50: return "🥷 پولی نداره!"
    
    chance = 0.4 + (p['weapon'] * 0.1) - (victim['armor'] * 0.1)
    if random.random() < chance:
        amount = min(victim['money'] // 4, 300)
        db.add_money(victim_id, -amount)
        db.add_money(p['user_id'], amount)
        return f"🥷 از {victim_name} دزدی کردی! +{amount} دلار."
    db.add_money(p['user_id'], -100)
    return f"🚔 گیر افتادی! -۱۰۰ دلار."

def do_marry(p, target_id, target_name):
    if p['spouse_id']: return "💍 همسر داری!"
    target = db.get_player(target_id)
    if not target or target['spouse_id']: return "❌ امکان‌پذیر نیست."
    db.update_player(p['user_id'], spouse_id=target_id)
    db.update_player(target_id, spouse_id=p['user_id'])
    return f"💍 {p['first_name']} و {target_name} ازدواج کردن!"

def do_gift(p, target_name):
    if p['money'] < 50: return "💸 پول کمه."
    db.add_money(p['user_id'], -50)
    return f"🎁 کادو دادی به {target_name}!"

def do_restaurant(p):
    if p['money'] < 100: return "💸 پول کمه."
    db.add_money(p['user_id'], -100)
    db.update_player(p['user_id'], energy=min(100, p['energy']+50))
    return "🍔 خوردی! +۵۰ انرژی."