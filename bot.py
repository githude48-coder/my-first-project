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
                return data if "file_links" in data else {"games": [], "posted_ids": [], "file_links": {}}
        except:
            return {"games": [], "posted_ids": [], "file_links": {}}
    return {"games": [], "posted_ids": [], "file_links": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def auto_run_process():
    db = load_db()
    updates = bot.get_updates()
    
    for up in updates:
        if not up.message: continue
        msg = up.message
        
        # ၁။ APK File Link ဖမ်းယူခြင်း
        if msg.document and msg.document.file_name.endswith(".apk"):
            # File ကို Storage ဆီ ပို့ပြီး Link ယူမယ်
            sent_file = bot.copy_message(FILE_STORE_CH, msg.chat.id, msg.message_id)
            clean_ch = FILE_STORE_CH.replace("@", "")
            direct_link = f"https://t.me/{clean_ch}/{sent_file.message_id}"
            
            # ဂိမ်းနာမည်ကို File Name ကနေ ယူမယ်
            file_key = msg.document.file_name.split("-v")[0].replace("-", " ").lower().strip()
            db["file_links"][file_key] = direct_link

        # ၂။ Post အလှကို မှတ်သားခြင်း
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

    # ၃။ တစ်ခုတည်းကို ရွေးချယ်တင်ခြင်း
    available = [g for g in db["games"] if str(g["post_id"]) not in db["posted_ids"]]
    if not available: return

    selected = random.choice(available)
    game_key = selected["name"].lower().strip()
    download_url = db["file_links"].get(game_key, "https://t.me/offlinegamelink")

    try:
        # ၄။ ပုံရော စာရော အကုန်ပါအောင် Copy Message ကို သုံးမယ်
        # ပြီးမှ Caption ကို Link အမှန်နဲ့ ပြင်မယ်
        sent_msg = bot.copy_message(POST_CH, selected["chat_id"], selected["post_id"])
        
        # Link ထည့်ရန်အတွက် Caption ကို ပြန်ပြင်မယ်
        # (Download ဆိုတဲ့ စာသားနေရာမှာ Link မြှုပ်ပေးမယ်)
        post_msg = bot.get_message(selected["chat_id"], selected["post_id"])
        new_caption = post_msg.caption.replace("[ Download ]", f"[Download]({download_url})")
        new_caption = new_caption.replace("Download", f"[Download]({download_url})")

        bot.edit_message_caption(
            chat_id=POST_CH,
            message_id=sent_msg.message_id,
            caption=new_caption,
            parse_mode="Markdown",
            disable_web_page_preview=True # Preview ပိတ်ထားတယ်
        )
        
        db["posted_ids"].append(str(selected["post_id"]))
        save_db(db)
        print(f"Success: Posted {selected['name']} with Link and Image.")
        return 

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
