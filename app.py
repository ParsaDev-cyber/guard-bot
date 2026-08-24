from flask import Flask
import requests
import time
import threading

app = Flask(__name__)

TOKEN = "212950195:AfqKYLrhXkM1pqq18QF7m2hrTs1jzYoT_WA"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"

def send_message(chat_id, text):
    data = {"chat_id": chat_id, "text": text}
    try:
        return requests.post(f"{BASE_URL}/sendMessage", json=data).json()
    except:
        return {"ok": False}

def bot_loop():
    print("🛡️ ربات نگهبان فعال شد!")
    last_update = 0
    
    while True:
        try:
            updates = requests.get(f"{BASE_URL}/getUpdates", params={"offset": last_update + 1, "timeout": 30}).json()
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    last_update = update["update_id"]
                    
                    if "message" in update and "text" in update["message"]:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        text = msg.get("text", "")
                        
                        if text == "سلام":
                            send_message(chat_id, "👋 سلام! خوبی؟ 😊")
                        elif text == "/start":
                            send_message(chat_id, "👋 سلام! ربات نگهبان فعاله! ✅")
        
        except Exception as e:
            print(f"⚠️ {e}")
        time.sleep(1)

@app.route('/')
def home():
    return "Bot is running!"

# پینگ خودکار برای بیدار موندن
def keep_alive():
    while True:
        try:
            requests.get("https://guard-bot-2-cl22.onrender.com", timeout=5)
            print("💓 پینگ خودکار")
        except:
            print("❌ پینگ ناموفق")
        time.sleep(600)  # هر ۱۰ دقیقه

if __name__ == "__main__":
    # اجرای ربات
    bot_thread = threading.Thread(target=bot_loop)
    bot_thread.daemon = True
    bot_thread.start()
    
    # اجرای پینگ خودکار
    ping_thread = threading.Thread(target=keep_alive)
    ping_thread.daemon = True
    ping_thread.start()
    
    # اجرای وب‌سرور
    app.run(host="0.0.0.0", port=10000)