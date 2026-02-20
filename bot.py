import telebot
import json
import random
import os

# --- CONFIGURATION ---
TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
FILE_STORE_CH = "offlinegamelink" # @ မပါဘဲ Channel ID သီးသန့်
POST_CH = "@offlinegame999"      
DB_FILE = 'database.json'

bot = telebot.TeleBot(TOKEN)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                if "file_links" not in data: data["file_links"] = {}
                return data
        except: pass
    return {"games": [], "posted_ids": [], "file_links": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def auto_run_process():
    db = load_db()
    updates = bot.get_updates(offset=-50, limit=100)
    
    for up in updates:
        if not up.message: continue
        msg = up.message
        
        # ၁။ File Channel ထဲက Message ID ကို ယူပြီး Link လုပ်မယ်
        if msg.document and msg.document.file_name.endswith(".apk"):
            # နာမည်ကို ရှင်းပြီး Key လုပ်မယ် (ဥပမာ- days after)
            f_name = msg.document.file_name.lower().replace("-", " ").replace("_", " ")
            file_key = f_name.split("v1")[0].split("v2")[0].strip()
            db["file_links"][file_key] = f"https://t.me/{FILE_STORE_CH}/{msg.message_id}"

        # ၂။ Post သိမ်းမယ်
        elif (msg.caption or msg.text) and (msg.photo or msg.video):
            text = msg.caption if msg.caption else msg.text
            if "Game:" in text:
                game_name = text.split("Game:")[1].split("\n")[0].strip().lower()
                if not any(g['post_id'] == msg.message_id for g in db["games"]):
                    db["games"].append({
                        "name": game_name,
                        "post_id": msg.message_id,
                        "chat_id": msg.chat.id,
                        "caption": text
                    })
    save_db(db)

    # ၃။ တစ်ခုပဲ ရွေးတင်မယ်
    available = [g for g in db["games"] if str(g["post_id"]) not in db["posted_ids"]]
    if not available: return

    selected = random.choice(available)
    # ရှေ့ဆုံးစာလုံးနဲ့ Link ရှာမယ်
    search_key = selected["name"].split("-")[0].strip()
    download_url = db["file_links"].get(search_key, f"https://t.me/{FILE_STORE_CH}")

    try:
        # ၄။ Post ကိုပဲ Channel ထဲ တင်မယ် (File မပါဘူး)
        # [ Download ] နေရာမှာ Link မြှုပ်ပေးမယ်
        new_caption = selected["caption"].replace("[ Download ]", f"[Download]({download_url})")
        
        orig_msg = bot.get_message(selected["chat_id"], selected["post_id"])
        if orig_msg.photo:
            bot.send_photo(POST_CH, orig_msg.photo[-1].file_id, caption=new_caption, parse_mode="Markdown", disable_web_page_preview=True)
        elif orig_msg.video:
            bot.send_video(POST_CH, orig_msg.video.file_id, caption=new_caption, parse_mode="Markdown", disable_web_page_preview=True)
        
        db["posted_ids"].append(str(selected["post_id"]))
        save_db(db)
        print("Post uploaded with deep link!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    auto_run_process()
