import telebot
import json
import random
import os

TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
FILE_STORE_CH = "offlinegamelink" 
POST_CH = "@offlinegame999"      
DB_FILE = 'database.json'

bot = telebot.TeleBot(TOKEN)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
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
        
        # Post သိမ်းခြင်း
        if (msg.caption or msg.text) and (msg.photo or msg.video):
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

    available = [g for g in db["games"] if str(g["post_id"]) not in db["posted_ids"]]
    if not available: return

    selected = random.choice(available)
    # Database ထဲက လင့်ခ်ကို တိုက်ရိုက်ယူမယ်
    download_url = db["file_links"].get(selected["name"], f"https://t.me/{FILE_STORE_CH}")

    try:
        # Download စာသားကို လင့်ခ်အဖြစ် ပြောင်းလဲခြင်း
        new_caption = selected["caption"].replace("[ Download ]", f"[Download]({download_url})")
        
        orig_msg = bot.get_message(selected["chat_id"], selected["post_id"])
        
        # Post ကိုပဲ တင်မယ် (File ကို လုံးဝ ထပ်မတင်တော့ပါ)
        if orig_msg.photo:
            bot.send_photo(POST_CH, orig_msg.photo[-1].file_id, caption=new_caption, parse_mode="Markdown", disable_web_page_preview=True)
        
        db["posted_ids"].append(str(selected["post_id"]))
        save_db(db)
        print(f"Success! Posted {selected['name']} with Link.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    auto_run_process()
