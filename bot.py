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
    # Update အသစ်တွေ အကုန်ဖတ်မယ်
    updates = bot.get_updates(offset=-100, limit=100)
    
    # ၁။ အရင်ဆုံး File Link တွေကို Database ထဲမှာ Auto မှတ်မယ်
    for up in updates:
        if not up.message: continue
        msg = up.message
        if msg.document and msg.document.file_name.endswith(".apk"):
            # နာမည်ကို ရှင်းပြီး သိမ်းမယ် (ဥပမာ- asphalt 8)
            f_name = msg.document.file_name.lower().replace("-", " ").replace("_", " ")
            file_key = " ".join(f_name.split()[:2]) 
            db["file_links"][file_key] = f"https://t.me/{FILE_STORE_CH}/{msg.message_id}"

    # ၂။ Post အသစ်တစ်ခု ရှာမယ်
    found_post = None
    for up in updates:
        if not up.message: continue
        msg = up.message
        if (msg.photo or msg.video) and msg.caption and "Game:" in msg.caption:
            if str(msg.message_id) not in db["posted_ids"]:
                found_post = msg
                break

    # ၃။ Post တွေ့ရင် တင်မယ်
    if found_post:
        try:
            caption = found_post.caption
            game_name = caption.split("Game:")[1].split("\n")[0].strip().lower()
            search_key = " ".join(game_name.split()[:2])
            
            # File Link ကို ရှာမယ်
            download_url = db["file_links"].get(search_key, f"https://t.me/{FILE_STORE_CH}")

            # Link မြှုပ်မယ်
            new_caption = caption.replace("[ Download ]", f"[Download]({download_url})")
            
            if found_post.photo:
                bot.send_photo(POST_CH, found_post.photo[-1].file_id, caption=new_caption, parse_mode="Markdown", disable_web_page_preview=True)
            elif found_post.video:
                bot.send_video(POST_CH, found_post.video.file_id, caption=new_caption, parse_mode="Markdown", disable_web_page_preview=True)

            db["posted_ids"].append(str(found_post.message_id))
            save_db(db)
            print(f"Success! Posted: {game_name}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("တင်စရာ အသစ်မရှိသေးပါ။")

if __name__ == "__main__":
    auto_run_process()
