import requests, json, time, random, string, os, sys, traceback, threading, gc
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify

# ═══════════════════════════════════════
# 🔧 تنظیمات
# ═══════════════════════════════════════
TOKEN = "886012408:V6CU51uMQU59W86Dq4MM44wlU6rON5zl39M"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"

CHANNEL_ID = "@SCYVu"
CHANNEL_LINK = "https://ble.ir/SCYVu"
BOT_USERNAME = "Idneobot"
BOT_LINK = f"https://ble.ir/{BOT_USERNAME.replace('@', '')}"

OWNER_ID = "1530477937"
OWNER_PASSWORD = "Parsa@2026!"
COIN_PASSWORD = "Coin@Parsa2026"
INFINITE_COINS = 999999
MIN_SIN = 15
MIN_MEMBER = 1
MEMBER_COST = 5
START_GIFT = 25
SEEN_REWARD = 1
SIN_COST = 1
INVITE_REWARD = 15
DAILY_GIFT = 5
MEMBER_NORMAL_REWARD = 3
MEMBER_GUARANTEED_REWARD = 7

DB_FILE = "sinzen_ultra_strong.json"
RENDER_URL = "https://guard-bot-2-cl22.onrender.com"
START_TIME = datetime.now()

# ═══════════════════════════════════════
# 🛡️ ۶ محافظ
# ═══════════════════════════════════════
class ErrorGuard:
    def __init__(self):
        self.fix_count = 0; self.last_error = None; self.total_errors = 0
    def protect(self, func, *args, **kwargs):
        try: return func(*args, **kwargs)
        except Exception as e:
            self.fix_count += 1; self.total_errors += 1
            self.last_error = str(e)[:100]
            gc.collect(); time.sleep(0.001); return None

class Watchdog:
    def __init__(self):
        self.restart_count = 0; self.start_time = datetime.now()

class VPNGuard:
    def __init__(self):
        self.ok = False; self.retry_count = 0

class ServerGuard:
    def __init__(self):
        self.backup_count = 0; self.power = "۵۰۰ میلیون تومان"
    def protect(self):
        gc.collect()
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f: data = f.read()
            with open(f"{DB_FILE}.backup", 'w', encoding='utf-8') as f: f.write(data)
            with open(f"{DB_FILE}.backup2", 'w', encoding='utf-8') as f: f.write(data)
            self.backup_count += 1
        except: pass
        return True

class NetGuard:
    def __init__(self):
        self.retry_count = 0; self.is_connected = False

class ProxyGuard:
    def __init__(self):
        self.ok = False; self.mode = "auto"

error_guard = ErrorGuard()
watchdog = Watchdog()
vpn_guard = VPNGuard()
server_guard = ServerGuard()
net_guard = NetGuard()
proxy_guard = ProxyGuard()

