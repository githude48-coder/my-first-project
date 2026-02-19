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
                # Ensure all necessary keys exist
                for key in ["games", "posted_ids", "file_links"]:
                    if key not in data: data[key] = [] if key != "file_links" else {}
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
    
    # ၁။ Syncing: ဖိုင်လင့်ခ်တွေနဲ့ Post တွေကို ရှာဖွေမှတ်သားမယ်
    for up in updates:
        if not up.message: continue
        msg = up.message
        
        # APK File တွေ့ရင် Storage Link ကို မှတ်မယ်
        if msg.document and msg.document.file_name.endswith(".apk"):
            file_key = msg.document.file_name.split("-v")[0].replace("-", " ").lower().strip()
            clean_ch = FILE_STORE_CH.replace("@", "")
            db["file_links"][file_key] = f"https://t.me/{clean_ch}/{msg.message_id}"

        # Post (ပုံ+စာ) တွေ့ရင် Database ထဲ ထည့်မယ်
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

    # ၂။ တစ်ခါတင်ရင် တစ်ခုပဲ တက်လာဖို့အတွက် ကျပန်းရွေးချယ်မယ်
    available = [g for g in db["games"] if str(g["post_id"]) not in db["posted_ids"]]
    
    if not available:
        print("တင်စရာ အသစ်မရှိပါ။")
        return

    selected = random.choice(available)
    game_key = selected["name"].lower().strip()
    # ဖိုင်လင့်ခ်ကို ရှာမယ်၊ မရှိရင် Channel Link ပေးမယ်
    download_url = db["file_links"].get(game_key, f"https://t.me/{FILE_STORE_CH.replace('@','')}")

    try:
        # ၃။ Post ကို Forward အရင်လုပ်မယ်
        sent_msg = bot.copy_message(POST_CH, selected["chat_id"], selected["post_id"])
        
        # ၄။ Caption ကို Link မြှုပ်ပြီး Preview ပိတ်မယ်
        orig_msg = bot.get_message(selected["chat_id"], selected["post_id"])
        final_caption = orig_msg.caption if orig_msg.caption else orig_msg.text
        
        # [ Download ] နေရာမှာ Link အစစ်ကို မြှုပ်ပေးခြင်း
        final_caption = final_caption.replace("[ Download ]", f"[Download]({download_url})")
        final_caption = final_caption.replace("Download", f"[Download]({download_url})")

        bot.edit_message_caption(
            chat_id=POST_CH,
            message_id=sent_msg.message_id,
            caption=final_caption,
            parse_mode="Markdown",
            disable_web_page_preview=True # Preview ပိတ်ထားသည်
        )
        
        # ၅။ တင်ပြီးကြောင်း မှတ်သားပြီး အလုပ်ရပ်မယ်
        db["posted_ids"].append(str(selected["post_id"]))
        save_db(db)
        print(f"Success: Posted {selected['name']} with Link. Preview disabled.")
        return 

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
