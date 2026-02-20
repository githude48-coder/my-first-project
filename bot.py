import telebot
import json
import random
import os

# --- CONFIGURATION ---
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
    return {"posted_ids": [], "file_links": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def auto_run_process():
    db = load_db()
    # အချက်အလက်အသစ်တွေကို ပြန်ဖတ်မယ်
    updates = bot.get_updates(offset=-50, limit=50)
    
    found_post = None

    for up in updates:
        if not up.message: continue
        msg = up.message
        
        # Post (ပုံ+စာ) ကို ရှာမယ်
        if (msg.photo or msg.video) and msg.caption and "Game:" in msg.caption:
            if str(msg.message_id) not in db["posted_ids"]:
                found_post = msg
                break # တစ်ခါ Run ရင် တစ်ခုပဲ တင်မယ်

    if found_post:
        try:
            game_name = found_post.caption.split("Game:")[1].split("\n")[0].strip().lower()
            # Database ထဲမှာ လင့်ခ်ရှိမရှိ စစ်မယ်
            download_url = db.get("file_links", {}).get(game_name, f"https://t.me/{FILE_STORE_CH}")

            # [ Download ] ကို Link ပြောင်းမယ်
            new_caption = found_post.caption.replace("[ Download ]", f"[Download]({download_url})")
            
            # Post ကို တင်မယ် (File ကို လုံးဝ မတင်ပါ)
            if found_post.photo:
                bot.send_photo(POST_CH, found_post.photo[-1].file_id, caption=new_caption, parse_mode="Markdown", disable_web_page_preview=True)
            elif found_post.video:
                bot.send_video(POST_CH, found_post.video.file_id, caption=new_caption, parse_mode="Markdown", disable_web_page_preview=True)

            db["posted_ids"].append(str(found_post.message_id))
            save_db(db)
            print(f"Success! Posted {game_name}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("တင်စရာ Post အသစ် ရှာမတွေ့ပါ။")

if __name__ == "__main__":
    auto_run_process()