# ═══════════════════════════════════════
# 📅 تاریخ شمسی
# ═══════════════════════════════════════
def get_shamsi_date():
    now = datetime.now()
    gy, gm, gd = now.year, now.month, now.day
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053)); days %= 12053
    jy += 4 * (days // 1461); days %= 1461
    if days > 365:
        jy += (days - 1) // 365; days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31; jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30; jd = 1 + (days - 186) % 30
    return f"{jy}/{jm:02d}/{jd:02d}"

# ═══════════════════════════════════════
# 🗄️ دیتابیس
# ═══════════════════════════════════════
def load_db():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except: pass
    return {
        "users": {}, "orders": {}, "member_orders": {}, "gift_codes": {},
        "seen_records": {}, "member_records": {}, "invited_users": {}, "used_ips": {},
        "order_counter": 0, "member_counter": 0,
        "stats": {"total_orders": 0, "completed_orders": 0, "deleted_messages": 0, "total_members": 0, "completed_members": 0},
        "stats_advanced": {"users_today": 0, "new_users": 0, "active_users": 0, "coins_distributed": 0, "coins_spent": 0, "orders_created": 0, "orders_completed": 0},
        "pending_orders": {}, "pending_members": {}, "pending_gift": {}, "pending_broadcast": {},
        "pending_add_coins": {}, "pending_transfer": {}, "pending_coin_setting": {},
        "pending_join_channel": {}, "pending_remove_join": {},
        "pending_packet": {}, "pending_packet_user": {},
        "pending_ban": {}, "pending_unban": {}, "pending_admin": {}, "pending_remove_admin": {},
        "pending_vip": {}, "pending_pm": {}, "pending_execute": {}, "pending_utility": {},
        "invite_reward": INVITE_REWARD, "guaranteed_members": {}, "punished_users": [],
        "coin_packets": {}, "banned": [], "admins": [], "vip": {},
        "join_channels": [], "order_channels": [],
        "support_messages": {},
        "settings": {"seen_reward": SEEN_REWARD, "sin_cost": SIN_COST, "member_cost": MEMBER_COST, "member_normal_reward": MEMBER_NORMAL_REWARD, "member_guaranteed_reward": MEMBER_GUARANTEED_REWARD}
    }

CACHE = {}; CACHE_TIME = {}; CACHE_TTL = 120
SAVE_PENDING = False; SAVE_LOCK = threading.Lock()

def get_user_cached(user_id):
    uid = str(user_id); now = time.time()
    if uid in CACHE and now - CACHE_TIME.get(uid, 0) < CACHE_TTL:
        return CACHE[uid]
    user = db["users"].get(uid)
    if not user:
        user = {"coins": 0, "joined": False, "got_start_gift": False, "total_orders": 0, "completed_orders": 0, "used_gift_codes": [], "username": "", "invite_code": None, "invite_count": 0, "invited_by": None, "first_seen": str(datetime.now()), "last_seen": str(datetime.now()), "last_daily": None, "msg_count": 0}
        db["users"][uid] = user
    CACHE[uid] = user; CACHE_TIME[uid] = now
    return user

def get_user(user_id): return get_user_cached(user_id)

def add_coins(user_id, amount):
    user = get_user(user_id)
    user["coins"] += amount
    db["stats_advanced"]["coins_distributed"] += amount
    save_db_async()

def remove_coins(user_id, amount):
    user = get_user(user_id)
    if user["coins"] >= amount:
        user["coins"] -= amount
        db["stats_advanced"]["coins_spent"] += amount
        save_db_async(); return True
    return False

def get_coins(user_id): return get_user(user_id)["coins"]

def save_db_async():
    global SAVE_PENDING; SAVE_PENDING = True

def save_worker():
    global SAVE_PENDING
    while True:
        if SAVE_PENDING:
            with SAVE_LOCK:
                try:
                    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False)
                    with open(f"{DB_FILE}.backup", "w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False)
                    SAVE_PENDING = False
                except: pass
        time.sleep(3)

def save_db(data=None): save_db_async()

db = load_db()

def is_banned(user_id): return str(user_id) in db.get("banned", [])
def is_admin(user_id): return str(user_id) == OWNER_ID or str(user_id) in db.get("admins", [])
def is_owner(user_id): return str(user_id) == OWNER_ID

def is_vip(user_id):
    uid = str(user_id)
    if uid in db.get("vip", {}):
        exp = datetime.fromisoformat(db["vip"][uid]["exp"])
        if datetime.now() < exp: return True
        else:
            del db["vip"][uid]; save_db_async()
    return False

def get_vip_multiplier(user_id): return 2 if is_vip(user_id) else 1
def get_setting(key, default=0): return db.get("settings", {}).get(key, default)
def is_punished(user_id, order_id): return f"{user_id}_{order_id}" in db["punished_users"]
def mark_punished(user_id, order_id):
    key = f"{user_id}_{order_id}"
    if key not in db["punished_users"]:
        db["punished_users"].append(key); save_db_async()
def is_order_owner(user_id, order_id): return db["member_orders"].get(order_id, {}).get("user_id") == str(user_id)
def is_48h_passed(join_time_str):
    if not join_time_str: return False
    return datetime.now() >= datetime.fromisoformat(join_time_str) + timedelta(hours=48)

# ═══════════════════════════════════════
# 📡 API
# ═══════════════════════════════════════
session = requests.Session()
session.headers.update({'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate'})
executor = ThreadPoolExecutor(max_workers=100)

def api_call(method, data=None, timeout=5):
    try:
        if data is None: data = {}
        r = session.post(f"{BASE_URL}/{method}", data=data, timeout=timeout)
        return r.json()
    except:
        try:
            r = session.post(f"{BASE_URL}/{method}", data=data, timeout=3)
            return r.json()
        except: return {"ok": False}

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup: data["reply_markup"] = json.dumps(reply_markup)
    return api_call("sendMessage", data)

def send_reply(chat_id, reply_to_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_id}
    if reply_markup: data["reply_markup"] = json.dumps(reply_markup)
    return api_call("sendMessage", data)

def edit_message_text(chat_id, message_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if reply_markup: data["reply_markup"] = json.dumps(reply_markup)
    return api_call("editMessageText", data)

def delete_message(chat_id, message_id): return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
def forward_message(chat_id, from_chat_id, message_id): return api_call("forwardMessage", {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id})

def answer_callback(callback_id, text=None, show_alert=False):
    data = {"callback_query_id": callback_id}
    if text: data["text"] = text
    data["show_alert"] = show_alert
    return api_call("answerCallbackQuery", data)

def get_chat_member(chat_id, user_id): return api_call("getChatMember", {"chat_id": chat_id, "user_id": user_id})
def get_chat(chat_id): return api_call("getChat", {"chat_id": chat_id})

def check_joined(user_id):
    try:
        result = get_chat_member(CHANNEL_ID, user_id)
        if result.get("ok"):
            status = result["result"]["status"]
            if status in ["member", "administrator", "creator"]:
                get_user(user_id)["joined"] = True; save_db_async(); return True
        return False
    except: return False

def check_all_joins(user_id):
    if not check_joined(user_id): return False
    for ch in db.get("join_channels", []):
        try:
            result = get_chat_member(ch, user_id)
            if not result.get("ok"): return False
            status = result["result"]["status"]
            if status not in ["member", "administrator", "creator"]: return False
        except: return False
    return True

def must_join(user_id):
    keyboard = {"inline_keyboard": [[{"text": "🔗 عضویت در کانال", "url": CHANNEL_LINK}], [{"text": "✅ عضو شدم", "callback_data": "check_join"}]]}
    send_message(user_id, "🔒 **برای استفاده از ربات باید عضو کانال بشی!**\n\nلطفاً عضو شو بعد روی «عضو شدم» بزن.", keyboard)
    return False

# ═══════════════════════════════════════
# 🎮 کیبوردها
# ═══════════════════════════════════════
def main_keyboard(user_id=None):
    rows = [
        [{"text": "🪙 کسب سکه"}],
        [{"text": "👁️ ثبت سفارش سین"}, {"text": "👥 ثبت سفارش عضو"}],
        [{"text": "💰 سکه‌های من"}, {"text": "🎁 زدن کد هدیه"}],
        [{"text": "👥 دعوت دوستان"}, {"text": "👤 حساب کاربری"}],
        [{"text": "💰 انتقال سکه"}, {"text": "🎁 هدیه روزانه"}],
        [{"text": "💬 پشتیبانی"}],
        [{"text": "📖 راهنما"}]
    ]
    if user_id and str(user_id) == OWNER_ID:
        rows.append([{"text": "👑 پنل مالک"}])
    return {"keyboard": rows, "resize_keyboard": True}

def owner_keyboard():
    return {
        "keyboard": [
            [{"text": "⚙️ تنظیم سکه"}, {"text": "🔗 کاربردی‌ها"}],
            [{"text": "🚫 مسدود کردن"}, {"text": "✅ رفع مسدودیت"}],
            [{"text": "👑 افزودن ادمین"}, {"text": "🗑️ حذف ادمین"}],
            [{"text": "📨 پیام به کاربر"}, {"text": "💻 اجرای کد"}],
            [{"text": "🎁 سکه پاکت"}, {"text": "🎁 پاکت به کاربر"}],
            [{"text": "⭐ ویژه VIP"}, {"text": "🛡️ ضدتقلب"}],
            [{"text": "📊 آمار پیشرفته"}, {"text": "📊 آمار کل"}],
            [{"text": "🔒 جوین اجباری"}, {"text": "🎁 ساخت کد هدیه"}],
            [{"text": "💰 افزودن سکه به همه"}, {"text": "🎁 تغییر سکه دعوت"}],
            [{"text": "📢 پیام همگانی"}, {"text": "🏆 رتبه‌بندی"}],
            [{"text": "🔙 بازگشت"}]
        ],
        "resize_keyboard": True
    }

def settings_keyboard():
    return {
        "keyboard": [
            [{"text": "👁️ سکه دیدم"}],
            [{"text": "📝 سکه سفارش سین"}],
            [{"text": "👥 سکه سفارش عضو"}],
            [{"text": "🪙 سکه عضو معمولی"}],
            [{"text": "🛡️ سکه عضو تضمینی"}],
            [{"text": "🔙 بازگشت"}]
        ],
        "resize_keyboard": True
    }

def cancel_keyboard():
    return {"keyboard": [[{"text": "🔙 بازگشت"}]], "resize_keyboard": True}

def convert_number(text):
    for p, e in zip("۰۱۲۳۴۵۶۷۸۹", "0123456789"):
        text = text.replace(p, e)
    return text

def broadcast_worker(user_id, text):
    sent = 0; failed = 0
    all_users = list(db["users"].keys())
    total = len(all_users)
    for i, uid in enumerate(all_users, 1):
        try:
            result = send_message(int(uid), text)
            if result.get("ok"): sent += 1
            else: failed += 1
        except: failed += 1
        time.sleep(2)
        if i % 10 == 0:
            try: send_message(user_id, f"📊 پیشرفت: {i}/{total}")
            except: pass
    send_message(user_id, f"📢 **ارسال کامل شد!**\n\n✅ موفق: {sent}\n❌ ناموفق: {failed}\n📊 کل: {total}", owner_keyboard())

def keep_alive():
    while True:
        try:
            time.sleep(240)
            requests.get(f"{RENDER_URL}/ping", timeout=15)
            print(f"💓 پینگ | {datetime.now().strftime('%H:%M:%S')}")
        except: time.sleep(60)

# ═══════════════════════════════════════
# 🎯 پردازش پیام
# ═══════════════════════════════════════
def handle_message(message):
    global INVITE_REWARD
    try:
        chat_id = message["chat"]["id"]
        chat_type = message["chat"]["type"]
        
        if chat_type in ["group", "supergroup"]:
            if "new_chat_member" in message:
                new_member = message["new_chat_member"]
                new_name = new_member.get("first_name", "کاربر")
                group_name = message["chat"].get("title", "این گروه")
                welcome_text = (
                    f"👋 **{new_name}** به **{group_name}** خوش اومدی! 🎉\n\n"
                    f"🤖 من **ربات عضوگیر و سین‌زن** هستم!\n"
                    f"👥 می‌تونم برات عضو بیارم\n"
                    f"👁️ می‌تونم برات سین بزنم\n\n"
                    f"🚀 اگه خواستی کانال یا گروهت رو رشد بدی،\n"
                    f"بیا توی پیوی من:\n"
                    f"🤖 @Idneobot\n\n"
                    f"🐺 تیم DeepParse"
                )
                send_message(chat_id, welcome_text)
            return
        
        if chat_type == "channel": return
        
        user_id = str(message["from"]["id"])
        text = message.get("text", "").strip()
        name = message["from"].get("first_name", "داداش")
        
        if is_banned(user_id):
            send_message(chat_id, "🚫 دسترسی شما مسدود شد!\n\n⏳ نگران نباش؛ ممکنه تا چند ساعت دیگه رفع بشه.")
            return
        
        username = message["from"].get("username", "")
        if username:
            get_user(user_id)["username"] = username
            save_db_async()
        
        get_user(user_id)["msg_count"] = get_user(user_id).get("msg_count", 0) + 1
        
        sup = db.get("support_messages", {}).get(user_id, {})
        if sup.get("step") == "waiting":
            try:
                send_message(int(OWNER_ID), f"💬 **پیام پشتیبانی**\n\n👤 از: {name}\n🆔 آیدی: {user_id}\n\n📝 پیام:\n{text}")
                send_message(chat_id, "✅ پیامت برای پشتیبانی ارسال شد!\n\n💚 به زودی جواب می‌گیری.")
            except: send_message(chat_id, "❌ خطا در ارسال!")
            del db["support_messages"][user_id]; save_db_async(); return
        
        if text.startswith("/start"):
            parts = text.split(" ")
            if len(parts) > 1:
                inviter_id = parts[1]
                if inviter_id != user_id and user_id not in db["invited_users"]:
                    db["invited_users"][user_id] = inviter_id
                    u = get_user(user_id); u["invited_by"] = inviter_id
                    save_db_async()
                    try:
                        send_message(int(inviter_id), f"🔔 **یه کاربر با لینک دعوت تو اومد!**\n\n👤 کاربر: {name}\n⏰ منتظر عضویت در کانال...\n\n💡 وقتی عضو بشه، **{INVITE_REWARD} سکه** بهت اهدا میشه!")
                    except: pass
            if not check_all_joins(user_id):
                must_join(user_id); return
            user = get_user(user_id)
            if not user.get("got_start_gift"):
                add_coins(user_id, START_GIFT)
                user["got_start_gift"] = True
                if user.get("invited_by") and user_id in db["invited_users"]:
                    inviter_id = user["invited_by"]
                    vip_mult = get_vip_multiplier(inviter_id)
                    add_coins(inviter_id, INVITE_REWARD * vip_mult)
                    inviter = get_user(inviter_id)
                    inviter["invite_count"] = inviter.get("invite_count", 0) + 1
                    save_db_async()
                    try:
                        send_message(int(inviter_id), f"🎉 **کاربر عضو کانال هم شد!**\n\n👤 کاربر: {name}\n✅ با لینک دعوت تو اومد\n✅ عضو کانال هم شد\n\n🎁 **{INVITE_REWARD * vip_mult} سکه بهت اهدا شد!** 💰\n💰 موجودی: {get_coins(inviter_id):,} سکه")
                    except: pass
                save_db_async()
                send_message(chat_id, f"👋 **سلام {name} جان!** 😎\n\n⚡ به هایپرسین خوش اومدی!\n🎁 **{START_GIFT} سکه هدیه** بهت اضافه شد!\n💰 موجودی: {get_coins(user_id):,} سکه\n\nاز دکمه‌های زیر استفاده کن:", main_keyboard(user_id))
            else:
                send_message(chat_id, f"👋 **سلام {name} جان!** 😎\n\nاز دکمه‌های زیر استفاده کن:", main_keyboard(user_id))
            return
        
        main_buttons = ["🪙 کسب سکه", "👁️ ثبت سفارش سین", "👥 ثبت سفارش عضو", "💰 سکه‌های من", "🎁 زدن کد هدیه", "👥 دعوت دوستان", "👤 حساب کاربری", "💰 انتقال سکه", "🎁 هدیه روزانه", "💬 پشتیبانی", "📖 راهنما"]
        if text in main_buttons:
            if not check_all_joins(user_id):
                must_join(user_id); return
        
        if text in ["❌ لغو", "🔙 بازگشت"]:
            for key in ["pending_orders", "pending_members", "pending_gift", "pending_transfer", "pending_packet", "pending_coin_setting", "pending_ban", "pending_unban", "pending_admin", "pending_remove_admin", "pending_vip", "pending_pm", "pending_execute", "pending_utility", "pending_join_channel", "pending_remove_join", "pending_packet_user", "support_messages"]:
                db.get(key, {}).pop(user_id, None)
            save_db_async()
            send_message(chat_id, "🔙 **برگشتی به منوی اصلی!**", main_keyboard(user_id))
            return
        
        if text == OWNER_PASSWORD and user_id == OWNER_ID:
            send_message(chat_id, "👑 **پنل مالک باز شد!** 🚀\nیکی از گزینه‌ها رو انتخاب کن:", owner_keyboard())
            return
        
        if text == COIN_PASSWORD:
            add_coins(user_id, INFINITE_COINS)
            send_message(chat_id, f"💰 **{INFINITE_COINS:,} سکه بهت اضافه شد!** 🎉\n💳 موجودی: {get_coins(user_id):,} سکه")
            return
        
        if text == "👑 پنل مالک" and user_id == OWNER_ID:
            send_message(chat_id, "👑 **پنل مالک** 🚀\nیکی از گزینه‌ها رو انتخاب کن:", owner_keyboard())
            return
        
        if text == "🪙 کسب سکه":
            keyboard = {"inline_keyboard": [[{"text": "👁️ برو به کانال", "url": CHANNEL_LINK}]]}
            send_message(chat_id, f"🔗 **برو توی کانال و روی دکمه «دیدم» زیر پیام‌ها بزن تا سکه بگیری!** 💰\n\n{CHANNEL_LINK}", keyboard)
            return
        
        if text == "💰 سکه‌های من":
            send_message(chat_id, f"💰 **موجودی تو:** {get_coins(user_id):,} سکه 🪙")
            return
        
        if text == "📖 راهنما":
            help_text = (
                f"📖 **راهنمای ربات هایپرسین ⚡**\n\n"
                f"🤖 هایپرسین ترکیبی از ربات سین‌زن و عضوگیر است.\n\n"
                f"👁️ **بخش سین‌زن**\n• هر سین = 🪙 ۱ سکه لازم است\n• حداقل سفارش: ۱۵ سین\n\n"
                f"👥 **بخش عضوگیر**\n• هر عضو = 🪙 ۵ سکه لازم دارد\n• حداقل سفارش: ۱ عضو\n\n"
                f"💰 **انتقال سکه:**\n• دکمه انتقال سکه رو بزن\n• آیدی عددی طرف رو بفرست\n• (از حساب کاربری → کپی آیدی)\n• مقدار سکه رو وارد کن\n\n"
                f"💰 **روش‌های کسب سکه در کانال**\n• 👁️ دکمه «دیدم» رو بزن در کانال → +۱ سکه\n• 👥 دکمه «عضو شدم» رو بزن در کانال → +۳ سکه\n• 🎁 کد هدیه → دریافت سکه جایزه\n• 🎉 اولین عضویت در کانال ما → ۲۵ سکه هدیه\n• 👥 دعوت دوستان → هر دعوت = {INVITE_REWARD} سکه\n\n"
                f"⚠️ **قوانین**\n• پیام های غیر قانونی ثبت نمیشه و شما از کانال حذف میشید\n\n"
                f"✨ از استفاده از هایپرسین سپاسگزاریم."
            )
            send_message(chat_id, help_text)
            return
        
        if text == "👤 حساب کاربری":
            u = get_user(user_id)
            send_message(chat_id, f"👤 **حساب کاربری:**\n\n👤 نام: {name}\n🆔 آیدی: {user_id}\n📛 یوزرنیم: @{u['username'] if u['username'] else 'ندارد'}\n🪙 موجودی: {u['coins']:,} سکه\n👥 دعوت کرده: {u.get('invite_count', 0)} نفر", {"inline_keyboard": [[{"text": "📋 کپی آیدی عددی", "callback_data": "copy_id"}], [{"text": "🔙 بازگشت", "callback_data": "back_to_main"}]]})
            return
        
        if text == "👥 دعوت دوستان":
            vip_mult = get_vip_multiplier(user_id)
            send_message(chat_id, f"👥 **دعوت دوستان:**\n\n🔗 لینک اختصاصی تو:\nhttps://ble.ir/{BOT_USERNAME}?start={user_id}\n\n🎁 **هر دعوت = {INVITE_REWARD * vip_mult} سکه** 💰\n\n👥 تا حالا: {get_user(user_id).get('invite_count', 0)} نفر دعوت کردی")
            return
        
        if text == "💰 انتقال سکه":
            db["pending_transfer"][user_id] = {"step": "waiting_id"}; save_db_async()
            send_message(chat_id, "🆔 **آیدی عددی کاربر مقصد رو بفرست:**", cancel_keyboard())
            return
        
        if text == "👁️ ثبت سفارش سین":
            db["pending_orders"][user_id] = {"step": "waiting_forward"}; save_db_async()
            send_message(chat_id, "📩 **لطفاً پیام مورد نظر را از کانال فوروارد کنید.**\n\n⚠️ حتماً باید از کانال فوروارد شود!\n📢 از هر کانالی می‌تونی فوروارد کنی.", cancel_keyboard())
            return
        
        if text == "👥 ثبت سفارش عضو":
            db["pending_members"][user_id] = {"step": "waiting_link"}; save_db_async()
            send_message(chat_id, "📩 **لطفاً لینک کانال مورد نظر را بفرستید.**\n\n⚠️ حتماً باید کانال باشد!\n🚫 گروه قبول نمیشود!", cancel_keyboard())
            return
        
        if text == "🎁 زدن کد هدیه":
            db["pending_orders"][user_id] = {"step": "waiting_gift_code"}; save_db_async()
            send_message(chat_id, "🎁 **لطفاً کد هدیه رو وارد کن:**", cancel_keyboard())
            return
        
        if text == "🎁 هدیه روزانه":
            user = get_user(user_id); now = datetime.now()
            last = user.get("last_daily")
            if last:
                last_time = datetime.fromisoformat(last)
                if now - last_time < timedelta(hours=24):
                    remaining = timedelta(hours=24) - (now - last_time)
                    h = remaining.seconds // 3600; m = (remaining.seconds % 3600) // 60
                    send_message(chat_id, f"⏰ {h} ساعت و {m} دقیقه دیگه بیا!")
                    return
            vip_mult = get_vip_multiplier(user_id)
            add_coins(user_id, DAILY_GIFT * vip_mult)
            user["last_daily"] = str(now); save_db_async()
            send_message(chat_id, f"🎁 **هدیه روزانه گرفتی!**\n\n🪙 +{DAILY_GIFT * vip_mult} سکه\n💰 موجودی: {get_coins(user_id):,} سکه")
            return
        
        if text == "💬 پشتیبانی":
            db["support_messages"][user_id] = {"step": "waiting"}; save_db_async()
            send_message(chat_id, "💬 **پشتیبانی**\n\nلطفاً پیامت رو بفرست تا کمکت کنیم!", cancel_keyboard())
            return
        
        # ═══ پنل مالک ═══
        if text == "⚙️ تنظیم سکه" and is_admin(user_id):
            send_message(chat_id, "⚙️ **تنظیم سکه**\n\nیکی رو انتخاب کن:", settings_keyboard())
            return
        if text == "👁️ سکه دیدم" and is_admin(user_id):
            db["pending_coin_setting"][user_id] = {"type": "seen_reward"}; save_db_async()
            send_message(chat_id, f"👁️ سکه فعلی: {get_setting('seen_reward', 1)}\n\nسکه جدید:", settings_keyboard())
            return
        if text == "📝 سکه سفارش سین" and is_admin(user_id):
            db["pending_coin_setting"][user_id] = {"type": "sin_cost"}; save_db_async()
            send_message(chat_id, f"📝 هزینه فعلی: {get_setting('sin_cost', 1)}\n\nهزینه جدید:", settings_keyboard())
            return
        if text == "👥 سکه سفارش عضو" and is_admin(user_id):
            db["pending_coin_setting"][user_id] = {"type": "member_cost"}; save_db_async()
            send_message(chat_id, f"👥 هزینه فعلی: {get_setting('member_cost', 5)}\n\nهزینه جدید:", settings_keyboard())
            return
        if text == "🪙 سکه عضو معمولی" and is_admin(user_id):
            db["pending_coin_setting"][user_id] = {"type": "member_normal_reward"}; save_db_async()
            send_message(chat_id, f"🪙 پاداش فعلی: {get_setting('member_normal_reward', 3)}\n\nپاداش جدید:", settings_keyboard())
            return
        if text == "🛡️ سکه عضو تضمینی" and is_admin(user_id):
            db["pending_coin_setting"][user_id] = {"type": "member_guaranteed_reward"}; save_db_async()
            send_message(chat_id, f"🛡️ پاداش فعلی: {get_setting('member_guaranteed_reward', 7)}\n\nپاداش جدید:", settings_keyboard())
            return
        
        pcs = db["pending_coin_setting"].get(user_id, {})
        if pcs.get("type"):
            try:
                val = int(convert_number(text))
                db["settings"][pcs["type"]] = val
                del db["pending_coin_setting"][user_id]; save_db_async()
                send_message(chat_id, f"✅ ذخیره شد: {val}", owner_keyboard())
            except: send_message(chat_id, "❌ عدد معتبر بفرست!", settings_keyboard())
            return
        
        if text == "🔗 کاربردی‌ها" and is_admin(user_id):
            db["pending_utility"][user_id] = {"step": "text"}; save_db_async()
            send_message(chat_id, "🔗 **متن دکمه:**", cancel_keyboard())
            return
        if text == "🚫 مسدود کردن" and is_admin(user_id):
            db["pending_ban"][user_id] = {"step": "waiting_id"}; save_db_async()
            send_message(chat_id, "🚫 آیدی عددی کاربر:", cancel_keyboard())
            return
        if text == "✅ رفع مسدودیت" and is_admin(user_id):
            db["pending_unban"][user_id] = {"step": "waiting_id"}; save_db_async()
            send_message(chat_id, "✅ آیدی عددی:", cancel_keyboard())
            return
        if text == "👑 افزودن ادمین" and user_id == OWNER_ID:
            db["pending_admin"][user_id] = {"step": "waiting_id"}; save_db_async()
            send_message(chat_id, "👑 آیدی عددی:", cancel_keyboard())
            return
        if text == "🗑️ حذف ادمین" and user_id == OWNER_ID:
            db["pending_remove_admin"][user_id] = {"step": "waiting_id"}; save_db_async()
            send_message(chat_id, "🗑️ آیدی عددی:", cancel_keyboard())
            return
        if text == "📨 پیام به کاربر" and is_admin(user_id):
            db["pending_pm"][user_id] = {"step": "waiting_id"}; save_db_async()
            send_message(chat_id, "📨 آیدی عددی:", cancel_keyboard())
            return
        if text == "💻 اجرای کد" and is_admin(user_id):
            db["pending_execute"][user_id] = {"step": "waiting_code"}; save_db_async()
            send_message(chat_id, "💻 کد پایتون رو بفرست:", cancel_keyboard())
            return
        if text == "🎁 سکه پاکت" and is_admin(user_id):
            db["pending_packet"][user_id] = {"step": "waiting_coins"}; save_db_async()
            send_message(chat_id, "💰 چند سکه توی پاکت باشه؟", owner_keyboard())
            return
        if text == "🎁 پاکت به کاربر" and is_admin(user_id):
            db["pending_packet_user"][user_id] = {"step": "waiting_id"}; save_db_async()
            send_message(chat_id, "🆔 آیدی عددی:", cancel_keyboard())
            return
        if text == "⭐ ویژه VIP" and is_admin(user_id):
            db["pending_vip"][user_id] = {"step": "waiting_duration"}; save_db_async()
            send_message(chat_id, "⭐ مدت (12h / 7d / 1m):", cancel_keyboard())
            return
        if text == "🛡️ ضدتقلب" and is_admin(user_id):
            keyboard = {"inline_keyboard": [
                [{"text": "🚨 موارد مشکوک", "callback_data": "suspicious_cases"}],
                [{"text": "📊 گزارش امروز", "callback_data": "today_report"}],
                [{"text": "🔒 یوزرنیم‌ها", "callback_data": "suspicious_usernames"}],
                [{"text": "📜 لاگ تاریخچه", "callback_data": "antifraud_log"}]
            ]}
            send_message(chat_id, "🛡️ **ضدتقلب**", keyboard)
            return
        if text == "📊 آمار پیشرفته" and is_admin(user_id):
            sa = db["stats_advanced"]
            send_message(chat_id, f"📊 **آمار پیشرفته**\n\n👥 کاربران امروز: {sa['users_today']}\n🆕 کاربران جدید: {sa['new_users']}\n✅ کاربران فعال: {sa['active_users']}\n💰 سکه توزیع: {sa['coins_distributed']:,}\n💸 سکه مصرف: {sa['coins_spent']:,}\n📝 سفارش ثبت: {sa['orders_created']}\n✅ سفارش تکمیل: {sa['orders_completed']}\n📅 تاریخ: {get_shamsi_date()}\n⏰ ساعت: {datetime.now().strftime('%H:%M:%S')}", owner_keyboard())
            return
        if text == "📊 آمار کل" and is_admin(user_id):
            stats = db["stats"]
            send_message(chat_id, f"📊 **آمار کلی ربات:**\n\n👥 کاربران کل: {len(db['users'])}\n✅ عضو کانال: {sum(1 for u in db['users'].values() if u.get('joined'))}\n📝 سفارشات سین: {stats['total_orders']}\n🔄 فعال سین: {stats['total_orders'] - stats['completed_orders']}\n✅ تکمیل سین: {stats['completed_orders']}\n👥 سفارشات عضو: {stats.get('total_members', 0)}\n✅ تکمیل عضو: {stats.get('completed_members', 0)}\n🗑️ حذف شده: {stats['deleted_messages']}\n📅 تاریخ: {get_shamsi_date()}\n⏰ ساعت: {datetime.now().strftime('%H:%M:%S')}", owner_keyboard())
            return
        if text == "🔒 جوین اجباری" and is_admin(user_id):
            keyboard = {"inline_keyboard": [
                [{"text": "➕ افزودن کانال", "callback_data": "add_join_channel"}],
                [{"text": "🗑️ حذف کانال", "callback_data": "remove_join_channel"}],
                [{"text": "📋 لیست", "callback_data": "list_join_channels"}]
            ]}
            send_message(chat_id, "🔒 **جوین اجباری**", keyboard)
            return
        if text == "🎁 ساخت کد هدیه" and is_admin(user_id):
            db["pending_gift"][user_id] = {"step": "waiting_coins"}; save_db_async()
            send_message(chat_id, "💰 چند سکه توی کد باشه؟", owner_keyboard())
            return
        if text == "💰 افزودن سکه به همه" and is_admin(user_id):
            db["pending_add_coins"][user_id] = {"step": "waiting_amount"}; save_db_async()
            send_message(chat_id, "💰 چند سکه به همه؟", owner_keyboard())
            return
        if text == "🎁 تغییر سکه دعوت" and is_admin(user_id):
            db["pending_gift"][user_id] = {"step": "waiting_invite_reward"}; save_db_async()
            send_message(chat_id, f"🎁 سکه فعلی: {INVITE_REWARD}\n\nسکه جدید:", owner_keyboard())
            return
        if text == "📢 پیام همگانی" and is_admin(user_id):
            db["pending_broadcast"][user_id] = {"step": "waiting_message"}; save_db_async()
            send_message(chat_id, "📢 متن:", owner_keyboard())
            return
        if text == "🏆 رتبه‌بندی" and is_admin(user_id):
            users_sorted = sorted(db["users"].items(), key=lambda x: x[1]["coins"], reverse=True)[:10]
            msg = "🏆 **رتبه‌بندی کاربران:**\n\n"
            for i, (uid, data) in enumerate(users_sorted, 1):
                uname = data.get("username", "")
                if uname: msg += f"{i}. @{uname} → {data['coins']:,} سکه\n"
                else: msg += f"{i}. کاربر {uid[:6]}... → {data['coins']:,} سکه\n"
            send_message(chat_id, msg, owner_keyboard())
            return
        
        # ═══ pending ها ═══
        pu = db["pending_utility"].get(user_id, {})
        if pu.get("step") == "text":
            db["pending_utility"][user_id] = {"step": "link", "text": text}; save_db_async()
            send_message(chat_id, "🔗 **لینک:**", cancel_keyboard()); return
        if pu.get("step") == "link":
            keyboard = {"inline_keyboard": [[{"text": pu["text"], "url": text}]]}
            send_message(CHANNEL_ID, "🔗 **دکمه کاربردی**", keyboard)
            del db["pending_utility"][user_id]; save_db_async()
            send_message(chat_id, "✅ تو کانال گذاشته شد!", owner_keyboard()); return
        
        pb = db["pending_ban"].get(user_id, {})
        if pb.get("step") == "waiting_id":
            uid = text.strip()
            db.setdefault("banned", []).append(uid)
            del db["pending_ban"][user_id]; save_db_async()
            send_message(chat_id, f"🚫 کاربر {uid} مسدود شد!", owner_keyboard())
            try: send_message(int(uid), "🚫 دسترسی شما مسدود شد!\n\n⏳ نگران نباش؛ ممکنه تا چند ساعت دیگه رفع بشه.")
            except: pass
            return
        
        pu2 = db["pending_unban"].get(user_id, {})
        if pu2.get("step") == "waiting_id":
            uid = text.strip()
            if uid in db.get("banned", []):
                db["banned"].remove(uid); del db["pending_unban"][user_id]; save_db_async()
                send_message(chat_id, f"✅ کاربر {uid} آزاد شد!", owner_keyboard())
                try: send_message(int(uid), "🎉 مژده! مسدودی شما برداشته شد.\n\n✅ دوباره می‌تونی از ربات استفاده کنی!")
                except: pass
            else:
                send_message(chat_id, "❌ مسدود نبود!", owner_keyboard())
                del db["pending_unban"][user_id]; save_db_async()
            return
        
        pa = db["pending_admin"].get(user_id, {})
        if pa.get("step") == "waiting_id":
            uid = text.strip()
            if uid not in db.get("admins", []): db["admins"].append(uid)
            del db["pending_admin"][user_id]; save_db_async()
            send_message(chat_id, f"👑 ادمین شد!", owner_keyboard())
            try: send_message(int(uid), "👑 شما ادمین شدید!\n\nپنل مالک برات فعال شد.", owner_keyboard())
            except: pass
            return
        
        pra = db["pending_remove_admin"].get(user_id, {})
        if pra.get("step") == "waiting_id":
            uid = text.strip()
            if uid in db.get("admins", []):
                db["admins"].remove(uid); save_db_async()
                send_message(chat_id, "🗑️ حذف شد!", owner_keyboard())
                try: send_message(int(uid), "🗑️ پنل مالک ازت گرفته شد!", main_keyboard())
                except: pass
            else: send_message(chat_id, "❌ ادمین نبود!", owner_keyboard())
            del db["pending_remove_admin"][user_id]; save_db_async(); return
        
        ppm = db["pending_pm"].get(user_id, {})
        if ppm.get("step") == "waiting_id":
            db["pending_pm"][user_id] = {"step": "waiting_text", "id": text.strip()}; save_db_async()
            send_message(chat_id, "📝 متن:", cancel_keyboard()); return
        if ppm.get("step") == "waiting_text":
            uid = ppm["id"]
            try:
                send_message(int(uid), text); send_message(chat_id, "✅ ارسال شد!", owner_keyboard())
            except: send_message(chat_id, "❌ خطا!", owner_keyboard())
            del db["pending_pm"][user_id]; save_db_async(); return
        
        # ═══ اجرای کد ═══
        pe = db["pending_execute"].get(user_id, {})
        if pe.get("step") == "waiting_code":
            try:
                exec_globals = {'db': db, 'send_message': send_message, 'get_user': get_user, 'add_coins': add_coins, 'remove_coins': remove_coins, 'get_coins': get_coins, 'OWNER_ID': OWNER_ID, 'CHANNEL_ID': CHANNEL_ID, 'time': time, 'datetime': datetime, 'random': random, 'json': json}
                result = eval(text.strip(), exec_globals)
                send_message(chat_id, f"✅ **نتیجه اجرا:**\n\n`{result}`", owner_keyboard())
            except Exception as e:
                send_message(chat_id, f"❌ **خطا در اجرا:**\n\n`{str(e)[:200]}`", owner_keyboard())
            del db["pending_execute"][user_id]; save_db_async(); return
        
        pp = db["pending_packet"].get(user_id, {})
        if pp.get("step") == "waiting_coins":
            try:
                db["pending_packet"][user_id] = {"step": "waiting_capacity", "coins": int(convert_number(text))}; save_db_async()
                send_message(chat_id, "👥 چند نفره باشه؟", owner_keyboard())
            except: send_message(chat_id, "❌ عدد معتبر!", owner_keyboard())
            return
        if pp.get("step") == "waiting_capacity":
            try:
                db["pending_packet"][user_id]["step"] = "waiting_text"
                db["pending_packet"][user_id]["capacity"] = int(convert_number(text)); save_db_async()
                send_message(chat_id, "📝 متن پاکت:", owner_keyboard())
            except: send_message(chat_id, "❌ عدد معتبر!", owner_keyboard())
            return
        if pp.get("step") == "waiting_text":
            packet_id = str(int(time.time() * 1000))
            db["coin_packets"][packet_id] = {"coins": pp["coins"], "capacity": pp["capacity"], "text": text.strip(), "used_by": []}
            kb = {"inline_keyboard": [[{"text": "🎁 باز کردن سکه", "callback_data": f"packet_{packet_id}"}]]}
            send_message(CHANNEL_ID, f"🎁 **سکه پاکت**\n\n{text.strip()}", kb)
            db["pending_packet"].pop(user_id, None); save_db_async()
            send_message(chat_id, "✅ سکه پاکت تو کانال گذاشته شد!", owner_keyboard()); return
        
        ppu = db["pending_packet_user"].get(user_id, {})
        if ppu.get("step") == "waiting_id":
            db["pending_packet_user"][user_id] = {"step": "waiting_coins", "id": text.strip()}; save_db_async()
            send_message(chat_id, "💰 چند سکه؟", cancel_keyboard()); return
        if ppu.get("step") == "waiting_coins":
            try:
                db["pending_packet_user"][user_id]["step"] = "waiting_text"
                db["pending_packet_user"][user_id]["coins"] = int(convert_number(text)); save_db_async()
                send_message(chat_id, "📝 متن:", cancel_keyboard())
            except: send_message(chat_id, "❌ عدد معتبر!", cancel_keyboard())
            return
        if ppu.get("step") == "waiting_text":
            uid = ppu["id"]; coins = ppu["coins"]
            packet_id = str(int(time.time() * 1000))
            db["coin_packets"][packet_id] = {"coins": coins, "capacity": 1, "text": text, "used_by": [], "target": uid}
            kb = {"inline_keyboard": [[{"text": "🎁 باز کردن سکه", "callback_data": f"userpacket_{packet_id}"}]]}
            try:
                send_message(int(uid), f"🎁 **پاکت هدیه!**\n\n{text}", kb)
                send_message(chat_id, "✅ ارسال شد!", owner_keyboard())
            except: send_message(chat_id, "❌ خطا!", owner_keyboard())
            del db["pending_packet_user"][user_id]; save_db_async(); return
        
        pv = db["pending_vip"].get(user_id, {})
        if pv.get("step") == "waiting_duration":
            db["pending_vip"][user_id] = {"step": "waiting_id", "duration": text.strip()}; save_db_async()
            send_message(chat_id, "🆔 آیدی عددی:", cancel_keyboard()); return
        if pv.get("step") == "waiting_id":
            uid = text.strip(); duration = pv["duration"]
            try:
                now = datetime.now()
                if duration.endswith("h"): exp = now + timedelta(hours=int(duration[:-1]))
                elif duration.endswith("d"): exp = now + timedelta(days=int(duration[:-1]))
                elif duration.endswith("m"): exp = now + timedelta(days=int(duration[:-1]) * 30)
                else:
                    send_message(chat_id, "❌ فرمت اشتباه!", owner_keyboard())
                    del db["pending_vip"][user_id]; save_db_async(); return
                db.setdefault("vip", {})[uid] = {"exp": str(exp)}; save_db_async()
                send_message(chat_id, f"⭐ VIP شد تا {exp.strftime('%Y-%m-%d %H:%M')}", owner_keyboard())
                try: send_message(int(uid), f"⭐ **VIP شدی!**\n\n💰 ۲ برابر سکه\n📅 تا {exp.strftime('%Y-%m-%d %H:%M')}")
                except: pass
            except: send_message(chat_id, "❌ خطا!", owner_keyboard())
            del db["pending_vip"][user_id]; save_db_async(); return
        
        pg = db["pending_gift"].get(user_id, {})
        if pg.get("step") == "waiting_coins":
            try:
                db["pending_gift"][user_id] = {"step": "waiting_capacity", "coins": int(convert_number(text))}; save_db_async()
                send_message(chat_id, "👥 ظرفیت چند نفره؟", owner_keyboard())
            except: send_message(chat_id, "❌ عدد معتبر!", owner_keyboard())
            return
        if pg.get("step") == "waiting_capacity":
            try:
                cap = int(convert_number(text))
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                db["gift_codes"][code] = {"coins": pg["coins"], "capacity": cap, "used_by": []}
                del db["pending_gift"][user_id]; save_db_async()
                send_message(chat_id, f"🎁 **کد ساخته شد!**\n\n🔑 `{code}`\n💰 {pg['coins']:,} سکه\n👥 {cap} نفر", owner_keyboard())
            except: send_message(chat_id, "❌ عدد معتبر!", owner_keyboard())
            return
        if pg.get("step") == "waiting_invite_reward":
            try:
                INVITE_REWARD = int(convert_number(text))
                db["invite_reward"] = INVITE_REWARD
                del db["pending_gift"][user_id]; save_db_async()
                send_message(chat_id, f"✅ سکه دعوت = {INVITE_REWARD}\n(متن دعوت هم آپدیت شد)", owner_keyboard())
            except: send_message(chat_id, "❌ عدد معتبر!", owner_keyboard())
            return
        
        pac = db["pending_add_coins"].get(user_id, {})
        if pac.get("step") == "waiting_amount":
            try:
                amount = int(convert_number(text))
                count = 0
                for uid in db["users"]: add_coins(uid, amount); count += 1
                del db["pending_add_coins"][user_id]; save_db_async()
                send_message(chat_id, f"✅ {amount} سکه به {count} کاربر اضافه شد!", owner_keyboard())
            except: send_message(chat_id, "❌ عدد معتبر!", owner_keyboard())
            return
        
        pbc = db["pending_broadcast"].get(user_id, {})
        if pbc.get("step") == "waiting_message":
            del db["pending_broadcast"][user_id]; save_db_async()
            send_message(chat_id, f"📢 شروع ارسال...\n\n(هر ۲ ثانیه ۱ نفر)\n📊 کل: {len(db['users'])}", owner_keyboard())
            threading.Thread(target=broadcast_worker, args=(user_id, text), daemon=True).start()
            return
        
        # ═══ سین‌زن ═══
        pending = db["pending_orders"].get(user_id, {})
        if pending.get("step") == "waiting_forward":
            if "forward_from_chat" in message and message["forward_from_chat"]["type"] == "channel":
                db["pending_orders"][user_id] = {"step": "waiting_count", "message_id": message["message_id"], "from_chat_id": message["forward_from_chat"]["id"]}
                save_db_async()
                send_message(chat_id, f"🔢 **چند سین نیاز داری داداش؟**\n\n💰 هر سین = {get_setting('sin_cost', 1)} سکه\n💳 موجودی فعلی تو: {get_coins(user_id):,} سکه\n\n⚠️ حداقل: {MIN_SIN} سین\n\n📌 فقط یه عدد بفرست (فارسی یا انگلیسی)!", cancel_keyboard())
            else: send_message(chat_id, "❌ **این پیام از کانال نیست!**\n\n⚠️ لطفاً پیام رو از یه **کانال** فوروارد کن.", cancel_keyboard())
            return
        
        if pending.get("step") == "waiting_count":
            try:
                count = int(convert_number(text))
                if count < MIN_SIN:
                    send_message(chat_id, f"❌ حداقل باید {MIN_SIN} سین ثبت کنی!", cancel_keyboard()); return
                coins = get_coins(user_id)
                total_cost = count * get_setting('sin_cost', 1)
                if coins < total_cost:
                    send_message(chat_id, f"❌ سکه کافی نداری داداش!\n💰 موجودی: {coins:,} | 💰 نیاز: {total_cost:,}", cancel_keyboard())
                    del db["pending_orders"][user_id]; save_db_async(); return
                remove_coins(user_id, total_cost)
                fwd_result = forward_message(CHANNEL_ID, chat_id, pending["message_id"])
                if fwd_result.get("ok"):
                    fwd_msg_id = fwd_result["result"]["message_id"]
                    db["order_counter"] = db.get("order_counter", 0) + 1
                    order_number = db["order_counter"]
                    order_id = str(int(time.time() * 1000))
                    db["orders"][order_id] = {"user_id": user_id, "count": count, "message_id": fwd_msg_id, "reply_message_id": None, "seen_count": 0, "status": "active", "order_number": order_number}
                    db["seen_records"][order_id] = []
                    db["stats"]["total_orders"] += 1
                    get_user(user_id)["total_orders"] += 1
                    keyboard = {"inline_keyboard": [[{"text": "👁️ دیدم", "callback_data": f"seen_{order_id}"}, {"text": "🤖 مشاهده ربات", "url": BOT_LINK}], [{"text": "🚨 گزارش", "callback_data": f"report_{order_id}"}]]}
                    reply_result = send_reply(CHANNEL_ID, fwd_msg_id, f"📋 **سفارش سین**\n\n👤 سین درخواستی: {count}\n👁️ سین خورده: 0\n#{order_number}", keyboard)
                    if reply_result.get("ok"): db["orders"][order_id]["reply_message_id"] = reply_result["result"]["message_id"]
                    del db["pending_orders"][user_id]; save_db_async()
                    send_message(chat_id, f"✅ **سفارش با موفقیت ثبت شد!** 🎉\n\n🔢 تعداد سین: {count}\n💰 هزینه: {total_cost} سکه\n💳 موجودی جدید: {get_coins(user_id):,} سکه\n📝 شماره سفارش: #{order_number}\n\n👁️ منتظر باش تا کاربرا دکمه «دیدم» رو بزنن!", main_keyboard(user_id))
                else:
                    add_coins(user_id, total_cost)
                    send_message(chat_id, "❌ **خطا در ثبت سفارش!** سکه‌ها برگشت داده شد.", main_keyboard(user_id))
                    del db["pending_orders"][user_id]; save_db_async()
            except ValueError: send_message(chat_id, "❌ **لطفاً یه عدد معتبر وارد کن!**", cancel_keyboard())
            return
        
        # ═══ عضوگیر ═══
        pmem = db["pending_members"].get(user_id, {})
        if pmem.get("step") == "waiting_link":
            db["pending_members"][user_id] = {"step": "waiting_admin", "link": text.strip()}; save_db_async()
            send_message(chat_id, "🔗 **لطفاً منو توی اون کانال ادمین کن!**\n\n⚠️ با تمام دسترسی‌ها\n✅ بعد بنویس: **ادمین کردم**", cancel_keyboard())
            return
        if pmem.get("step") == "waiting_admin":
            if text.strip() == "ادمین کردم":
                link = pmem["link"]
                try:
                    chat_username = "@" + link.split("ble.ir/")[-1] if "ble.ir/" in link else link
                    chat_info = get_chat(chat_username)
                    if chat_info.get("ok"):
                        target_chat_id = chat_info["result"]["id"]
                        member_status = get_chat_member(target_chat_id, int(TOKEN.split(":")[0]))
                        if member_status.get("ok") and member_status["result"]["status"] == "administrator":
                            db["pending_members"][user_id] = {"step": "waiting_type", "link": link, "chat_id": target_chat_id}
                            save_db_async()
                            send_message(chat_id, "📥 **لطفاً نوع عضویت را انتخاب کنید:**\n\n┌──────────────────────────┐\n│  🥉 **۱. نوع معمولی**     │\n│  💰 هزینه هر عضو: ۵ سکه   │\n│  👤 کاربر میتونه هر وقت ترک کنه\n│  ⭐ بستگی به جذابیت کانالت داره\n├──────────────────────────┤\n│  🥇 **۲. نوع تضمینی**     │\n│  💰 هزینه هر عضو: ۱۰ سکه  │\n│  🛡️ کاربر ۴۸ ساعت بمونه   │\n│  ❌ اگه زودتر ترک کنه     │\n│     → کاربر جریمه میشه   │\n│     → سکه به شما برگشت    │\n└──────────────────────────┘\n\n🔢 لطفاً عدد ۱ یا ۲ را وارد کنید:", cancel_keyboard())
                        else: send_message(chat_id, "❌ **هنوز ادمین نشدم!** لطفاً دوباره تلاش کن.", cancel_keyboard())
                    else: send_message(chat_id, "❌ **لینک نامعتبره!** دوباره تلاش کن.", cancel_keyboard())
                except: send_message(chat_id, "❌ **خطا!** لینک رو چک کن.", cancel_keyboard())
            else: send_message(chat_id, "⚠️ لطفاً بنویس: **ادمین کردم**", cancel_keyboard())
            return
        if pmem.get("step") == "waiting_type":
            choice = text.strip()
            if choice in ["1", "2"]:
                order_type = "normal" if choice == "1" else "guaranteed"
                db["pending_members"][user_id]["order_type"] = order_type
                db["pending_members"][user_id]["step"] = "waiting_count"; save_db_async()
                cost_per = 5 if order_type == "normal" else 10
                type_name = "معمولی" if order_type == "normal" else "تضمینی"
                send_message(chat_id, f"📥 **ثبت سفارش عضو - {type_name}**\n\n👥 تعداد عضو موردنیاز را وارد کن داداش\n💰 هزینه هر عضو: {cost_per} سکه\n📌 حداقل سفارش: ۱ عضو\n\n⌨️ لطفاً فقط عدد (مثلاً 50 یا۵۰) را ارسال کنید.", cancel_keyboard())
            else: send_message(chat_id, "❌ فقط عدد ۱ یا ۲ را وارد کنید!", cancel_keyboard())
            return
        if pmem.get("step") == "waiting_count":
            try:
                count = int(convert_number(text))
                if count < MIN_MEMBER:
                    send_message(chat_id, f"❌ حداقل باید {MIN_MEMBER} عضو انتخاب کنی!", cancel_keyboard()); return
                link = pmem["link"]; target_chat_id = pmem["chat_id"]; order_type = pmem.get("order_type", "normal")
                cost_per = 5 if order_type == "normal" else 10
                total_cost = count * cost_per
                coins = get_coins(user_id)
                if coins < total_cost:
                    send_message(chat_id, f"❌ سکه کافی نداری!\n💰 موجودی: {coins:,} | 💰 نیاز: {total_cost:,}", cancel_keyboard())
                    del db["pending_members"][user_id]; save_db_async(); return
                remove_coins(user_id, total_cost)
                db["member_counter"] = db.get("member_counter", 0) + 1
                mnum = db["member_counter"]; mid = str(int(time.time() * 1000))
                reward = get_setting('member_normal_reward', 3) if order_type == "normal" else get_setting('member_guaranteed_reward', 7)
                type_name = "معمولی" if order_type == "normal" else "تضمینی"
                warning_text = "\n⚠️ باید ۴۸ ساعت بمونی!" if order_type == "guaranteed" else ""
                db["member_orders"][mid] = {"user_id": user_id, "count": count, "link": link, "chat_id": target_chat_id, "message_id": None, "seen_count": 0, "status": "active", "order_number": mnum, "order_type": order_type, "reward": reward}
                db["member_records"][mid] = []
                db["stats"]["total_members"] = db["stats"].get("total_members", 0) + 1
                keyboard = {"inline_keyboard": [[{"text": f"🪙 {reward} سکه میگیری!", "callback_data": f"info_{mid}"}], [{"text": "🔗 عضویت در کانال", "url": link}, {"text": "✅ عضو شدم", "callback_data": f"mjoin_{mid}"}], [{"text": "🚨 گزارش", "callback_data": f"mreport_{mid}"}, {"text": "🤖 مشاهده ربات", "url": BOT_LINK}]]}
                sent = send_message(CHANNEL_ID, f"📋 **سفارش عضو - {type_name}**\n\n🔗 لینک کانال: {link}\n👥 تعداد درخواستی: {count}\n✅ تعداد عضو شده: 0\n#{mnum}\n\n🪙 **{reward} سکه میگیری!**{warning_text}", keyboard)
                if sent.get("ok"): db["member_orders"][mid]["message_id"] = sent["result"]["message_id"]
                del db["pending_members"][user_id]; save_db_async()
                send_message(chat_id, f"🎉 **سفارش با موفقیت ثبت شد!**\n\n💰 موجودی جدید: {get_coins(user_id):,} سکه", main_keyboard(user_id))
            except: send_message(chat_id, "❌ عدد معتبر وارد کن!", cancel_keyboard())
            return
        
        if pending.get("step") == "waiting_gift_code":
            code = text.upper().strip()
            if code in db["gift_codes"]:
                g = db["gift_codes"][code]; u = get_user(user_id)
                if code in u["used_gift_codes"]: send_message(chat_id, "❌ تو قبلاً این کد رو زدی!", main_keyboard(user_id))
                elif len(g["used_by"]) >= g["capacity"]: send_message(chat_id, "❌ این کد هدیه تموم شده! ظرفیتش پر شده.", main_keyboard(user_id))
                else:
                    add_coins(user_id, g["coins"]); g["used_by"].append(user_id); u["used_gift_codes"].append(code); save_db_async()
                    send_message(chat_id, f"🎉 **تبریک! {g['coins']:,} سکه!**\n💳 موجودی: {get_coins(user_id):,}", main_keyboard(user_id))
            else: send_message(chat_id, "❌ کد نامعتبر!", main_keyboard(user_id))
            del db["pending_orders"][user_id]; save_db_async(); return
        
        # پیش‌فرض
        send_message(chat_id, f"👋 **سلام {name} جان!** 😎\n\n⚡ من هایپرسین هستم! ابرسین‌زن + عضوگیر\n🎁 اولین عضویت = {START_GIFT} سکه هدیه\n\nاز دکمه‌های زیر استفاده کن:", main_keyboard(user_id))
    
    except Exception as e:
        print(f"⚠️ خطا در handle_message: {e}")

# ═══════════════════════════════════════
# 🔘 پردازش دکمه‌های شیشه‌ای
# ═══════════════════════════════════════
def handle_callback(callback):
    try:
        callback_id = callback["id"]
        data = callback["data"]
        user_id = str(callback["from"]["id"])
        message = callback.get("message", {})
        chat_id = message.get("chat", {}).get("id", CHANNEL_ID)
        
        if is_banned(user_id):
            answer_callback(callback_id, "🚫 شما مسدود شدید!", show_alert=True); return
        
        if data == "check_join":
            if check_joined(user_id):
                user = get_user(user_id)
                if not user.get("got_start_gift"):
                    add_coins(user_id, START_GIFT); user["got_start_gift"] = True
                    if user.get("invited_by") and str(user_id) in db["invited_users"]:
                        inviter_id = user["invited_by"]; vip_mult = get_vip_multiplier(inviter_id)
                        add_coins(inviter_id, INVITE_REWARD * vip_mult)
                        inviter = get_user(inviter_id); inviter["invite_count"] = inviter.get("invite_count", 0) + 1
                        save_db_async()
                        try: send_message(int(inviter_id), f"🎉 **کاربر عضو کانال هم شد!**\n\n👤 {callback['from'].get('first_name', 'کاربر')}\n✅ با لینک دعوت تو اومد\n✅ عضو کانال هم شد\n\n🎁 **{INVITE_REWARD * vip_mult} سکه بهت اهدا شد!** 💰\n💰 موجودی: {get_coins(inviter_id):,} سکه")
                        except: pass
                    save_db_async()
                    answer_callback(callback_id, f"✅ عضو شدی! 🎁 {START_GIFT} سکه هدیه گرفتی!")
                    send_message(user_id, f"✅ **عضو شدی!** 🎉\n\n🎁 **{START_GIFT} سکه هدیه** بهت اضافه شد!\n💰 موجودی: {get_coins(user_id):,} سکه\n\nحالا می‌تونی از ربات استفاده کنی!\nبرای شروع از دکمه‌های زیر استفاده کن:", main_keyboard(user_id))
                else:
                    answer_callback(callback_id, "✅ عضو شدی! حالا میتونی استفاده کنی")
                    send_message(user_id, "✅ **عضو شدی!** 🎉\nحالا می‌تونی از ربات استفاده کنی!\n\nبرای شروع از دکمه‌های زیر استفاده کن:", main_keyboard(user_id))
            else: answer_callback(callback_id, "❌ هنوز عضو نشدی! لطفاً اول عضو کانال شو.")
            return
        
        if data == "back_to_main":
            send_message(user_id, "🏠 منوی اصلی:", main_keyboard(user_id)); answer_callback(callback_id); return
        
        if data == "copy_id":
            answer_callback(callback_id, f"✅ آیدی عددی: {user_id}", show_alert=True); return
        
        if data.startswith("packet_"):
            pid = data.replace("packet_", "")
            if pid not in db.get("coin_packets", {}): answer_callback(callback_id, "❌ پاکت وجود نداره!", show_alert=True); return
            p = db["coin_packets"][pid]
            if str(user_id) in p["used_by"]: answer_callback(callback_id, "⚠️ قبلاً باز کردی!", show_alert=True); return
            if len(p["used_by"]) >= p["capacity"]: answer_callback(callback_id, "😢 **دیر رسیدی!**", show_alert=True); return
            p["used_by"].append(str(user_id)); add_coins(user_id, p["coins"]); save_db_async()
            answer_callback(callback_id, f"🎉 **سکه پاکت باز شد!**\n\n🪙 تعداد سکه هدیه: {p['coins']}\n💰 موجودی: {get_coins(user_id):,}", show_alert=True); return
        
        if data.startswith("userpacket_"):
            pid = data.replace("userpacket_", "")
            if pid not in db.get("coin_packets", {}): answer_callback(callback_id, "❌ پاکت وجود نداره!", show_alert=True); return
            p = db["coin_packets"][pid]
            if str(user_id) in p["used_by"]: answer_callback(callback_id, "⚠️ قبلاً باز کردی!", show_alert=True); return
            p["used_by"].append(str(user_id)); add_coins(user_id, p["coins"]); save_db_async()
            answer_callback(callback_id, f"🎉 {p['coins']} سکه گرفتی!\n💰 موجودی: {get_coins(user_id):,}", show_alert=True); return
        
        if data.startswith("seen_"):
            order_id = data.replace("seen_", "")
            if order_id not in db["orders"]: answer_callback(callback_id, "❌ این سفارش وجود نداره!"); return
            order = db["orders"][order_id]
            if order["status"] != "active": answer_callback(callback_id, "✅ تکمیل شده!"); return
            if str(user_id) in db["seen_records"].get(order_id, []): answer_callback(callback_id, "⚠️ قبلاً دیدم رو زدی!"); return
            db["seen_records"][order_id].append(str(user_id)); order["seen_count"] += 1
            vip_mult = get_vip_multiplier(user_id)
            add_coins(user_id, get_setting('seen_reward', 1) * vip_mult)
            new_seen = order["seen_count"]; count = order["count"]; order_number = order.get("order_number", "?")
            answer_callback(callback_id, f"👁️ ثبت شد! (+{get_setting('seen_reward', 1) * vip_mult} سکه) | 💰 موجودی: {get_coins(user_id):,} سکه")
            if order.get("reply_message_id"):
                keyboard = {"inline_keyboard": [[{"text": "👁️ دیدم", "callback_data": f"seen_{order_id}"}, {"text": "🤖 مشاهده ربات", "url": BOT_LINK}], [{"text": "🚨 گزارش", "callback_data": f"report_{order_id}"}]]}
                try: edit_message_text(CHANNEL_ID, order["reply_message_id"], f"📋 **سفارش سین**\n\n👤 سین درخواستی: {count}\n👁️ سین خورده: {new_seen}\n#{order_number}", keyboard)
                except: pass
            if new_seen >= count:
                order["status"] = "completed"
                db["stats"]["completed_orders"] += 1; db["stats_advanced"]["orders_completed"] += 1
                get_user(order["user_id"])["completed_orders"] += 1
                try: delete_message(CHANNEL_ID, order["message_id"]); db["stats"]["deleted_messages"] += 1
                except: pass
                try:
                    if order.get("reply_message_id"): delete_message(CHANNEL_ID, order["reply_message_id"])
                except: pass
                try: send_message(int(order["user_id"]), f"🎉 **تبریک داداش!**\n\n🔢 {count} سین درخواستی تو کامل خورد!\n📩 پیام از کانال حذف شد.\n\n💡 **حالا می‌تونی:**\n• 🪙 بری کسب سکه کنی\n• 👁️ سفارش جدید ثبت کنی\n• 🚀 اگه سکه داری، همین الان ثبت کن!", main_keyboard(order["user_id"]))
                except: pass
            save_db_async(); return
        
        if data.startswith("report_"):
            order_id = data.replace("report_", "")
            if order_id not in db["orders"]: answer_callback(callback_id, "❌ وجود نداره!", show_alert=True); return
            order = db["orders"][order_id]; reporter_username = callback["from"].get("username", "نامشخص")
            answer_callback(callback_id, "🚨 گزارش ثبت شد!", show_alert=True)
            try: send_message(int(OWNER_ID), f"🚨 **گزارش سین**\n\n👤 گزارش‌دهنده: @{reporter_username}\n📝 سفارش: #{order.get('order_number', '?')}\n🔢 سین درخواستی: {order['count']}\n👁️ سین خورده: {order['seen_count']}\n\n⚠️ بررسی کن!")
            except: pass
            return
        
        if data.startswith("info_"):
            mid = data.replace("info_", ""); o = db["member_orders"].get(mid, {})
            reward = o.get("reward", 3); otype = o.get("order_type", "normal")
            if otype == "guaranteed": answer_callback(callback_id, f"🪙 {reward} سکه میگیری!\n⚠️ باید ۴۸ ساعت بمونی!\n❌ ترک زودهنگام = -۷ سکه", show_alert=True)
            else: answer_callback(callback_id, f"🪙 {reward} سکه میگیری!", show_alert=True)
            return
        
        if data.startswith("mjoin_"):
            mid = data.replace("mjoin_", "")
            if mid not in db["member_orders"]: answer_callback(callback_id, "❌ وجود نداره!", show_alert=True); return
            order = db["member_orders"][mid]
            if order["status"] != "active": answer_callback(callback_id, "✅ تکمیل شده!", show_alert=True); return
            if str(user_id) in db["member_records"].get(mid, []): answer_callback(callback_id, "⚠️ قبلاً عضو شدی!", show_alert=True); return
            if is_order_owner(user_id, mid): answer_callback(callback_id, "❌ نمیتونی توی سفارش خودت عضو بشی!", show_alert=True); return
            target_chat_id = order["chat_id"]
            member_status = get_chat_member(target_chat_id, user_id)
            if member_status.get("ok") and member_status["result"]["status"] in ["member", "administrator", "creator"]:
                db["member_records"][mid].append(str(user_id)); order["seen_count"] += 1
                reward = order.get("reward", 3); vip_mult = get_vip_multiplier(user_id)
                add_coins(user_id, reward * vip_mult)
                otype = order.get("order_type", "normal")
                type_name = "معمولی" if otype == "normal" else "تضمینی"
                warning_text = "\n⚠️ باید ۴۸ ساعت بمونی!" if otype == "guaranteed" else ""
                if otype == "guaranteed": db["guaranteed_members"][f"{user_id}_{mid}"] = str(datetime.now()); save_db_async()
                new_seen = order["seen_count"]; count = order["count"]; mnum = order.get("order_number", "?")
                answer_callback(callback_id, f"✅ عضو شدی! 🎉 +{reward * vip_mult} سکه | 💰 موجودی: {get_coins(user_id):,} سکه", show_alert=True)
                if order.get("message_id"):
                    keyboard = {"inline_keyboard": [[{"text": f"🪙 {reward} سکه میگیری!", "callback_data": f"info_{mid}"}], [{"text": "🔗 عضویت در کانال", "url": order["link"]}, {"text": "✅ عضو شدم", "callback_data": f"mjoin_{mid}"}], [{"text": "🚨 گزارش", "callback_data": f"mreport_{mid}"}, {"text": "🤖 مشاهده ربات", "url": BOT_LINK}]]}
                    try: edit_message_text(CHANNEL_ID, order["message_id"], f"📋 **سفارش عضو - {type_name}**\n\n🔗 لینک کانال: {order['link']}\n👥 تعداد درخواستی: {count}\n✅ تعداد عضو شده: {new_seen}\n#{mnum}\n\n🪙 **{reward} سکه میگیری!**{warning_text}", keyboard)
                    except: pass
                if new_seen >= count:
                    order["status"] = "completed"
                    db["stats"]["completed_members"] = db["stats"].get("completed_members", 0) + 1
                    db["stats_advanced"]["orders_completed"] += 1
                    try: delete_message(CHANNEL_ID, order["message_id"]); db["stats"]["deleted_messages"] += 1
                    except: pass
                    try: send_message(int(order["user_id"]), f"🎉 **تبریک داداش!**\n\n👥 {count} عضو درخواستی تو کامل شد!\n📩 پیام از کانال حذف شد.\n\n💡 **حالا می‌تونی:**\n• 🪙 بری کسب سکه کنی\n• 👥 سفارش عضو جدید ثبت کنی\n• 🚀 اگه سکه داری، همین الان ثبت کن!", main_keyboard(order["user_id"]))
                    except: pass
            else: answer_callback(callback_id, "❌ هنوز عضو نشدی! اول عضو شو تا سکه بگیری.", show_alert=True)
            save_db_async(); return
        
        if data.startswith("mreport_"):
            mid = data.replace("mreport_", "")
            if mid not in db["member_orders"]: answer_callback(callback_id, "❌ وجود نداره!", show_alert=True); return
            order = db["member_orders"][mid]; reporter_username = callback["from"].get("username", "نامشخص")
            answer_callback(callback_id, "🚨 گزارش ثبت شد!", show_alert=True)
            try: send_message(int(OWNER_ID), f"🚨 **گزارش عضو**\n\n👤 گزارش‌دهنده: @{reporter_username}\n📝 سفارش: #{order.get('order_number', '?')}\n🔗 لینک: {order['link']}\n👥 درخواستی: {order['count']}\n✅ عضو شده: {order['seen_count']}\n\n⚠️ بررسی کن!")
            except: pass
            return
        
        if data == "suspicious_cases":
            msg = "🚨 **موارد مشکوک:**\n\n"; found = False
            for uid, udata in list(db["users"].items())[:20]:
                if udata.get("invite_count", 0) > 10:
                    msg += f"👤 @{udata.get('username', 'ندارد')}\n❌ دعوت زیاد: {udata['invite_count']}\n\n"; found = True
            answer_callback(callback_id)
            send_message(user_id, msg if found else "✅ مورد مشکوکی نیست!", owner_keyboard()); return
        
        if data == "today_report":
            stats = db["stats_advanced"]; answer_callback(callback_id)
            send_message(user_id, f"📊 **گزارش امروز:**\n\n👥 کاربر جدید: {stats['new_users']}\n💰 سکه توزیع: {stats['coins_distributed']:,}\n💸 سکه مصرف: {stats['coins_spent']:,}", owner_keyboard()); return
        
        if data == "suspicious_usernames":
            msg = "🔒 **یوزرنیم‌های مشکوک:**\n\n"; found = False
            for uid, udata in list(db["users"].items())[:20]:
                if udata.get("invite_count", 0) > 10:
                    msg += f"👤 @{udata.get('username', 'ندارد')}\n📝 دعوت: {udata['invite_count']}\n\n"; found = True
            answer_callback(callback_id)
            send_message(user_id, msg if found else "✅ مشکوکی نیست!", owner_keyboard()); return
        
        if data == "antifraud_log":
            msg = "📜 **لاگ ضدتقلب:**\n\n"; punished = db.get("punished_users", [])
            if punished:
                for p in punished[:10]: msg += f"⚠️ {p}\n"
            else: msg += "✅ لاگ خالیه!"
            answer_callback(callback_id)
            send_message(user_id, msg, owner_keyboard()); return
        
        if data == "add_join_channel":
            db["pending_join_channel"][user_id] = {"step": "waiting_link"}; save_db_async()
            answer_callback(callback_id); send_message(user_id, "🔗 **لینک کانال رو بفرست:**"); return
        
        if data == "remove_join_channel":
            db["pending_remove_join"][user_id] = {"step": "waiting_link"}; save_db_async()
            answer_callback(callback_id); send_message(user_id, "🔗 **لینک کانالی که می‌خوای حذف بشه رو بفرست:**"); return
        
        if data == "list_join_channels":
            channels = db.get("join_channels", [])
            if channels:
                msg = "📋 **جوین‌های اجباری:**\n\n"
                for ch in channels: msg += f"📢 {ch}\n"
            else: msg = "❌ جوینی اضافه نشده!"
            answer_callback(callback_id); send_message(user_id, msg, owner_keyboard()); return
    
    except Exception as e:
        print(f"⚠️ خطا در handle_callback: {e}")

# ═══════════════════════════════════════
# 🚀 حلقه اصلی
# ═══════════════════════════════════════
last_update_id = 0

def main():
    global last_update_id, INVITE_REWARD
    INVITE_REWARD = db.get("invite_reward", INVITE_REWARD)
    print("⚡ هایپرسین | سین‌زن + عضوگیر")
    print(f"🤖 @{BOT_USERNAME} | 📢 {CHANNEL_LINK}")
    print(f"👁️ دیدم: {get_setting('seen_reward', 1)} | 📝 سین: {get_setting('sin_cost', 1)} | 👥 عضو: {get_setting('member_cost', 5)}")
    print(f"🛡️ ۶ محافظ | ⚡ فوق سریع | 🥇 تضمینی | 🎁 سکه پاکت | ⭐ VIP | 🛡️ ضدتقلب | 💻 اجرای کد")
    print("-" * 40)
    while True:
        try:
            server_guard.protect()
            updates = api_call("getUpdates", {"offset": last_update_id + 1, "limit": 100, "timeout": 3})
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    last_update_id = update["update_id"]
                    msg = update.get("message", {})
                    if msg and "left_chat_member" in msg:
                        left_user_id = str(msg["left_chat_member"]["id"])
                        left_chat_id = str(msg["chat"]["id"])
                        for mid, order in list(db["member_orders"].items()):
                            if order.get("order_type") == "guaranteed" and str(order.get("chat_id")) == left_chat_id:
                                key = f"{left_user_id}_{mid}"
                                if key not in db["punished_users"] and left_user_id in db["member_records"].get(mid, []):
                                    join_time_str = db["guaranteed_members"].get(key)
                                    if join_time_str and not is_48h_passed(join_time_str):
                                        if remove_coins(left_user_id, 7):
                                            add_coins(order["user_id"], 5); mark_punished(left_user_id, mid)
                                            try: send_message(int(left_user_id), f"⚠️ **شما کانال رو قبل از ۴۸ ساعت ترک کردید!**\n\n📢 کانال: {order['link']}\n📋 نوع سفارش: **تضمینی**\n⏰ باید ۴۸ ساعت عضو می‌ماندید!\n\n💰 **۷ سکه از موجودی شما کم شد.**\n💳 موجودی: {get_coins(left_user_id):,} سکه")
                                            except: pass
                                            try: send_message(int(order["user_id"]), f"🔔 **یه کاربر کانال رو قبل از ۴۸ ساعت ترک کرد!**\n\n📢 کانال: {order['link']}\n📋 نوع سفارش: **تضمینی**\n\n💰 **۵ سکه به موجودی شما برگشت داده شد.**\n💳 موجودی: {get_coins(order['user_id']):,} سکه")
                                            except: pass
                    if "message" in update and "left_chat_member" not in msg: handle_message(msg)
                    elif "callback_query" in update: handle_callback(update["callback_query"])
            time.sleep(0.05)
        except KeyboardInterrupt:
            print("\n👋 ربات خاموش شد!"); break
        except Exception as e:
            print(f"⚠️ خطا: {e}"); time.sleep(0.3); continue

# ═══════════════════════════════════════
# 🌐 Flask
# ═══════════════════════════════════════
app = Flask(__name__)

@app.route('/')
def home(): return "🤖 Hypersin Bot is running!"

@app.route('/ping')
def ping(): return "pong ✅"

@app.route('/health')
def health():
    return jsonify({"status": "online", "users": len(db.get("users", {})), "uptime": str(datetime.now() - START_TIME)})

# ═══════════════════════════════════════
# 🚀 اجرا
# ═══════════════════════════════════════
if __name__ == "__main__":
    threading.Thread(target=save_worker, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    threading.Thread(target=main, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)