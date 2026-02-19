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
                return data if "games" in data else {"games": [], "posted_ids": [], "file_links": {}}
        except:
            return {"games": [], "posted_ids": [], "file_links": {}}
    return {"games": [], "posted_ids": [], "file_links": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def auto_run_process():
    db = load_db()
    if "file_links" not in db: db["file_links"] = {}
    
    updates = bot.get_updates()
    for up in updates:
        if not up.message: continue
        msg = up.message
        
        # ၁။ APK File ဖြစ်ရင် Storage ဆီပို့ပြီး Link ကို မှတ်သားမယ်
        if msg.document and msg.document.file_name.endswith(".apk"):
            sent_file = bot.copy_message(FILE_STORE_CH, msg.chat.id, msg.message_id)
            clean_ch = FILE_STORE_CH.replace("@", "")
            direct_link = f"https://t.me/{clean_ch}/{sent_file.message_id}"
            
            # ဖိုင်နာမည်ထဲက ဂိမ်းနာမည်ကို ခွဲထုတ်မယ် (ဥပမာ- Human-Resource-Machine)
            file_key = msg.document.file_name.split("-v")[0].replace("-", " ").lower()
            db["file_links"][file_key] = direct_link
            print(f"File Linked: {file_key}")

        # ၂။ ပုံ+စာ ပါတဲ့ Post ဖြစ်ရင် Database ထဲ မှတ်မယ်
        elif (msg.caption or msg.text) and not msg.document:
            text = msg.caption if msg.caption else msg.text
            if "Game:" in text:
                game_name = text.split("Game:")[1].split("\n")[0].strip()
                if not any(g['post_id'] == msg.message_id for g in db["games"]):
                    db["games"].append({
                        "name": game_name,
                        "post_id": msg.message_id,
                        "chat_id": msg.chat.id,
                        "caption": text
                    })
    save_db(db)

    # ၃။ မတင်ရသေးတဲ့ ဂိမ်းတစ်ခုတည်းကိုပဲ ရွေးမယ်
    available = [g for g in db["games"] if str(g["post_id"]) not in db["posted_ids"]]
    if not available:
        print("တင်စရာ အသစ်မရှိပါ။")
        return

    selected = random.choice(available)
    game_key = selected["name"].lower().strip()
    
    # ဖိုင်လင့်ခ် ရှိမရှိ စစ်မယ်
    download_url = db["file_links"].get(game_key, "#")

    try:
        # ၄။ Post ကို Edit လုပ်ပြီး Download Link အမှန်ထည့်မယ်
        final_caption = selected["caption"].replace("[ Download ]", f"[Download]({download_url})")
        
        # ၅။ တင်မယ် (Preview ပိတ်ထားတယ်)
        bot.send_message(
            POST_CH, 
            final_caption, 
            parse_mode="Markdown", 
            disable_web_page_preview=True
        )
        
        db["posted_ids"].append(str(selected["post_id"]))
        save_db(db)
        print(f"Success: Posted {selected['name']} with Link.")
        return # တစ်ခုတင်ပြီးရင် ရပ်မယ်

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
