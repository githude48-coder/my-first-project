import telebot
import json
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
                data = json.load(f)
                if "processed_ids" not in data: data["processed_ids"] = []
                return data
        except: pass
    return {"processed_ids": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def auto_run_process():
    db = load_db()
    updates = bot.get_updates(offset=-100, limit=100)
    
    current_post = None
    current_file = None

    # ၁။ တင်ဖို့အတွက် Post နဲ့ File တစ်စုံကိုပဲ ရှာမယ်
    for up in updates:
        if not up.message: continue
        msg = up.message
        msg_id = str(msg.message_id)

        if msg_id in db["processed_ids"]: continue

        # Post ရှာခြင်း
        if (msg.photo or msg.video) and msg.caption and "Game:" in msg.caption:
            if not current_post: current_post = msg
        
        # File ရှာခြင်း
        elif msg.document and msg.document.file_name.endswith(".apk"):
            if not current_file: current_file = msg
        
        if current_post and current_file: break

    # ၂။ တစ်စုံ (Post + File) တွေ့ပြီဆိုမှ အလုပ်လုပ်မယ်
    if current_post and current_file:
        try:
            # (က) File ကို အရင်ဆုံး File Channel ထဲ ပို့မယ်
            sent_f = bot.copy_message(f"@{FILE_STORE_CH}", current_file.chat.id, current_file.message_id)
            file_link = f"https://t.me/{FILE_STORE_CH}/{sent_f.message_id}"

            # (ခ) Post ထဲက Download စာသားမှာ အဲ့ဒီ Link ကို မြှုပ်မယ်
            new_caption = current_post.caption.replace("[ Download ]", f"[Download]({file_link})")
            new_caption = new_caption.replace("Download", f"[Download]({file_link})")

            # (ဂ) Post ကို Post Channel ထဲ တင်မယ်
            if current_post.photo:
                bot.send_photo(POST_CH, current_post.photo[-1].file_id, caption=new_caption, parse_mode="Markdown", disable_web_page_preview=True)
            elif current_post.video:
                bot.send_video(POST_CH, current_post.video.file_id, caption=new_caption, parse_mode="Markdown", disable_web_page_preview=True)

            # (ဃ) လုပ်ဆောင်ပြီးကြောင်း မှတ်မယ်
            db["processed_ids"].extend([str(current_post.message_id), str(current_file.message_id)])
            save_db(db)
            print(f"Success: Posted {current_post.caption.split('Game:')[1].splitlines()[0]}")

        except Exception as e:
            print(f"Error: {e}")
    else:
        print("တင်စရာ Post နဲ့ File တစ်စုံ မတွေ့သေးပါ။")

if __name__ == "__main__":
    auto_run_process()
