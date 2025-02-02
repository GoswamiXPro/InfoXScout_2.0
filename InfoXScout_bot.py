import logging
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import asyncio
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from keep_alive import keep_alive  # keep_alive.py ko import kar rahe hain

# Flask se bot ko 24/7 active rakhega
keep_alive()  # Ye line jaroori hai, taaki bot 24/7 live rahe

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token
BOT_TOKEN = "7733683118:AAH0Atfqy1dpo2L6wgQD3apbJs2kgdZY7tg"

# API Keys
NUMLOOK_API_KEY = "num_live_MuLRtwoKHKUNTqOnB4Mfg9h27PJrfNHACLb3inre"
IPINFO_API_KEY = "6d91ca897c96d0"
DATA_MONITORING_API = "14a9acd846185e02a900aa42b7ff6bc1d0211be2"
MAP_API_KEY = "pk.17830ca65ecf76a43d8b22bbfa350389"

# Google APIs
GOOGLE_API_KEY = "AIzaSyBnqN6EFkPyqQcexoFtnHXGc0FFWMBkcIg"
CUSTOM_SEARCH_CSE = "d40a44baaabc94cfb"
CRIMINAL_SEARCH_API = "AIzaSyBMEmHeGdtdifOGpCf2TXXfVOLu4YJTT7k"
CRIMINAL_SEARCH_CSE = "434ed78b215584620"
IMAGE_FETCHER_API = "AIzaSyDzmjjX1p8oYAHwtrqcwlvL_KoIecUdT_g"
IMAGE_FETCHER_CSE = "c5f99b55b30e2491b"

# Initialize cache
cache = Cache.from_url("redis://localhost:6379", serializer=JsonSerializer())

# Start command with inline buttons
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Get Mobile Number Info", callback_data="get_number")],
        [InlineKeyboardButton("Get Criminal Record", callback_data="get_criminal")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to InfoXScout Bot! Choose an option:", reply_markup=reply_markup)

# Button to trigger mobile number input
async def get_mobile_number(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Enter Mobile Number", callback_data="get_number_input")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click below to enter a mobile number:", reply_markup=reply_markup)

# Mobile number details retrieval
async def process_mobile_number(update: Update, context):
    user_input = update.message.text
    await update.message.reply_text(f"Processing number: {user_input}, please wait...")

    numlook_url = f"https://numlook.io/api/{NUMLOOK_API_KEY}/{user_input}"
    response = requests.get(numlook_url).json()

    if "status" in response and response["status"] == "success":
        name = response.get("name", "Unknown")
        address = response.get("address", "Unknown")
        social_media = response.get("social_media", "Unknown")
        usernames = response.get("usernames", "Unknown")
        ip_address = response.get("ip_address", "Unknown")
        criminal_record = response.get("criminal_record", "No criminal record")

        img = Image.new("RGB", (600, 800), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        draw.text((10, 10), f"Name: {name}", font=font, fill=(0, 0, 0))
        draw.text((10, 50), f"Address: {address}", font=font, fill=(0, 0, 0))
        draw.text((10, 90), f"Social Media: {social_media}", font=font, fill=(0, 0, 0))
        draw.text((10, 130), f"Usernames: {usernames}", font=font, fill=(0, 0, 0))
        draw.text((10, 170), f"IP Address: {ip_address}", font=font, fill=(0, 0, 0))
        draw.text((10, 210), f"Criminal Record: {criminal_record}", font=font, fill=(0, 0, 0))

        # Add watermark (Your Name)
        draw.text((500, 750), "Himanshu Goswami", font=font, fill=(200, 200, 200))

        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        await update.message.reply_photo(photo=img_byte_arr)
    else:
        await update.message.reply_text("No information found for this number.")

# Handle callback queries
async def button(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "get_number":
        await query.message.reply_text("Please enter the mobile number to fetch details:")

    elif query.data == "get_criminal":
        await query.message.reply_text("Please enter a name to search for criminal records:")

    elif query.data == "get_number_input":
        await query.message.reply_text("Please enter the mobile number:")

# Asynchronous data fetch with cache
async def fetch_data_from_api(query):
    cached_data = await cache.get(query)
    if cached_data:
        return cached_data

    response = requests.get(f"https://example.com/api/{query}")
    data = response.json()
    await cache.set(query, data, ttl=3600)
    return data

# Main function to set up the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_mobile", get_mobile_number))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_mobile_number))

    # Button handler
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()