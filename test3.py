import os
import urllib.parse
import asyncio
import json
import requests
from pyrogram import Client, filters
from dotenv import load_dotenv
from quart import Quart
from pyrogram import enums

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_TOKEN = os.getenv("EARNKARO_API_TOKEN")  # Your EarnKaro API token

# Initialize Pyrogram bot
bot = Client("search_links_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize Quart app
app = Quart(__name__)

# Health check route (for hosting platforms)
@app.route("/")
async def home():
    return {"status": "running", "message": "Affiliate Search Bot is alive!"}

# Affiliate API function
def earnkaroapi(text):
    url = "https://ekaro-api.affiliaters.in/api/converter/public"
    payload = json.dumps({
        "deal": f"{text}",
        "convert_option": "convert_only"
    })
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    response_dict = response.json()

    data_value = response_dict.get('data')
    if not data_value or "We could not locate" in data_value:
        return text  # Return original link if no affiliate found
    return data_value

# Generate affiliate search links
# Generate affiliate search links in one go
def generate_search_links(keyword: str):
    encoded_kw = urllib.parse.quote(keyword)

    # Step 1: Create full text block
    search_text = (
        f"🔍 Found your Query '{keyword}' from Amazon, Flipkart, Myntra, Ajio:\n\n\n"
        f"Amazon → https://www.amazon.in/s?k={encoded_kw}\n\n"
        f"Flipkart → https://www.flipkart.com/search?q={encoded_kw}\n\n"
        f"Shopsy → https://www.shopsy.in/search?q={encoded_kw}\n\n"
        f"Ajio → https://www.ajio.com/search/?text={encoded_kw}\n\n"
        f"Myntra → https://www.myntra.com/{encoded_kw.replace('%20', '-')}\n"
    )

    # Step 2: Convert all links at once
    affiliate_text = earnkaroapi(search_text)
    return affiliate_text
    # return search_text


# /start command
@bot.on_message(filters.private & filters.incoming & (filters.command("start") | filters.regex('start')))
async def start_cmd(client, message):
    await message.reply(f"👋 Welcome {message.from_user.first_name}!  from @lootsxpert \n\nSend me a product name or keyword and I'll give you search links from all Platforms.\n\n"
                        "Example: Enter <b><i>Smartwatch</i></b> or <b><i>Jeans under 500</i></b> or <b><i>Laptops </i></b>")

# Handle keywords
@bot.on_message(filters.private & filters.incoming & filters.text & ~filters.command("start"))
async def send_links(client, message):
    keyword = message.text.strip()
    # print(f"🔍 Query from {message.from_user.id}: {keyword}")
    if not keyword:
        await message.reply("❌ Please enter a product name or keyword.")
        return
    # a=await bot.send_dice(chat_id=message.chat.id)
    affiliate_text = generate_search_links(keyword)
    await message.reply(f'<b>{affiliate_text}</b>', disable_web_page_preview=True)


@app.before_serving
async def before_serving():
    await bot.start()


@app.after_serving
async def after_serving():
    await bot.stop()
# Run bot + quart together
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(app.run_task(host='0.0.0.0', port=8080))
    loop.run_forever()

