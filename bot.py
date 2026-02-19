import telebot
import json
import random
import os
import sys

# --- CONFIGURATION ---
TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
SOURCE_CH = "@offlinegamelink" # Post တွေရှိတဲ့နေရာ
TARGET_CH = "@offlinegame999" # Post တင်မယ့်နေရာ
DB_FILE = 'database.json'

bot = telebot.TeleBot(TOKEN)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"posted_ids": []}
    return {"posted_ids": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def auto_post():
    db = load_db()
    
    # Post ID နံပါတ် ၁ ကနေ ၁၀၀၀ အထိထဲက ကျပန်းရွေးမယ်
    # (သင် Post တွေ ထပ်တင်ရင် ၁၀၀၀ ဂဏန်းကို တိုးပေးလို့ရပါတယ်)
    start_id = 1
    end_id = 1000 
    
    all_possible_ids = list(range(start_id, end_id + 1))
    posted_ids = db.get("posted_ids", [])

    # မတင်ရသေးတဲ့ ID တွေကိုပဲ ရွေးမယ်
    available = [i for i in all_possible_ids if i not in posted_ids]

    # အကုန်တင်ပြီးရင် အစက ပြန်စမယ်
    if not available:
        db["posted_ids"] = []
        available = all_possible_ids

    # ကျပန်း Post ID တစ်ခုကို ရွေးတယ်
    selected_id = random.choice(available)

    try:
        # copy_message က ရေးထားတဲ့ Post ကို ပုံစံမပျက် (စာ၊ ပုံ၊ Button) အကုန်ကူးပေးတာပါ
        bot.copy_message(TARGET_CH, SOURCE_CH, selected_id)
        
        # တင်ပြီးကြောင်း မှတ်ထားမယ်
        db["posted_ids"].append(selected_id)
        save_db(db)
        print(f"Success: Copied Post ID {selected_id}")
        
    except Exception as e:
        # တကယ်လို့ အဲ့ဒီ ID မှာ Post မရှိရင် (ဥပမာ ဖျက်ထားရင်) နောက်တစ်ခု ထပ်ရွေးခိုင်းမယ်
        print(f"ID {selected_id} is empty or error, trying another...")
        # ဒီ ID ကို တင်ပြီးသားစာရင်းထဲ ထည့်လိုက်မှ နောက်တစ်ခါ ထပ်မရွေးမှာပါ
        db["posted_ids"].append(selected_id)
        save_db(db)
        auto_post() 

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_post()
    else:
        print("Bot is listening for commands...")
        bot.polling(none_stop=True)
