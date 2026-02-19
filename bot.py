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
    
    # ၁။ Storage Channel ထဲက File Link တွေကို အရင်မှတ်သားမယ်
    for up in updates:
        if not up.message: continue
        msg = up.message
        
        if msg.document and msg.document.file_name.endswith(".apk"):
            file_key = msg.document.file_name.split("-v")[0].replace("-", " ").lower().strip()
            clean_ch = FILE_STORE_CH.replace("@", "")
            # ဖိုင်ရှိတဲ့နေရာရဲ့ တိုက်ရိုက်လင့်ခ်ကို သိမ်းမယ်
            db["file_links"][file_key] = f"https://t.me/{clean_ch}/{msg.message_id}"

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

    # ၂။ မတင်ရသေးတာထဲက တစ်ခုပဲ ကျပန်းရွေးမယ်
    available = [g for g in db["games"] if str(g["post_id"]) not in db["posted_ids"]]
    if not available: return

    selected = random.choice(available)
    game_key = selected["name"].lower().strip()
    # ဖိုင်လင့်ခ်ကို ရှာမယ်
    download_url = db["file_links"].get(game_key, f"https://t.me/{FILE_STORE_CH.replace('@','')}")

    try:
        # ၃။ Post ကို Forward အရင်လုပ်မယ်
        sent_msg = bot.copy_message(POST_CH, selected["chat_id"], selected["post_id"])
        
        # ၄။ Caption ကို Link အဖြစ်ပြောင်းလဲပြီး Edit လုပ်မယ်
        orig = bot.get_message(selected["chat_id"], selected["post_id"])
        caption = orig.caption if orig.caption else orig.text
        
        # [ Download ] နေရာမှာ Link မြှုပ်ပေးခြင်း
        final_caption = caption.replace("[ Download ]", f"[Download]({download_url})")
        final_caption = final_caption.replace("Download", f"[Download]({download_url})")

        bot.edit_message_caption(
            chat_id=POST_CH,
            message_id=sent_msg.message_id,
            caption=final_caption,
            parse_mode="Markdown",
            disable_web_page_preview=True # Preview ပိတ်ရန်
        )
        
        db["posted_ids"].append(str(selected["post_id"]))
        save_db(db)
        print(f"Success: Posted {selected['name']} with deep link.")
        return 

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
