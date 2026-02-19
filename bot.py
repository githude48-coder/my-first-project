import telebot
import json
import random
import os
import sys

# --- CONFIGURATION ---
TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
FILE_STORE_CH = "@offlinegamelink" 
POST_CH = "@offlinegame999"      
DB_FILE = 'database.json'

bot = telebot.TeleBot(TOKEN)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                # လိုအပ်သော Field များပါဝင်မှု ရှိမရှိ စစ်ဆေးခြင်း
                if "games" not in data: data["games"] = []
                if "posted_ids" not in data: data["posted_ids"] = []
                if "file_links" not in data: data["file_links"] = {}
                return data
        except:
            return {"games": [], "posted_ids": [], "file_links": {}}
    return {"games": [], "posted_ids": [], "file_links": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def auto_run_process():
    db = load_db()
    updates = bot.get_updates()
    
    # ၁။ Syncing: အသစ်ပို့ထားသမျှ ဖိုင်နှင့် Post များကို စာရင်းသွင်းခြင်း
    for up in updates:
        if not up.message: continue
        msg = up.message
        
        # File Link မှတ်သားခြင်း
        if msg.document and msg.document.file_name.endswith(".apk"):
            file_key = msg.document.file_name.split("-v")[0].replace("-", " ").lower().strip()
            clean_ch = FILE_STORE_CH.replace("@", "")
            # Direct Message Link
            db["file_links"][file_key] = f"https://t.me/{clean_ch}/{msg.message_id}"

        # Post (ပုံ+စာ) မှတ်သားခြင်း
        elif (msg.caption or msg.text) and (msg.photo or msg.video):
            text = msg.caption if msg.caption else msg.text
            if "Game:" in text:
                game_name = text.split("Game:")[1].split("\n")[0].strip()
                if not any(g['post_id'] == msg.message_id for g in db["games"]):
                    db["games"].append({
                        "name": game_name,
                        "post_id": msg.message_id,
                        "chat_id": msg.chat.id
                    })
    save_db(db)

    # ၂။ Filtering: တင်ပြီးသား ID များကို ဖယ်ထုတ်ပြီး ကျန်တာထဲမှ ကျပန်း (Random) တစ်ခုရွေးခြင်း
    available = [g for g in db["games"] if str(g["post_id"]) not in db["posted_ids"]]
    
    if not available:
        print("တင်စရာ အသစ်မရှိတော့ပါ။")
        return

    selected = random.choice(available)
    game_key = selected["name"].lower().strip()
    # ဖိုင်လင့်ခ် ရှိမရှိစစ်၊ မရှိရင် Channel Link ပြပေးမယ်
    download_url = db["file_links"].get(game_key, f"https://t.me/{FILE_STORE_CH.replace('@','')}")

    try:
        # ၃။ တင်ဆက်ခြင်း: ပုံစံမပျက် Forward လုပ်ပြီးမှ Caption ကို ပြန်ပြင်ခြင်း
        sent_msg = bot.copy_message(POST_CH, selected["chat_id"], selected["post_id"])
        
        orig = bot.get_message(selected["chat_id"], selected["post_id"])
        caption = orig.caption if orig.caption else orig.text
        
        # Link မြှုပ်ခြင်း (Markdown သုံးထားသည်)
        caption = caption.replace("[ Download ]", f"[Download]({download_url})")
        caption = caption.replace("Download", f"[Download]({download_url})")

        bot.edit_message_caption(
            chat_id=POST_CH,
            message_id=sent_msg.message_id,
            caption=caption,
            parse_mode="Markdown",
            disable_web_page_preview=True # Preview ပိတ်ရန်
        )
        
        # ၄။ Logging: တင်ပြီးသားအဖြစ် မှတ်သားခြင်း (နောက်တစ်ခါ လုံးဝ ပြန်မတင်ရန်)
        db["posted_ids"].append(str(selected["post_id"]))
        save_db(db)
        print(f"Success: Randomly Posted {selected['name']}.")
        return 

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
