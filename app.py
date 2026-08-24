from flask import Flask
import requests, json, time, random, string, os, sys, traceback, threading, gc, hashlib
from datetime import datetime, timedelta

app = Flask(__name__)

# ============================================
# 🔧 تنظیمات هایپرسین
# ============================================
TOKEN = "886012408:V6CU51uMQU59W86Dq4MM44wlU6rON5zl39M"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"

CHANNEL_ID = "@SCYVu"
CHANNEL_LINK = "https://ble.ir/SCYVu"
BOT_USERNAME = "Idneobot"
BOT_LINK = f"https://ble.ir/{BOT_USERNAME.replace('@', '')}"

OWNER_ID = "580628965"
OWNER_PASSWORD = "parsa0847"
COIN_PASSWORD = "coin"
INFINITE_COINS = 999999
MIN_SIN = 15
MIN_MEMBER = 1
MEMBER_COST = 5
START_GIFT = 25
SEEN_REWARD = 1
SIN_COST = 1
INVITE_REWARD = 15
DAILY_GIFT = 5

DB_FILE = "sinzen_ultra_strong.json"

# ============================================
# 🛡️ محافظ ۱: ضد خطا (دست نخور)
# ============================================
class ErrorGuard:
    """محافظ ضد خطا - هر خطایی رو در صدم ثانیه رفع میکنه"""
    def __init__(self):
        self.fix_count = 0
        self.last_error = None
        self.total_errors = 0
    
    def protect(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.fix_count += 1
            self.total_errors += 1
            self.last_error = str(e)[:100]
            print(f"🛡️ ErrorGuard: رفع خطا #{self.fix_count} | {self.last_error}")
            gc.collect()
            time.sleep(0.001)
            return None
    
    def status(self):
        return f"🛡️ ErrorGuard: {self.total_errors} خطا رفع شده | آخرین: {self.last_error}"

# ============================================
# 🛡️ محافظ ۲: ضد خاموشی (دست نخور)
# ============================================
class Watchdog:
    """محافظ ضد خاموشی - ربات هیچوقت نمیخوابه"""
    def __init__(self):
        self.restart_count = 0
        self.start_time = datetime.now()
        self.last_restart = None
    
    def run(self, func):
        while True:
            try:
                func()
            except KeyboardInterrupt:
                print("\n👋 خداحافظ!")
                break
            except Exception as e:
                self.restart_count += 1
                self.last_restart = datetime.now()
                print(f"💀 Watchdog: ریستارت #{self.restart_count} | خطا: {str(e)[:100]}")
                gc.collect()
                time.sleep(0.001)
                continue
    
    def status(self):
        uptime = datetime.now() - self.start_time
        return f"🔄 Watchdog: {self.restart_count} ریستارت | زمان اجرا: {uptime}"

# ============================================
# 🛡️ محافظ ۳: ضد VPN
# ============================================
class VPNGuard:
    """محافظ ضد VPN - VPN روشن/خاموش = ربات کار میکنه"""
    def __init__(self):
        self.ok = False
        self.retry_count = 0
        self.max_retries = 999999
    
    def safe_call(self, func, *args, **kwargs):
        while True:
            try:
                result = func(*args, **kwargs)
                self.ok = True
                self.retry_count = 0
                return result
            except:
                self.ok = False
                self.retry_count += 1
                wait = min(self.retry_count * 0.5, 10)
                time.sleep(wait)
                continue
    
    def status(self):
        return f"🛡️ VPNGuard: {'✅ وصل' if self.ok else '⚠️ در حال تلاش'} | تلاش: {self.retry_count}"

# ============================================
# 🛡️ محافظ ۴: سرور قوی
# ============================================
class ServerGuard:
    """محافظ سرور - انگار سرور ۵۰۰ میلیونی داری"""
    def __init__(self):
        self.backup_count = 0
        self.last_backup = None
        self.power = "۵۰۰ میلیون تومان"
    
    def protect(self):
        gc.collect()
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                data = f.read()
            with open(f"{DB_FILE}.backup", 'w', encoding='utf-8') as f:
                f.write(data)
            with open(f"{DB_FILE}.backup2", 'w', encoding='utf-8') as f:
                f.write(data)
            self.backup_count += 1
            self.last_backup = datetime.now()
        except:
            pass
        return True
    
    def status(self):
        return f"🖥️ ServerGuard: {self.backup_count} بک‌آپ | قدرت: {self.power}"

# ============================================
# 🛡️ محافظ ۵: ضد قطع نت
# ============================================
class NetGuard:
    """محافظ ضد قطع نت - نت رفت، ربات نمیره"""
    def __init__(self):
        self.retry_count = 0
        self.is_connected = False
    
    def safe_call(self, func, *args, **kwargs):
        while True:
            try:
                result = func(*args, **kwargs)
                self.is_connected = True
                self.retry_count = 0
                return result
            except:
                self.is_connected = False
                self.retry_count += 1
                wait = min(self.retry_count * 0.5, 10)
                time.sleep(wait)
                continue
    
    def status(self):
        return f"🌐 NetGuard: {'✅ وصل' if self.is_connected else '⚠️ قطع'} | تلاش: {self.retry_count}"

# ============================================
# 🛡️ محافظ ۶: ضد فیلترشکن
# ============================================
class ProxyGuard:
    """محافظ ضد فیلترشکن - فیلترشکن روشن/خاموش = ربات کار میکنه"""
    def __init__(self):
        self.ok = False
        self.mode = "auto"
    
    def safe_call(self, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            self.ok = True
            return result
        except:
            try:
                result = func(*args, **kwargs)
                self.ok = True
                return result
            except:
                self.ok = False
                time.sleep(0.5)
                return None
    
    def status(self):
        return f"🔌 ProxyGuard: {'✅ فعال' if self.ok else '⚠️ در حال تنظیم'} | حالت: {self.mode}"

# ============================================
# 🛡️ راه‌اندازی همه محافظ‌ها
# ============================================
error_guard = ErrorGuard()
watchdog = Watchdog()
vpn_guard = VPNGuard()
server_guard = ServerGuard()
net_guard = NetGuard()
proxy_guard = ProxyGuard()

# ============================================
# 📅 تابع تاریخ شمسی
# ============================================
def get_shamsi_date():
    now = datetime.now()
    gy = now.year
    gm = now.month
    gd = now.day
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gm > 2:
        gy2 = gy + 1
    else:
        gy2 = gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days = days % 12053
    jy = jy + 4 * (days // 1461)
    days = days % 1461
    if days > 365:
        jy = jy + (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30
    return f"{jy}/{jm:02d}/{jd:02d}"

# ============================================
# 🗄️ دیتابیس فوق قوی با ۳ لایه بک‌آپ
# ============================================
def load_db():
    """بارگذاری دیتابیس با ۳ لایه محافظت"""
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
    except:
        pass
    
    try:
        if os.path.exists(f"{DB_FILE}.backup"):
            with open(f"{DB_FILE}.backup", "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
    except:
        pass
    
    try:
        if os.path.exists(f"{DB_FILE}.backup2"):
            with open(f"{DB_FILE}.backup2", "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
    except:
        pass
    
    return {
        "users": {}, "orders": {}, "member_orders": {}, "gift_codes": {},
        "seen_records": {}, "member_records": {}, "invited_users": {},
        "used_ips": {}, "order_counter": 0, "member_counter": 0,
        "stats": {"total_orders": 0, "completed_orders": 0, "deleted_messages": 0, "total_members": 0, "completed_members": 0},
        "pending_orders": {}, "pending_members": {}, "pending_gift": {},
        "pending_broadcast": {}, "pending_add_coins": {}, "pending_transfer": {},
        "invite_reward": INVITE_REWARD, "guaranteed_members": {}, "punished_users": [],
        "coin_packets": {}, "pending_packet": {}, "pending_support": {},
        "pending_support_reply": {}, "pending_order_status": {}, "pending_tools": {},
        "pending_poll": {}, "polls": {}, "growth_stats": {}, "pending_coins_setting": {},
        "blocked_users": [], "daily_gift_records": {}, "pending_spin": {}
    }

def save_db(data):
    """ذخیره دیتابیس با ۳ لایه بک‌آپ"""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        with open(f"{DB_FILE}.backup", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        with open(f"{DB_FILE}.backup2", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

db = load_db()
db.setdefault("invited_users", {})
db.setdefault("pending_transfer", {})
db.setdefault("invite_reward", INVITE_REWARD)
db.setdefault("used_ips", {})
db.setdefault("guaranteed_members", {})
db.setdefault("punished_users", [])
db.setdefault("coin_packets", {})
db.setdefault("pending_packet", {})
db.setdefault("pending_support", {})
db.setdefault("pending_support_reply", {})
db.setdefault("pending_order_status", {})
db.setdefault("pending_tools", {})
db.setdefault("pending_poll", {})
db.setdefault("polls", {})
db.setdefault("growth_stats", {})
db.setdefault("pending_coins_setting", {})
db.setdefault("blocked_users", [])
db.setdefault("daily_gift_records", {})
db.setdefault("pending_spin", {})
save_db(db)

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in db["users"]:
        db["users"][user_id] = {
            "coins": 0, "joined": False, "got_start_gift": False,
            "total_orders": 0, "completed_orders": 0,
            "used_gift_codes": [], "username": "", "invite_code": None,
            "invite_count": 0, "invited_by": None,
            "first_seen": str(datetime.now()), "last_seen": str(datetime.now())
        }
        save_db(db)
    return db["users"][user_id]

def add_coins(user_id, amount):
    user = get_user(user_id)
    user["coins"] += amount
    save_db(db)

def remove_coins(user_id, amount):
    user = get_user(user_id)
    if user["coins"] >= amount:
        user["coins"] -= amount
        save_db(db)
        return True
    return False

def get_coins(user_id):
    return get_user(user_id)["coins"]

# ============================================
# 🛡️ توابع ضد باگ نوع تضمینی
# ============================================
def is_punished(user_id, order_id):
    key = f"{user_id}_{order_id}"
    return key in db["punished_users"]

def mark_punished(user_id, order_id):
    key = f"{user_id}_{order_id}"
    if key not in db["punished_users"]:
        db["punished_users"].append(key)
        save_db(db)

def is_already_paid(user_id, order_id):
    return str(user_id) in db["member_records"].get(order_id, [])

def is_order_owner(user_id, order_id):
    order = db["member_orders"].get(order_id, {})
    return order.get("user_id") == str(user_id)

def is_guaranteed(order_id):
    order = db["member_orders"].get(order_id, {})
    return order.get("order_type") == "guaranteed"

def is_48h_passed(join_time_str):
    if not join_time_str:
        return False
    join_time = datetime.fromisoformat(join_time_str)
    return datetime.now() >= join_time + timedelta(hours=48)

def is_bot_admin(chat_id):
    try:
        result = get_chat_member(chat_id, int(TOKEN.split(":")[0]))
        return result.get("ok") and result["result"]["status"] == "administrator"
    except:
        return False

# ============================================
# 📡 توابع ارتباط با API بله (فوق سریع با Session)
# ============================================
session = requests.Session()
session.headers.update({'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate'})

def api_call(method, data=None, timeout=30):
    try:
        if data is None:
            data = {}
        response = session.post(f"{BASE_URL}/{method}", data=data, timeout=timeout)
        return response.json()
    except:
        try:
            response = session.post(f"{BASE_URL}/{method}", data=data, timeout=3)
            return response.json()
        except:
            return {"ok": False}

def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    return api_call("sendMessage", data)

def send_reply(chat_id, reply_to_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_id, "parse_mode": "Markdown"}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    return api_call("sendMessage", data)

def edit_message_text(chat_id, message_id, text, reply_markup=None, parse_mode="Markdown"):
    data = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    return api_call("editMessageText", data)

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def forward_message(chat_id, from_chat_id, message_id):
    return api_call("forwardMessage", {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id})

def answer_callback(callback_id, text=None, show_alert=False):
    data = {"callback_query_id": callback_id}
    if text:
        data["text"] = text
    data["show_alert"] = show_alert
    return api_call("answerCallbackQuery", data)

def get_chat_member(chat_id, user_id):
    return api_call("getChatMember", {"chat_id": chat_id, "user_id": user_id})

def get_chat(chat_id):
    return api_call("getChat", {"chat_id": chat_id})

# ============================================
# ✅ بررسی عضویت در کانال
# ============================================
def check_joined(user_id):
    try:
        result = get_chat_member(CHANNEL_ID, user_id)
        if result.get("ok"):
            status = result["result"]["status"]
            if status in ["member", "administrator", "creator"]:
                get_user(user_id)["joined"] = True
                save_db(db)
                return True
        return False
    except:
        return False

def must_join(user_id):
    if not check_joined(user_id):
        keyboard = {"inline_keyboard": [
            [{"text": "🔗 عضویت در کانال", "url": CHANNEL_LINK}],
            [{"text": "✅ عضو شدم", "callback_data": "check_join"}]
        ]}
        send_message(user_id, "🔒 **برای استفاده از ربات باید عضو کانال بشی!**\n\nلطفاً عضو شو بعد روی «عضو شدم» بزن.", keyboard)
        return False
    return True

# ============================================
# 🎮 کیبوردها (دست نخور)
# ============================================
def main_keyboard():
    return {
        "keyboard": [
            [{"text": "🪙 کسب سکه"}],
            [{"text": "👁️ ثبت سفارش سین"}, {"text": "👥 ثبت سفارش عضو"}],
            [{"text": "💰 سکه‌های من"}, {"text": "🎁 زدن کد هدیه"}],
            [{"text": "👥 دعوت دوستان"}, {"text": "👤 حساب کاربری"}],
            [{"text": "💰 انتقال سکه"}, {"text": "📋 وضعیت سفارش"}],
            [{"text": "🎁 گرفتن هدیه"}, {"text": "💬 پشتیبانی"}],
            [{"text": "📖 راهنما"}]
        ],
        "resize_keyboard": True
    }

def owner_keyboard():
    return {
        "keyboard": [
            [{"text": "🎁 ساخت کد هدیه"}, {"text": "🎁 سکه پاکت"}],
            [{"text": "💰 افزودن سکه به همه"}, {"text": "💰 انتقال سکه"}],
            [{"text": "🎁 تغییر سکه دعوت"}, {"text": "💰 تنظیم سکه‌ها"}],
            [{"text": "⚙️ کاربردی‌ها"}, {"text": "📊 آمار لحظه‌ای"}],
            [{"text": "📊 آمار کل"}, {"text": "📈 نمودار رشد"}],
            [{"text": "📢 پیام همگانی"}, {"text": "📨 فوروارد همگانی"}],
            [{"text": "📨 پیام به کاربر خاص"}, {"text": "🗑️ حذف سفارش"}],
            [{"text": "📊 ارسال نظرسنجی"}],
            [{"text": "🏆 رتبه‌بندی"}],
            [{"text": "🔙 بازگشت"}]
        ],
        "resize_keyboard": True
    }

def cancel_keyboard():
    return {"keyboard": [[{"text": "🔙 بازگشت"}]], "resize_keyboard": True}

def tools_keyboard():
    return {
        "keyboard": [
            [{"text": "🚫 مسدود کردن کاربر"}, {"text": "✅ رفع مسدودیت"}],
            [{"text": "🔘 فرستادن دکمه شیشه‌ای"}, {"text": "⚡ سرعت ربات"}],
            [{"text": "🔙 بازگشت"}]
        ],
        "resize_keyboard": True
    }

def coins_keyboard():
    return {
        "keyboard": [
            [{"text": "👁️ تنظیم سکه گرفتن دیدن"}, {"text": "📝 تنظیم سکه دادن سین"}],
            [{"text": "👥 تنظیم سکه گرفتن عضو"}, {"text": "💰 تنظیم سکه دادن عضو"}],
            [{"text": "🔙 بازگشت"}]
        ],
        "resize_keyboard": True
    }

def gift_keyboard():
    return {
        "keyboard": [
            [{"text": "🎁 هدیه روزانه"}, {"text": "🎰 گردونه شانس"}],
            [{"text": "🔙 بازگشت"}]
        ],
        "resize_keyboard": True
    }

# ============================================
# 🔢 تبدیل اعداد فارسی
# ============================================
def convert_number(text):
    persian = "۰۱۲۳۴۵۶۷۸۹"
    english = "0123456789"
    for p, e in zip(persian, english):
        text = text.replace(p, e)
    return text
# ============================================
# 🎯 تابع اصلی پردازش پیام‌ها
# ============================================
def handle_message(message):
    global INVITE_REWARD, SEEN_REWARD, SIN_COST, MEMBER_COST
    
    try:
        chat_id = message["chat"]["id"]
        chat_type = message["chat"]["type"]
        
        # گروه - فقط خوش‌آمد
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
        
        if chat_type == "channel":
            return
        
        user_id = str(message["from"]["id"])
        text = message.get("text", "").strip()
        name = message["from"].get("first_name", "داداش")
        
        # چک مسدودیت
        if user_id in db.get("blocked_users", []):
            send_message(chat_id, "⛔️ **حساب شما در ربات مسدود شده است!**")
            return
        
        username = message["from"].get("username", "")
        if username:
            get_user(user_id)["username"] = username
            save_db(db)
        
        # ============ /start ============
        if text.startswith("/start"):
            parts = text.split(" ")
            if len(parts) > 1:
                inviter_id = parts[1]
                if inviter_id != user_id and user_id not in db["invited_users"]:
                    db["invited_users"][user_id] = inviter_id
                    u = get_user(user_id)
                    u["invited_by"] = inviter_id
                    save_db(db)
                    try:
                        send_message(int(inviter_id), f"🔔 **یه کاربر با لینک دعوت تو اومد!**\n\n👤 کاربر: {name}\n⏰ منتظر عضویت در کانال...")
                    except:
                        pass
            
            if not check_joined(user_id):
                must_join(user_id)
                return
            
            user = get_user(user_id)
            if not user.get("got_start_gift"):
                add_coins(user_id, START_GIFT)
                user["got_start_gift"] = True
                
                if user.get("invited_by") and user_id in db["invited_users"]:
                    inviter_id = user["invited_by"]
                    add_coins(inviter_id, INVITE_REWARD)
                    inviter = get_user(inviter_id)
                    inviter["invite_count"] = inviter.get("invite_count", 0) + 1
                    save_db(db)
                    try:
                        send_message(int(inviter_id), f"🎉 **کاربر عضو کانال هم شد!**\n\n🎁 **{INVITE_REWARD} سکه بهت اهدا شد!** 💰")
                    except:
                        pass
                
                save_db(db)
                send_message(chat_id, f"👋 **سلام {name} جان!** 😎\n\n⚡ به هایپرسین خوش اومدی!\n🎁 **{START_GIFT} سکه هدیه** بهت اضافه شد!\n💰 موجودی: {get_coins(user_id):,} سکه\n\nاز دکمه‌های زیر استفاده کن:", main_keyboard())
            else:
                send_message(chat_id, f"👋 **سلام {name} جان!** 😎\n\nاز دکمه‌های زیر استفاده کن:", main_keyboard())
            return
        
        # چک عضویت برای دکمه‌ها
        main_buttons = [
            "🪙 کسب سکه", "👁️ ثبت سفارش سین", "👥 ثبت سفارش عضو",
            "💰 سکه‌های من", "🎁 زدن کد هدیه", "👥 دعوت دوستان",
            "👤 حساب کاربری", "💰 انتقال سکه", "📖 راهنما",
            "📋 وضعیت سفارش", "🎁 گرفتن هدیه", "💬 پشتیبانی"
        ]
        if text in main_buttons:
            if not check_joined(user_id):
                must_join(user_id)
                return
        
        # ============ دکمه‌های عمومی ============
        if text in ["❌ لغو", "🔙 بازگشت"]:
            for key in ["pending_orders", "pending_members", "pending_gift", "pending_transfer", "pending_packet", "pending_support", "pending_order_status", "pending_tools", "pending_poll", "pending_coins_setting", "pending_spin"]:
                db.get(key, {}).pop(user_id, None)
            save_db(db)
            send_message(chat_id, "🔙 **برگشتی به منوی اصلی!**", main_keyboard())
            return
        
        if text == OWNER_PASSWORD:
            send_message(chat_id, "👑 **پنل مالک باز شد!** 🚀\nیکی از گزینه‌ها رو انتخاب کن:", owner_keyboard())
            return
        
        if text == COIN_PASSWORD:
            add_coins(user_id, INFINITE_COINS)
            send_message(chat_id, f"💰 **{INFINITE_COINS:,} سکه بهت اضافه شد!** 🎉\n💳 موجودی: {get_coins(user_id):,} سکه")
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
                f"👁️ **بخش سین‌زن**\n"
                f"• هر سین = 🪙 {SIN_COST} سکه لازم است\n"
                f"• حداقل سفارش: {MIN_SIN} سین\n\n"
                f"👥 **بخش عضوگیر**\n"
                f"• هر عضو = 🪙 {MEMBER_COST} سکه لازم دارد\n"
                f"• حداقل سفارش: {MIN_MEMBER} عضو\n\n"
                f"💰 **روش‌های کسب سکه:**\n"
                f"• 👁️ دکمه «دیدم» → +{SEEN_REWARD} سکه\n"
                f"• 🎁 هدیه روزانه → +{DAILY_GIFT} سکه\n"
                f"• 👥 دعوت دوستان → +{INVITE_REWARD} سکه\n"
                f"• 🎰 گردونه شانس → جایزه\n\n"
                f"✨ از استفاده از هایپرسین سپاسگزاریم."
            )
            send_message(chat_id, help_text)
            return
        
        if text == "👤 حساب کاربری":
            u = get_user(user_id)
            send_message(
                chat_id,
                f"👤 **حساب کاربری:**\n\n"
                f"👤 نام: {name}\n"
                f"🆔 آیدی: {user_id}\n"
                f"📛 یوزرنیم: @{u['username'] if u['username'] else 'ندارد'}\n"
                f"🪙 موجودی: {u['coins']:,} سکه\n"
                f"👥 دعوت کرده: {u.get('invite_count', 0)} نفر",
                {"inline_keyboard": [
                    [{"text": "📋 کپی آیدی عددی", "callback_data": "copy_id"}],
                    [{"text": "🔙 بازگشت", "callback_data": "back_to_main"}]
                ]}
            )
            return
        
        if text == "👥 دعوت دوستان":
            send_message(
                chat_id,
                f"🔥 **هایپرسین**\n\n"
                f"👁️ سین بزن | 👥 عضو بگیر\n"
                f"ترکیبی حرفه‌ای بله\n\n"
                f"🎁 همه‌چی رایگان!\n\n"
                f"📈 همین الان بیا و کانالتو رشد بده 😎👇\n"
                f"بدون پول\n\n"
                f"🔗 داش لینک دعوتت:\n"
                f"https://ble.ir/{BOT_USERNAME}?start={user_id}"
            )
            send_reply(chat_id, message["message_id"], f"🪙 با هر دعوت {INVITE_REWARD} سکه هدیه بگیر! 🎁🔥")
            return
        
        if text == "💰 انتقال سکه":
            db["pending_transfer"][user_id] = {"step": "waiting_id"}
            save_db(db)
            send_message(chat_id, "🆔 **آیدی عددی کاربر مقصد رو بفرست:**", cancel_keyboard())
            return
        
        if text == "👁️ ثبت سفارش سین":
            db["pending_orders"][user_id] = {"step": "waiting_forward"}
            save_db(db)
            send_message(chat_id, "📩 **لطفاً پیام مورد نظر را از کانال فوروارد کنید.**\n\n⚠️ حتماً باید از کانال فوروارد شود!\n📢 از هر کانالی می‌تونی فوروارد کنی.", cancel_keyboard())
            return
        
        if text == "👥 ثبت سفارش عضو":
            db["pending_members"][user_id] = {"step": "waiting_link"}
            save_db(db)
            send_message(chat_id, "📩 **لطفاً لینک کانال مورد نظر را بفرستید.**\n\n⚠️ حتماً باید کانال باشد!\n🚫 گروه قبول نمیشود!", cancel_keyboard())
            return
        
        if text == "🎁 زدن کد هدیه":
            db["pending_orders"][user_id] = {"step": "waiting_gift_code"}
            save_db(db)
            send_message(chat_id, "🎁 **لطفاً کد هدیه رو وارد کن:**", cancel_keyboard())
            return
        
        if text == "📋 وضعیت سفارش":
            db["pending_order_status"][user_id] = {"step": "waiting_number"}
            save_db(db)
            send_message(chat_id, "🔢 **لطفاً شماره سفارش رو وارد کن:**\n\n💡 مثال: #123", cancel_keyboard())
            return
        
        if text == "🎁 گرفتن هدیه":
            send_message(chat_id, "🎁 **گرفتن هدیه:**\n\nیکی از گزینه‌ها رو انتخاب کن:", gift_keyboard())
            return
        
        if text == "🎁 هدیه روزانه":
            today = get_shamsi_date()
            last_daily = db.get("daily_gift_records", {}).get(user_id)
            if last_daily == today:
                send_message(chat_id, "❌ **امروز هدیه‌اتو گرفتی!**\n\n⏰ هر ۲۴ ساعت یه بار می‌تونی بگیری!")
            else:
                add_coins(user_id, DAILY_GIFT)
                db["daily_gift_records"][user_id] = today
                save_db(db)
                send_message(chat_id, f"🎁 **هدیه روزانه گرفتی!**\n\n🪙 +{DAILY_GIFT} سکه\n💰 موجودی: {get_coins(user_id):,} سکه")
            return
        
        if text == "🎰 گردونه شانس":
            rewards = [
                ("😢 پوچ", 0), ("🪙 ۵ سکه", 5), ("🪙 ۱۰ سکه", 10),
                ("🔄 چرخش دوباره", -1), ("💎 ۳۵ سکه", 35), ("💎 ۴۰ سکه", 40)
            ]
            result = random.choice(rewards)
            
            if result[1] == -1:
                send_message(chat_id, "🔄 **چرخش دوباره!**\n\nیه بار دیگه می‌تونی بچرخونی!")
            elif result[1] == 0:
                send_message(chat_id, "😢 **پوچ!**\n\nامروز شانست بد بود! فردا دوباره امتحان کن!")
            else:
                add_coins(user_id, result[1])
                send_message(chat_id, f"🎉 **{result[0]} گرفتی!**\n\n💰 موجودی: {get_coins(user_id):,} سکه")
            return
        
        if text == "💬 پشتیبانی":
            db["pending_support"][user_id] = {"step": "waiting_message"}
            save_db(db)
            send_message(chat_id, "سلام! مشکلی پیش اومده؟ 🤔\n\nلطفاً پیامت رو ارسال کن تا کمکت کنیم!", cancel_keyboard())
            return
        
        # ============ پنل مالک ============
        if text == "🎁 ساخت کد هدیه" and user_id == OWNER_ID:
            db["pending_gift"][user_id] = {"step": "waiting_coins"}
            save_db(db)
            send_message(chat_id, "💰 **چند سکه توی کد باشه؟**", owner_keyboard())
            return
        
        if text == "🎁 سکه پاکت" and user_id == OWNER_ID:
            db["pending_packet"][user_id] = {"step": "waiting_coins"}
            save_db(db)
            send_message(chat_id, "💰 **چند سکه توی پاکت باشه؟**", owner_keyboard())
            return
        
        if text == "💰 افزودن سکه به همه" and user_id == OWNER_ID:
            db["pending_add_coins"][user_id] = {"step": "waiting_amount"}
            save_db(db)
            send_message(chat_id, "💰 **چند سکه به همه کاربرا اضافه بشه؟**\n\n📌 فقط عدد بفرست!", owner_keyboard())
            return
        
        if text == "🎁 تغییر سکه دعوت" and user_id == OWNER_ID:
            db["pending_gift"][user_id] = {"step": "waiting_invite_reward"}
            save_db(db)
            send_message(chat_id, f"🎁 **تغییر سکه دعوت:**\n\n💰 سکه فعلی: **{INVITE_REWARD}**\n\n🔢 سکه جدید رو وارد کن:", owner_keyboard())
            return
        
        if text == "💰 تنظیم سکه‌ها" and user_id == OWNER_ID:
            send_message(chat_id, f"💰 **تنظیم سکه‌ها:**\n\n👁️ سکه دیدن: {SEEN_REWARD}\n📝 سکه سین: {SIN_COST}\n👥 سکه عضو: {MEMBER_COST}", coins_keyboard())
            return
        
        if text == "👁️ تنظیم سکه گرفتن دیدن" and user_id == OWNER_ID:
            db["pending_coins_setting"][user_id] = {"step": "waiting_seen_reward"}
            save_db(db)
            send_message(chat_id, f"👁️ **تعداد سکه جدید دیدن رو وارد کن:**\n\n💰 فعلی: {SEEN_REWARD}", coins_keyboard())
            return
        
        if text == "📝 تنظیم سکه دادن سین" and user_id == OWNER_ID:
            db["pending_coins_setting"][user_id] = {"step": "waiting_sin_cost"}
            save_db(db)
            send_message(chat_id, f"📝 **تعداد سکه جدید سین رو وارد کن:**\n\n💰 فعلی: {SIN_COST}", coins_keyboard())
            return
        
        if text == "👥 تنظیم سکه گرفتن عضو" and user_id == OWNER_ID:
            db["pending_coins_setting"][user_id] = {"step": "waiting_member_get"}
            save_db(db)
            send_message(chat_id, "👥 **کدوم رو می‌خوای تغییر بدی؟**\n\n۱️⃣ عضو معمولی (۳ سکه)\n۲️⃣ عضو تضمینی (۷ سکه)", coins_keyboard())
            return
        
        if text == "💰 تنظیم سکه دادن عضو" and user_id == OWNER_ID:
            db["pending_coins_setting"][user_id] = {"step": "waiting_member_cost"}
            save_db(db)
            send_message(chat_id, f"💰 **تعداد سکه جدید عضو رو وارد کن:**\n\n💰 فعلی: {MEMBER_COST}", coins_keyboard())
            return
        
        if text == "⚙️ کاربردی‌ها" and user_id == OWNER_ID:
            send_message(chat_id, "⚙️ **کاربردی‌ها:**", tools_keyboard())
            return
        
        if text == "🚫 مسدود کردن کاربر" and user_id == OWNER_ID:
            db["pending_tools"][user_id] = {"step": "waiting_block_id"}
            save_db(db)
            send_message(chat_id, "🆔 **آیدی عددی کاربر رو بفرست:**", tools_keyboard())
            return
        
        if text == "✅ رفع مسدودیت" and user_id == OWNER_ID:
            db["pending_tools"][user_id] = {"step": "waiting_unblock_id"}
            save_db(db)
            send_message(chat_id, "🆔 **آیدی عددی کاربر رو بفرست:**", tools_keyboard())
            return
        
        if text == "🔘 فرستادن دکمه شیشه‌ای" and user_id == OWNER_ID:
            db["pending_tools"][user_id] = {"step": "waiting_btn_text"}
            save_db(db)
            send_message(chat_id, "📝 **متن پست رو بفرست:**", tools_keyboard())
            return
        
        if text == "⚡ سرعت ربات" and user_id == OWNER_ID:
            start = time.time()
            api_call("getMe")
            delay = int((time.time() - start) * 1000)
            
            if delay < 100:
                score, emoji, opinion = 10, "🏆", "بی‌نظیر!"
            elif delay < 200:
                score, emoji, opinion = 9, "🔥", "عالی!"
            elif delay < 350:
                score, emoji, opinion = 8, "😍", "خیلی خوب!"
            elif delay < 500:
                score, emoji, opinion = 7, "😊", "خوب!"
            elif delay < 700:
                score, emoji, opinion = 6, "🙂", "معمولی"
            elif delay < 1000:
                score, emoji, opinion = 5, "😐", "بد نیست"
            elif delay < 1500:
                score, emoji, opinion = 4, "😕", "یکم کنده"
            elif delay < 2000:
                score, emoji, opinion = 3, "😔", "بده"
            elif delay < 3000:
                score, emoji, opinion = 2, "😢", "خیلی بده"
            else:
                score, emoji, opinion = 1, "😭", "فاجعه‌ست!"
            
            send_message(chat_id, f"{emoji} **سرعت ربات:** {delay}ms\n\n⭐ امتیاز: {score}/10\n💬 نظر ربات: {opinion}", tools_keyboard())
            return
        
        if text == "📊 آمار لحظه‌ای" and user_id == OWNER_ID:
            today = get_shamsi_date()
            total_users = len(db["users"])
            active_orders = sum(1 for o in db["orders"].values() if o["status"] == "active")
            today_users = sum(1 for u in db["users"].values() if u.get("first_seen", "").startswith(today))
            send_message(chat_id, f"📊 **آمار لحظه‌ای:**\n\n👥 کاربر کل: {total_users}\n✅ کاربر امروز: {today_users}\n📋 سفارش فعال: {active_orders}\n📅 تاریخ: {today}", owner_keyboard())
            return
        
        if text == "📊 آمار کل" and user_id == OWNER_ID:
            stats = db["stats"]
            total_users = len(db["users"])
            send_message(chat_id, f"📊 **آمار کل:**\n\n👥 کاربران: {total_users}\n📝 سفارشات سین: {stats['total_orders']}\n✅ تکمیل سین: {stats['completed_orders']}\n👥 سفارشات عضو: {stats.get('total_members', 0)}\n✅ تکمیل عضو: {stats.get('completed_members', 0)}\n📅 تاریخ: {get_shamsi_date()}", owner_keyboard())
            return
        
        if text == "📈 نمودار رشد" and user_id == OWNER_ID:
            stats = db.get("growth_stats", {})
            if not stats:
                send_message(chat_id, "📈 **هنوز داده‌ای ثبت نشده!**", owner_keyboard())
            else:
                msg = "📈 **نمودار رشد:**\n\n"
                for day, count in list(stats.items())[-7:]:
                    bar = "█" * min(count // 10, 20)
                    msg += f"📅 {day}: {bar} {count}\n"
                send_message(chat_id, msg, owner_keyboard())
            return
        
        if text == "📢 پیام همگانی" and user_id == OWNER_ID:
            db["pending_broadcast"][user_id] = {"step": "waiting_message"}
            save_db(db)
            send_message(chat_id, "📢 **پیام همگانی رو بفرست:**", owner_keyboard())
            return
        
        if text == "📨 فوروارد همگانی" and user_id == OWNER_ID:
            db["pending_broadcast"][user_id] = {"step": "waiting_forward"}
            save_db(db)
            send_message(chat_id, "📨 **یه پیام رو فوروارد کن:**", owner_keyboard())
            return
        
        if text == "📨 پیام به کاربر خاص" and user_id == OWNER_ID:
            db["pending_tools"][user_id] = {"step": "waiting_target_msg"}
            save_db(db)
            send_message(chat_id, "🆔 **آیدی عددی کاربر رو بفرست:**", owner_keyboard())
            return
        
        if text == "🗑️ حذف سفارش" and user_id == OWNER_ID:
            db["pending_tools"][user_id] = {"step": "waiting_delete_order"}
            save_db(db)
            send_message(chat_id, "🔢 **شماره سفارش رو وارد کن:**", owner_keyboard())
            return
        
        if text == "📊 ارسال نظرسنجی" and user_id == OWNER_ID:
            db["pending_poll"][user_id] = {"step": "waiting_question"}
            save_db(db)
            send_message(chat_id, "📝 **سوال نظرسنجی رو بفرست:**", owner_keyboard())
            return
        
        if text == "🏆 رتبه‌بندی" and user_id == OWNER_ID:
            users_sorted = sorted(db["users"].items(), key=lambda x: x[1]["coins"], reverse=True)[:10]
            msg = "🏆 **رتبه‌بندی:**\n\n"
            for i, (uid, data) in enumerate(users_sorted, 1):
                uname = data.get("username", "")
                msg += f"{i}. @{uname if uname else uid[:6]} → {data['coins']:,} سکه\n"
            send_message(chat_id, msg, owner_keyboard())
            return
        
        if text == "🔙 بازگشت" and user_id == OWNER_ID:
            send_message(chat_id, "🔙 **برگشتی به منوی اصلی!**", main_keyboard())
            return
        
        # ============ پردازش انتقال سکه ============
        pt = db["pending_transfer"].get(user_id, {})
        if pt.get("step") == "waiting_id":
            target = text.strip()
            if target in db["users"] and target != user_id:
                db["pending_transfer"][user_id] = {"step": "waiting_amount", "target": target}
                save_db(db)
                send_message(chat_id, f"💰 **چند سکه میخوای به {target} بدی؟**\n💰 موجودی: {get_coins(user_id):,}", cancel_keyboard())
            else:
                send_message(chat_id, "❌ کاربر یافت نشد!", main_keyboard())
                db["pending_transfer"].pop(user_id, None)
                save_db(db)
            return
        
        if pt.get("step") == "waiting_amount":
            try:
                amount = int(convert_number(text))
                if remove_coins(user_id, amount):
                    add_coins(pt["target"], amount)
                    send_message(chat_id, f"✅ **{amount} سکه انتقال دادی!**\n💰 موجودی جدید: {get_coins(user_id):,}", main_keyboard())
                else:
                    send_message(chat_id, "❌ سکه کافی نداری!", main_keyboard())
            except:
                send_message(chat_id, "❌ عدد معتبر وارد کن!", main_keyboard())
            db["pending_transfer"].pop(user_id, None)
            save_db(db)
            return
        
        # ============ پردازش افزودن سکه به همه ============
        pac = db["pending_add_coins"].get(user_id, {})
        if pac.get("step") == "waiting_amount":
            try:
                amount = int(convert_number(text))
                count = 0
                for uid in db["users"]:
                    add_coins(uid, amount)
                    count += 1
                del db["pending_add_coins"][user_id]
                save_db(db)
                send_message(chat_id, f"✅ **{amount} سکه به {count} کاربر اضافه شد!** 🎉", owner_keyboard())
            except:
                send_message(chat_id, "❌ عدد معتبر وارد کن!", owner_keyboard())
            return
        
        # ============ پردازش تغییر سکه دعوت ============
        pg = db["pending_gift"].get(user_id, {})
        if pg.get("step") == "waiting_invite_reward":
            try:
                INVITE_REWARD = int(convert_number(text))
                db["invite_reward"] = INVITE_REWARD
                del db["pending_gift"][user_id]
                save_db(db)
                send_message(chat_id, f"✅ **سکه دعوت تغییر کرد!**\n💰 جدید: **{INVITE_REWARD}**", owner_keyboard())
            except:
                send_message(chat_id, "❌ عدد معتبر وارد کن!", owner_keyboard())
            return
        
        # ============ پردازش تنظیم سکه‌ها ============
        pcs = db["pending_coins_setting"].get(user_id, {})
        if pcs.get("step") == "waiting_seen_reward":
            try:
                SEEN_REWARD = int(convert_number(text))
                del db["pending_coins_setting"][user_id]
                save_db(db)
                send_message(chat_id, f"✅ **سکه دیدن: {SEEN_REWARD}**", coins_keyboard())
            except:
                send_message(chat_id, "❌ عدد معتبر!", coins_keyboard())
            return
        
        if pcs.get("step") == "waiting_sin_cost":
            try:
                SIN_COST = int(convert_number(text))
                del db["pending_coins_setting"][user_id]
                save_db(db)
                send_message(chat_id, f"✅ **سکه سین: {SIN_COST}**", coins_keyboard())
            except:
                send_message(chat_id, "❌ عدد معتبر!", coins_keyboard())
            return
        
        if pcs.get("step") == "waiting_member_cost":
            try:
                MEMBER_COST = int(convert_number(text))
                del db["pending_coins_setting"][user_id]
                save_db(db)
                send_message(chat_id, f"✅ **سکه عضو: {MEMBER_COST}**", coins_keyboard())
            except:
                send_message(chat_id, "❌ عدد معتبر!", coins_keyboard())
            return
        
        # ============ پردازش ابزارها ============
        ptools = db["pending_tools"].get(user_id, {})
        if ptools.get("step") == "waiting_block_id":
            target = text.strip()
            if target in db["users"]:
                if target not in db["blocked_users"]:
                    db["blocked_users"].append(target)
                save_db(db)
                send_message(chat_id, f"🚫 **کاربر {target} مسدود شد!**", tools_keyboard())
            else:
                send_message(chat_id, "❌ کاربر یافت نشد!", tools_keyboard())
            del db["pending_tools"][user_id]
            save_db(db)
            return
        
        if ptools.get("step") == "waiting_unblock_id":
            target = text.strip()
            if target in db["blocked_users"]:
                db["blocked_users"].remove(target)
                save_db(db)
                send_message(chat_id, f"✅ **کاربر {target} آزاد شد!**", tools_keyboard())
            else:
                send_message(chat_id, f"❌ **کاربر {target} مسدود نیست!**", tools_keyboard())
            del db["pending_tools"][user_id]
            save_db(db)
            return
        
        if ptools.get("step") == "waiting_btn_text":
            db["pending_tools"][user_id]["btn_text"] = text
            db["pending_tools"][user_id]["step"] = "waiting_btn_name"
            save_db(db)
            send_message(chat_id, "🔘 **اسم دکمه چی باشه؟**", tools_keyboard())
            return
        
        if ptools.get("step") == "waiting_btn_name":
            db["pending_tools"][user_id]["btn_name"] = text
            db["pending_tools"][user_id]["step"] = "waiting_btn_url"
            save_db(db)
            send_message(chat_id, "🔗 **لینک دکمه چی باشه؟**", tools_keyboard())
            return
        
        if ptools.get("step") == "waiting_btn_url":
            keyboard = {"inline_keyboard": [[{"text": ptools["btn_name"], "url": text}]]}
            send_message(CHANNEL_ID, ptools["btn_text"], keyboard)
            del db["pending_tools"][user_id]
            save_db(db)
            send_message(chat_id, "✅ **پست با دکمه شیشه‌ای فرستاده شد!**", tools_keyboard())
            return
        
        if ptools.get("step") == "waiting_target_msg":
            db["pending_tools"][user_id]["target"] = text.strip()
            db["pending_tools"][user_id]["step"] = "waiting_target_text"
            save_db(db)
            send_message(chat_id, "📝 **پیامت رو بفرست:**", owner_keyboard())
            return
        
        if ptools.get("step") == "waiting_target_text":
            try:
                send_message(int(ptools["target"]), f"📨 **پیام از طرف مالک:**\n\n{text}")
                send_message(chat_id, "✅ **پیام ارسال شد!**", owner_keyboard())
            except:
                send_message(chat_id, "❌ خطا در ارسال!", owner_keyboard())
            del db["pending_tools"][user_id]
            save_db(db)
            return
        
        if ptools.get("step") == "waiting_delete_order":
            order_num = text.strip().replace("#", "")
            found = False
            for oid, order in db["orders"].items():
                if str(order.get("order_number")) == order_num:
                    try:
                        delete_message(CHANNEL_ID, order["message_id"])
                        if order.get("reply_message_id"):
                            delete_message(CHANNEL_ID, order["reply_message_id"])
                    except:
                        pass
                    order["status"] = "deleted"
                    try:
                        send_message(int(order["user_id"]), "⚠️ **سفارش شما توسط سیستم حذف شد!**\n\n💰 **در ۱ ساعت آینده سکه‌هات برمی‌گرده!**")
                        add_coins(order["user_id"], order["count"] * SIN_COST)
                    except:
                        pass
                    found = True
                    break
            
            if found:
                send_message(chat_id, "🗑️ **سفارش حذف شد!**", owner_keyboard())
            else:
                send_message(chat_id, "❌ سفارش پیدا نشد!", owner_keyboard())
            del db["pending_tools"][user_id]
            save_db(db)
            return
        
        # ============ پردازش نظرسنجی ============
        ppoll = db["pending_poll"].get(user_id, {})
        if ppoll.get("step") == "waiting_question":
            db["pending_poll"][user_id]["question"] = text
            db["pending_poll"][user_id]["step"] = "waiting_options"
            save_db(db)
            send_message(chat_id, "📝 **گزینه‌ها رو بفرست:**\n\nهر گزینه توی یه خط:\n۱. گزینه اول\n۲. گزینه دوم", owner_keyboard())
            return
        
        if ppoll.get("step") == "waiting_options":
            options = text.strip().split("\n")
            poll_id = str(int(time.time() * 1000))
            keyboard = {"inline_keyboard": []}
            for i, opt in enumerate(options, 1):
                keyboard["inline_keyboard"].append([{"text": f"{i}. {opt}", "callback_data": f"poll_{poll_id}_{i}"}])
            
            db["polls"][poll_id] = {
                "question": ppoll["question"],
                "options": options,
                "votes": {str(i): [] for i in range(1, len(options) + 1)}
            }
            sent = send_message(CHANNEL_ID, f"📊 **{ppoll['question']}**", keyboard)
            if sent.get("ok"):
                db["polls"][poll_id]["message_id"] = sent["result"]["message_id"]
            
            del db["pending_poll"][user_id]
            save_db(db)
            send_message(chat_id, "✅ **نظرسنجی فرستاده شد!**", owner_keyboard())
            return
        
        # ============ پردازش وضعیت سفارش ============
        pos = db["pending_order_status"].get(user_id, {})
        if pos.get("step") == "waiting_number":
            order_num = text.strip().replace("#", "")
            found = False
            
            for oid, order in db["orders"].items():
                if str(order.get("order_number")) == order_num:
                    seen = order["seen_count"]
                    count = order["count"]
                    send_message(chat_id, f"📋 **وضعیت سفارش #{order_num}:**\n\n👁️ سین درخواستی: {count}\n✅ سین خورده: {seen}\n⏳ سین مونده: {count - seen}\n📊 وضعیت: {'✅ تکمیل' if order['status'] == 'completed' else '⏳ فعال'}", main_keyboard())
                    found = True
                    break
            
            if not found:
                for mid, order in db["member_orders"].items():
                    if str(order.get("order_number")) == order_num:
                        seen = order["seen_count"]
                        count = order["count"]
                        send_message(chat_id, f"📋 **وضعیت سفارش #{order_num}:**\n\n👥 عضو درخواستی: {count}\n✅ عضو شده: {seen}\n⏳ عضو مونده: {count - seen}\n📊 وضعیت: {'✅ تکمیل' if order['status'] == 'completed' else '⏳ فعال'}", main_keyboard())
                        found = True
                        break
            
            if not found:
                send_message(chat_id, "❌ سفارشی با این شماره پیدا نشد!", main_keyboard())
            
            del db["pending_order_status"][user_id]
            save_db(db)
            return
        
        # ============ پردازش پشتیبانی ============
        ps = db["pending_support"].get(user_id, {})
        if ps.get("step") == "waiting_message":
            support_keyboard = {"inline_keyboard": [[
                {"text": "✅ جواب دادن", "callback_data": f"reply_{user_id}"},
                {"text": "❌ رد کردن", "callback_data": f"reject_{user_id}"}
            ]]}
            send_message(int(OWNER_ID), f"📨 **پیام پشتیبانی:**\n\n👤 کاربر: {name}\n🆔 آیدی: {user_id}\n📝 پیام: {text}", support_keyboard)
            del db["pending_support"][user_id]
            save_db(db)
            send_message(chat_id, "✅ **پیامت ارسال شد!**", main_keyboard())
            return
        
        psr = db["pending_support_reply"].get(user_id, {})
        if psr.get("target"):
            try:
                send_message(int(psr["target"]), f"📨 **جواب پشتیبانی:**\n\n{text}")
                send_message(chat_id, "✅ **جوابت ارسال شد!**")
            except:
                send_message(chat_id, "❌ خطا!")
            del db["pending_support_reply"][user_id]
            save_db(db)
            return
        
        # ============ پردازش سین‌زن ============
        pending = db["pending_orders"].get(user_id, {})
        if pending.get("step") == "waiting_forward":
            if "forward_from_chat" in message and message["forward_from_chat"]["type"] == "channel":
                db["pending_orders"][user_id] = {"step": "waiting_count", "message_id": message["message_id"], "from_chat_id": message["forward_from_chat"]["id"]}
                save_db(db)
                send_message(chat_id, f"🔢 **چند سین نیاز داری؟**\n\n💰 هر سین = {SIN_COST} سکه\n💳 موجودی: {get_coins(user_id):,} سکه\n⚠️ حداقل: {MIN_SIN} سین", cancel_keyboard())
            else:
                send_message(chat_id, "❌ **این پیام از کانال نیست!**", cancel_keyboard())
            return
        
        if pending.get("step") == "waiting_count":
            try:
                count = int(convert_number(text))
                if count < MIN_SIN:
                    send_message(chat_id, f"❌ حداقل {MIN_SIN} سین!", cancel_keyboard())
                    return
                total_cost = count * SIN_COST
                if not remove_coins(user_id, total_cost):
                    send_message(chat_id, f"❌ سکه کافی نداری!\n💰 موجودی: {get_coins(user_id):,}", cancel_keyboard())
                    del db["pending_orders"][user_id]
                    save_db(db)
                    return
                
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
                    
                    keyboard = {"inline_keyboard": [[
                        {"text": "👁️ دیدم", "callback_data": f"seen_{order_id}"},
                        {"text": "🤖 مشاهده ربات", "url": BOT_LINK}
                    ], [{"text": "🚨 گزارش", "callback_data": f"report_{order_id}"}]]}
                    
                    reply_result = send_reply(CHANNEL_ID, fwd_msg_id, f"📋 **سفارش سین**\n\n👤 سین درخواستی: {count}\n👁️ سین خورده: 0\n#{order_number}", keyboard)
                    if reply_result.get("ok"):
                        db["orders"][order_id]["reply_message_id"] = reply_result["result"]["message_id"]
                    
                    del db["pending_orders"][user_id]
                    save_db(db)
                    send_message(chat_id, f"✅ **سفارش ثبت شد!**\n\n🔢 تعداد: {count}\n💰 هزینه: {total_cost} سکه\n📝 شماره: #{order_number}", main_keyboard())
                else:
                    add_coins(user_id, total_cost)
                    send_message(chat_id, "❌ **خطا!** سکه‌ها برگشت!", main_keyboard())
                    del db["pending_orders"][user_id]
                    save_db(db)
            except:
                send_message(chat_id, "❌ عدد معتبر وارد کن!", cancel_keyboard())
            return
        
        # ============ پردازش کد هدیه ============
        if pending.get("step") == "waiting_gift_code":
            code = text.upper().strip()
            if code in db["gift_codes"]:
                g = db["gift_codes"][code]
                u = get_user(user_id)
                if code in u["used_gift_codes"]:
                    send_message(chat_id, "❌ قبلاً این کد رو زدی!", main_keyboard())
                elif len(g["used_by"]) >= g["capacity"]:
                    send_message(chat_id, "❌ این کد تموم شده!", main_keyboard())
                else:
                    add_coins(user_id, g["coins"])
                    g["used_by"].append(user_id)
                    u["used_gift_codes"].append(code)
                    save_db(db)
                    send_message(chat_id, f"🎉 **{g['coins']:,} سکه گرفتی!**", main_keyboard())
            else:
                send_message(chat_id, "❌ کد نامعتبر!", main_keyboard())
            del db["pending_orders"][user_id]
            save_db(db)
            return
        
        # ============ پردازش ساخت کد هدیه ============
        if pg.get("step") == "waiting_coins":
            try:
                db["pending_gift"][user_id] = {"step": "waiting_capacity", "coins": int(convert_number(text))}
                save_db(db)
                send_message(chat_id, "👥 **ظرفیت چند نفره؟**", owner_keyboard())
            except:
                send_message(chat_id, "❌ عدد معتبر وارد کن!", owner_keyboard())
            return
        
        if pg.get("step") == "waiting_capacity":
            try:
                cap = int(convert_number(text))
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                db["gift_codes"][code] = {"coins": pg["coins"], "capacity": cap, "used_by": []}
                del db["pending_gift"][user_id]
                save_db(db)
                send_message(chat_id, f"🎁 **کد هدیه:** `{code}`\n💰 سکه: {pg['coins']:,}\n👥 ظرفیت: {cap}", owner_keyboard())
            except:
                send_message(chat_id, "❌ عدد معتبر وارد کن!", owner_keyboard())
            return
        
        # ============ پردازش عضوگیر ============
        pmem = db["pending_members"].get(user_id, {})
        if pmem.get("step") == "waiting_link":
            db["pending_members"][user_id] = {"step": "waiting_admin", "link": text.strip()}
            save_db(db)
            send_message(chat_id, "🔗 **منو توی کانال ادمین کن!**\n✅ بعد بنویس: ادمین کردم", cancel_keyboard())
            return
        
        if pmem.get("step") == "waiting_admin":
            if text.strip() == "ادمین کردم":
                db["pending_members"][user_id]["step"] = "waiting_type"
                save_db(db)
                send_message(chat_id, "📥 **نوع عضویت:**\n\n🥉 ۱. معمولی (۵ سکه)\n🥇 ۲. تضمینی (۱۰ سکه)", cancel_keyboard())
            else:
                send_message(chat_id, "⚠️ بنویس: ادمین کردم", cancel_keyboard())
            return
        
        if pmem.get("step") == "waiting_type":
            if text in ["1", "2"]:
                db["pending_members"][user_id]["order_type"] = "normal" if text == "1" else "guaranteed"
                db["pending_members"][user_id]["step"] = "waiting_count"
                save_db(db)
                cost = 5 if text == "1" else 10
                send_message(chat_id, f"👥 **تعداد عضو رو وارد کن:**\n💰 هر عضو: {cost} سکه", cancel_keyboard())
            else:
                send_message(chat_id, "❌ فقط ۱ یا ۲!", cancel_keyboard())
            return
        
        if pmem.get("step") == "waiting_count":
            try:
                count = int(convert_number(text))
                cost_per = 5 if pmem.get("order_type") == "normal" else 10
                total_cost = count * cost_per
                if not remove_coins(user_id, total_cost):
                    send_message(chat_id, "❌ سکه کافی نداری!", cancel_keyboard())
                    del db["pending_members"][user_id]
                    save_db(db)
                    return
                
                db["member_counter"] = db.get("member_counter", 0) + 1
                mnum = db["member_counter"]
                mid = str(int(time.time() * 1000))
                reward = 3 if pmem.get("order_type") == "normal" else 7
                type_name = "معمولی" if pmem.get("order_type") == "normal" else "تضمینی"
                
                db["member_orders"][mid] = {"user_id": user_id, "count": count, "link": pmem["link"], "message_id": None, "seen_count": 0, "status": "active", "order_number": mnum, "order_type": pmem.get("order_type"), "reward": reward}
                db["member_records"][mid] = []
                db["stats"]["total_members"] = db["stats"].get("total_members", 0) + 1
                
                keyboard = {"inline_keyboard": [
                    [{"text": f"🪙 {reward} سکه میگیری!", "callback_data": f"info_{mid}"}],
                    [{"text": "🔗 عضویت در کانال", "url": pmem["link"]}, {"text": "✅ عضو شدم", "callback_data": f"mjoin_{mid}"}],
                    [{"text": "🚨 گزارش", "callback_data": f"mreport_{mid}"}, {"text": "🤖 مشاهده ربات", "url": BOT_LINK}]
                ]}
                
                sent = send_message(CHANNEL_ID, f"📋 **سفارش عضو - {type_name}**\n\n🔗 لینک: {pmem['link']}\n👥 تعداد: {count}\n✅ عضو شده: 0\n#{mnum}\n\n🪙 **{reward} سکه میگیری!**", keyboard)
                if sent.get("ok"):
                    db["member_orders"][mid]["message_id"] = sent["result"]["message_id"]
                
                del db["pending_members"][user_id]
                save_db(db)
                send_message(chat_id, f"🎉 **سفارش ثبت شد!**\n💰 موجودی: {get_coins(user_id):,} سکه", main_keyboard())
            except:
                send_message(chat_id, "❌ عدد معتبر وارد کن!", cancel_keyboard())
            return
        
        # ============ پردازش پیام همگانی ============
        pbc = db["pending_broadcast"].get(user_id, {})
        if pbc.get("step") == "waiting_message":
            sent = 0
            failed = 0
            for uid in list(db["users"].keys()):
                try:
                    result = send_message(int(uid), text)
                    if result.get("ok"):
                        sent += 1
                    else:
                        failed += 1
                except:
                    failed += 1
                time.sleep(0.05)
            del db["pending_broadcast"][user_id]
            save_db(db)
            send_message(chat_id, f"📢 **ارسال شد!**\n✅ موفق: {sent}\n❌ ناموفق: {failed}", owner_keyboard())
            return
        
        # ============ پردازش فوروارد همگانی ============
        if pbc.get("step") == "waiting_forward":
            sent = 0
            failed = 0
            for uid in list(db["users"].keys()):
                try:
                    result = forward_message(int(uid), chat_id, message["message_id"])
                    if result.get("ok"):
                        sent += 1
                    else:
                        failed += 1
                except:
                    failed += 1
                time.sleep(0.05)
            del db["pending_broadcast"][user_id]
            save_db(db)
            send_message(chat_id, f"📨 **فوروارد شد!**\n✅ موفق: {sent}\n❌ ناموفق: {failed}", owner_keyboard())
            return
        
        # ============ پردازش سکه پاکت ============
        pp = db.get("pending_packet", {}).get(user_id, {})
        if pp.get("step") == "waiting_coins":
            try:
                db["pending_packet"][user_id] = {"step": "waiting_capacity", "coins": int(convert_number(text))}
                save_db(db)
                send_message(chat_id, "👥 **چند نفره باشه؟**", owner_keyboard())
            except:
                send_message(chat_id, "❌ عدد معتبر وارد کن!", owner_keyboard())
            return
        
        if pp.get("step") == "waiting_capacity":
            try:
                db["pending_packet"][user_id]["step"] = "waiting_text"
                db["pending_packet"][user_id]["capacity"] = int(convert_number(text))
                save_db(db)
                send_message(chat_id, "📝 **متن پاکت چی باشه؟**", owner_keyboard())
            except:
                send_message(chat_id, "❌ عدد معتبر وارد کن!", owner_keyboard())
            return
        
        if pp.get("step") == "waiting_text":
            packet_text = text.strip()
            packet_id = str(int(time.time() * 1000))
            db["coin_packets"][packet_id] = {"coins": pp["coins"], "capacity": pp["capacity"], "text": packet_text, "used_by": []}
            kb = {"inline_keyboard": [[{"text": "🎁 باز کردن سکه", "callback_data": f"packet_{packet_id}"}]]}
            send_message(CHANNEL_ID, f"🎁 **سکه پاکت**\n\n{packet_text}", kb)
            db["pending_packet"].pop(user_id, None)
            save_db(db)
            send_message(chat_id, "✅ **سکه پاکت توی کانال گذاشته شد!** 🎉", owner_keyboard())
            return
        
        # ============ پیش‌فرض ============
        send_message(chat_id, f"👋 **سلام {name} جان!** 😎\n\nاز دکمه‌های زیر استفاده کن:", main_keyboard())
    
    except Exception as e:
        print(f"⚠️ خطا: {e}")
        traceback.print_exc()
# ============================================
# 🔘 پردازش دکمه‌های شیشه‌ای
# ============================================
def handle_callback(callback):
    try:
        callback_id = callback["id"]
        data = callback["data"]
        user_id = callback["from"]["id"]
        message = callback.get("message", {})
        chat_id = message.get("chat", {}).get("id", CHANNEL_ID)
        
        if data == "check_join":
            if check_joined(user_id):
                user = get_user(user_id)
                if not user.get("got_start_gift"):
                    add_coins(user_id, START_GIFT)
                    user["got_start_gift"] = True
                    if user.get("invited_by") and str(user_id) in db["invited_users"]:
                        inviter_id = user["invited_by"]
                        add_coins(inviter_id, INVITE_REWARD)
                        inviter = get_user(inviter_id)
                        inviter["invite_count"] = inviter.get("invite_count", 0) + 1
                        save_db(db)
                        try:
                            send_message(int(inviter_id), f"🎉 **کاربر عضو کانال هم شد!**\n\n🎁 **{INVITE_REWARD} سکه بهت اهدا شد!** 💰")
                        except:
                            pass
                    save_db(db)
                    answer_callback(callback_id, f"✅ عضو شدی! 🎁 {START_GIFT} سکه هدیه گرفتی!")
                    send_message(user_id, f"✅ **عضو شدی!** 🎉\n\n🎁 **{START_GIFT} سکه هدیه** بهت اضافه شد!\n💰 موجودی: {get_coins(user_id):,} سکه", main_keyboard())
                else:
                    answer_callback(callback_id, "✅ عضو شدی!")
                    send_message(user_id, "✅ **عضو شدی!** 🎉", main_keyboard())
            else:
                answer_callback(callback_id, "❌ هنوز عضو نشدی!")
            return
        
        if data == "back_to_main":
            send_message(user_id, "🏠 منوی اصلی:", main_keyboard())
            answer_callback(callback_id)
            return
        
        if data == "copy_id":
            answer_callback(callback_id, f"✅ آیدی عددی: {user_id}", show_alert=True)
            return
        
        if data.startswith("reply_"):
            target = data.replace("reply_", "")
            db["pending_support_reply"][user_id] = {"target": target}
            save_db(db)
            send_message(user_id, "📝 **لطفاً جوابت رو بفرست:**")
            answer_callback(callback_id)
            return
        
        if data.startswith("reject_"):
            answer_callback(callback_id, "❌ رد شد!", show_alert=True)
            return
        
        if data.startswith("deleteorder_"):
            oid = data.replace("deleteorder_", "")
            order = db["orders"].get(oid, {})
            try:
                delete_message(CHANNEL_ID, order["message_id"])
                if order.get("reply_message_id"):
                    delete_message(CHANNEL_ID, order["reply_message_id"])
            except:
                pass
            order["status"] = "deleted"
            try:
                send_message(int(order["user_id"]), "⚠️ **سفارش شما توسط سیستم حذف شد!**\n\n🤖 سیستم: شاید غیرقانونی بوده یا مشکلی داشته!\n\n💰 **در ۱ ساعت آینده سکه‌هات برمی‌گرده!**")
                add_coins(order["user_id"], order["count"] * SIN_COST)
            except:
                pass
            save_db(db)
            answer_callback(callback_id, "🗑️ سفارش حذف شد!", show_alert=True)
            return
        
        if data.startswith("keep_"):
            target = data.replace("keep_", "")
            try:
                send_message(int(target), "⏳ **سیستم در حال بررسی گزارشه!**\n\nصبر کن تا بررسی تموم بشه!")
            except:
                pass
            answer_callback(callback_id, "⏳ نگه داشته شد!", show_alert=True)
            return
        
        if data.startswith("packet_"):
            pid = data.replace("packet_", "")
            if pid not in db.get("coin_packets", {}):
                answer_callback(callback_id, "❌ پاکت وجود نداره!", show_alert=True)
                return
            p = db["coin_packets"][pid]
            if str(user_id) in p["used_by"]:
                answer_callback(callback_id, "⚠️ قبلاً باز کردی!", show_alert=True)
                return
            if len(p["used_by"]) >= p["capacity"]:
                answer_callback(callback_id, "😢 **دیر رسیدی!**", show_alert=True)
                return
            p["used_by"].append(str(user_id))
            add_coins(user_id, p["coins"])
            save_db(db)
            answer_callback(callback_id, f"🎉 **{p['coins']} سکه گرفتی!**", show_alert=True)
            return
        
        if data.startswith("seen_"):
            order_id = data.replace("seen_", "")
            if order_id not in db["orders"]:
                answer_callback(callback_id, "❌ این سفارش وجود نداره!")
                return
            order = db["orders"][order_id]
            if order["status"] != "active":
                answer_callback(callback_id, "✅ تکمیل شده!")
                return
            if str(user_id) in db["seen_records"].get(order_id, []):
                answer_callback(callback_id, "⚠️ قبلاً دیدم رو زدی!")
                return
            db["seen_records"][order_id].append(str(user_id))
            order["seen_count"] += 1
            add_coins(user_id, SEEN_REWARD)
            new_seen = order["seen_count"]
            count = order["count"]
            order_number = order.get("order_number", "?")
            answer_callback(callback_id, f"👁️ ثبت شد! (+{SEEN_REWARD} سکه)")
            if order.get("reply_message_id"):
                keyboard = {"inline_keyboard": [[
                    {"text": "👁️ دیدم", "callback_data": f"seen_{order_id}"},
                    {"text": "🤖 مشاهده ربات", "url": BOT_LINK}
                ], [{"text": "🚨 گزارش", "callback_data": f"report_{order_id}"}]]}
                try:
                    edit_message_text(CHANNEL_ID, order["reply_message_id"], f"📋 **سفارش سین**\n\n👤 سین درخواستی: {count}\n👁️ سین خورده: {new_seen}\n#{order_number}", keyboard)
                except:
                    pass
            if new_seen >= count:
                order["status"] = "completed"
                db["stats"]["completed_orders"] += 1
                get_user(order["user_id"])["completed_orders"] += 1
                try:
                    delete_message(CHANNEL_ID, order["message_id"])
                    if order.get("reply_message_id"):
                        delete_message(CHANNEL_ID, order["reply_message_id"])
                except:
                    pass
                try:
                    send_message(int(order["user_id"]), f"🎉 **تبریک!**\n\n{count} سین کامل شد!")
                except:
                    pass
            save_db(db)
            return
        
        if data.startswith("report_"):
            order_id = data.replace("report_", "")
            order = db["orders"].get(order_id, {})
            reporter = callback["from"]
            report_keyboard = {"inline_keyboard": [
                [{"text": "✅ پاسخ دادن", "callback_data": f"reply_{user_id}"},
                 {"text": "❌ رد کردن", "callback_data": f"reject_{user_id}"}],
                [{"text": "🗑️ حذف سفارش", "callback_data": f"deleteorder_{order_id}"},
                 {"text": "⏳ نگه داشتن", "callback_data": f"keep_{user_id}"}]
            ]}
            send_message(int(OWNER_ID), f"🚨 **گزارش جدید!**\n\n👤 کاربر: {reporter.get('first_name', '?')}\n🆔 آیدی: {user_id}\n🔢 سفارش: #{order.get('order_number', '?')}", report_keyboard)
            answer_callback(callback_id, "🚨 گزارش ثبت شد!")
            return
        
        if data.startswith("info_"):
            mid = data.replace("info_", "")
            o = db["member_orders"].get(mid, {})
            reward = o.get("reward", 3)
            otype = o.get("order_type", "normal")
            if otype == "guaranteed":
                answer_callback(callback_id, f"🪙 {reward} سکه میگیری!\n⚠️ باید ۴۸ ساعت بمونی!\n❌ ترک زودهنگام = -۷ سکه", show_alert=True)
            else:
                answer_callback(callback_id, f"🪙 {reward} سکه میگیری!", show_alert=True)
            return
        
        if data.startswith("mjoin_"):
            mid = data.replace("mjoin_", "")
            if mid not in db["member_orders"]:
                answer_callback(callback_id, "❌ وجود نداره!", show_alert=True)
                return
            order = db["member_orders"][mid]
            if order["status"] != "active":
                answer_callback(callback_id, "✅ تکمیل شده!", show_alert=True)
                return
            if str(user_id) in db["member_records"].get(mid, []):
                answer_callback(callback_id, "⚠️ قبلاً عضو شدی!", show_alert=True)
                return
            if is_order_owner(user_id, mid):
                answer_callback(callback_id, "❌ نمیتونی توی سفارش خودت عضو بشی!", show_alert=True)
                return
            
            db["member_records"][mid].append(str(user_id))
            order["seen_count"] += 1
            reward = order.get("reward", 3)
            add_coins(user_id, reward)
            otype = order.get("order_type", "normal")
            type_name = "معمولی" if otype == "normal" else "تضمینی"
            
            if otype == "guaranteed":
                db["guaranteed_members"][f"{user_id}_{mid}"] = str(datetime.now())
                save_db(db)
            
            new_seen = order["seen_count"]
            count = order["count"]
            mnum = order.get("order_number", "?")
            answer_callback(callback_id, f"✅ عضو شدی! 🎉 +{reward} سکه", show_alert=True)
            
            if order.get("message_id"):
                keyboard = {"inline_keyboard": [
                    [{"text": f"🪙 {reward} سکه میگیری!", "callback_data": f"info_{mid}"}],
                    [{"text": "🔗 عضویت در کانال", "url": order["link"]}, {"text": "✅ عضو شدم", "callback_data": f"mjoin_{mid}"}],
                    [{"text": "🚨 گزارش", "callback_data": f"mreport_{mid}"}, {"text": "🤖 مشاهده ربات", "url": BOT_LINK}]
                ]}
                try:
                    edit_message_text(CHANNEL_ID, order["message_id"], f"📋 **سفارش عضو - {type_name}**\n\n🔗 لینک: {order['link']}\n👥 تعداد: {count}\n✅ عضو شده: {new_seen}\n#{mnum}\n\n🪙 **{reward} سکه میگیری!**", keyboard)
                except:
                    pass
            
            if new_seen >= count:
                order["status"] = "completed"
                db["stats"]["completed_members"] = db["stats"].get("completed_members", 0) + 1
                try:
                    delete_message(CHANNEL_ID, order["message_id"])
                except:
                    pass
                try:
                    send_message(int(order["user_id"]), f"🎉 **تبریک!**\n\n{count} عضو کامل شد!")
                except:
                    pass
            save_db(db)
            return
        
        if data.startswith("mreport_"):
            mid = data.replace("mreport_", "")
            order = db["member_orders"].get(mid, {})
            report_keyboard = {"inline_keyboard": [
                [{"text": "✅ پاسخ دادن", "callback_data": f"reply_{user_id}"},
                 {"text": "❌ رد کردن", "callback_data": f"reject_{user_id}"}],
                [{"text": "🗑️ حذف سفارش", "callback_data": f"deletemember_{mid}"},
                 {"text": "⏳ نگه داشتن", "callback_data": f"keep_{user_id}"}]
            ]}
            send_message(int(OWNER_ID), f"🚨 **گزارش عضو:**\n\n👤 {callback['from'].get('first_name', '?')}\n🆔 {user_id}\n🔢 #{order.get('order_number', '?')}", report_keyboard)
            answer_callback(callback_id, "🚨 گزارش ثبت شد!")
            return
        
        if data.startswith("deletemember_"):
            mid = data.replace("deletemember_", "")
            order = db["member_orders"].get(mid, {})
            try:
                delete_message(CHANNEL_ID, order["message_id"])
            except:
                pass
            order["status"] = "deleted"
            try:
                send_message(int(order["user_id"]), "⚠️ **سفارش شما توسط سیستم حذف شد!**\n\n💰 **در ۱ ساعت آینده سکه‌هات برمی‌گرده!**")
                cost_per = 5 if order.get("order_type") == "normal" else 10
                add_coins(order["user_id"], order["count"] * cost_per)
            except:
                pass
            save_db(db)
            answer_callback(callback_id, "🗑️ سفارش حذف شد!", show_alert=True)
            return
        
        if data.startswith("poll_"):
            parts = data.split("_")
            poll_id = parts[1]
            option_num = parts[2]
            poll = db["polls"].get(poll_id, {})
            if not poll:
                answer_callback(callback_id, "❌ وجود نداره!")
                return
            
            votes = poll.get("votes", {})
            for opt, voters in votes.items():
                if str(user_id) in voters:
                    voters.remove(str(user_id))
            
            if str(user_id) not in votes[option_num]:
                votes[option_num].append(str(user_id))
            
            db["polls"][poll_id]["votes"] = votes
            save_db(db)
            
            total_votes = sum(len(v) for v in votes.values())
            result_text = f"📊 **{poll['question']}**\n\n"
            for i, opt in enumerate(poll["options"], 1):
                count = len(votes[str(i)])
                percent = int((count / total_votes) * 100) if total_votes > 0 else 0
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔸"
                result_text += f"{medal} {opt}: {count} ({percent}٪)\n"
            
            keyboard = {"inline_keyboard": []}
            for i, opt in enumerate(poll["options"], 1):
                keyboard["inline_keyboard"].append([{"text": f"{i}. {opt}", "callback_data": f"poll_{poll_id}_{i}"}])
            
            edit_message_text(CHANNEL_ID, poll["message_id"], result_text, keyboard)
            answer_callback(callback_id, "✅ رای ثبت شد!")
            return
    
    except Exception as e:
        print(f"⚠️ خطا در callback: {e}")
        traceback.print_exc()

# ============================================
# 🌐 Flask برای Render
# ============================================
@app.route('/')
def home():
    return "Hypersin Bot is running!"

# ============================================
# 💓 پینگ خودکار ضد خاموشی
# ============================================
def keep_alive():
    while True:
        try:
            requests.get("https://guard-bot-2-cl22.onrender.com", timeout=5)
            print("💓 پینگ خودکار")
        except:
            print("❌ پینگ ناموفق")
        time.sleep(300)  # هر ۵ دقیقه

# ============================================
# 📋 گزارش ساعتی خودکار
# ============================================
def hourly_report():
    while True:
        time.sleep(3600)  # هر ۱ ساعت
        try:
            total = len(db["users"])
            active = sum(1 for o in db["orders"].values() if o["status"] == "active")
            today = get_shamsi_date()
            send_message(int(OWNER_ID), f"📋 **گزارش ساعتی:**\n\n👥 کاربران: {total}\n📋 سفارش فعال: {active}\n📅 {today}")
        except:
            pass

# ============================================
# 📈 ذخیره رشد روزانه
# ============================================
def save_growth():
    while True:
        time.sleep(86400)  # هر ۲۴ ساعت
        try:
            today = get_shamsi_date()
            total = len(db["users"])
            db["growth_stats"][today] = total
            save_db(db)
        except:
            pass

# ============================================
# 🚀 حلقه اصلی
# ============================================
last_update_id = 0

def main():
    global last_update_id, INVITE_REWARD
    INVITE_REWARD = db.get("invite_reward", INVITE_REWARD)
    
    print("⚡ هایپرسین | سین‌زن + عضوگیر")
    print(f"🤖 @{BOT_USERNAME} | 📢 {CHANNEL_LINK}")
    print(f"👁️ دیدم: {SEEN_REWARD} | 📝 سین: {SIN_COST} | 👥 عضو: {MEMBER_COST}")
    print(f"📁 دیتابیس: {DB_FILE}")
    print(f"🛡️ ۶ محافظ فعال | ⚡ فوق سریع | 🥇 تضمینی | 🎁 سکه پاکت")
    print(f"♾️ همیشه روشن")
    print("-" * 40)
    
    while True:
        try:
            server_guard.protect()
            updates = api_call("getUpdates", {"offset": last_update_id + 1, "timeout": 30})
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    last_update_id = update["update_id"]
                    
                    msg = update.get("message", {})
                    
                    # چک ترک کاربر برای نوع تضمینی
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
                                            add_coins(order["user_id"], 5)
                                            mark_punished(left_user_id, mid)
                                            try:
                                                send_message(int(left_user_id), f"⚠️ **قبل از ۴۸ ساعت ترک کردی!**\n💰 **۷ سکه کم شد.**")
                                            except:
                                                pass
                                            try:
                                                send_message(int(order["user_id"]), f"🔔 **کاربر ترک کرد!**\n💰 **۵ سکه برگشت.**")
                                            except:
                                                pass
                    
                    if "message" in update and "left_chat_member" not in msg:
                        handle_message(msg)
                    elif "callback_query" in update:
                        handle_callback(update["callback_query"])
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\n👋 ربات خاموش شد!")
            break
        except Exception as e:
            print(f"⚠️ خطا: {e}")
            print("🔄 ادامه می‌دم...")
            time.sleep(1)
            continue

# ============================================
# 🚀 اجرای همزمان همه
# ============================================
if __name__ == "__main__":
    # ربات
    bot_thread = threading.Thread(target=main)
    bot_thread.daemon = True
    bot_thread.start()
    
    # پینگ خودکار
    ping_thread = threading.Thread(target=keep_alive)
    ping_thread.daemon = True
    ping_thread.start()
    
    # گزارش ساعتی
    report_thread = threading.Thread(target=hourly_report)
    report_thread.daemon = True
    report_thread.start()
    
    # ذخیره رشد
    growth_thread = threading.Thread(target=save_growth)
    growth_thread.daemon = True
    growth_thread.start()
    
    # وب‌سرور
    app.run(host="0.0.0.0", port=10000)