import sqlite3
from config import DATABASE_PATH, ADMIN_IDS

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
        money INTEGER DEFAULT 100, bank INTEGER DEFAULT 0, level INTEGER DEFAULT 1, xp INTEGER DEFAULT 0,
        spouse_id INTEGER DEFAULT 0, energy INTEGER DEFAULT 100, weapon INTEGER DEFAULT 0, armor INTEGER DEFAULT 0,
        pet INTEGER DEFAULT 0, last_work INTEGER DEFAULT 0, last_steal INTEGER DEFAULT 0, 
        last_trade INTEGER DEFAULT 0, last_meow INTEGER DEFAULT 0, last_daily INTEGER DEFAULT 0, last_sleep INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

KEYS = ['user_id','username','first_name','money','bank','level','xp','spouse_id','energy','weapon','armor','pet','last_work','last_steal','last_trade','last_meow','last_daily','last_sleep','is_admin']

def get_player(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(zip(KEYS, row)) if row else None

def create_player(user_id, username, first_name):
    is_admin = 1 if user_id in ADMIN_IDS else 0
    money = 999_999_999 if is_admin else 100
    level = 999 if is_admin else 1
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO players (user_id, username, first_name, money, level, is_admin) 
                 VALUES (?,?,?,?,?,?)''', (user_id, username or "", first_name or "", money, level, is_admin))
    conn.commit()
    conn.close()

def update_player(user_id, **kwargs):
    if not kwargs: return
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute(f"UPDATE players SET {fields} WHERE user_id = ?", values)
    conn.commit()
    conn.close()

def add_money(user_id, amount):
    p = get_player(user_id)
    if not p or p['is_admin']: return
    update_player(user_id, money=max(0, p['money'] + amount))