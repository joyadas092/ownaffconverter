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
def create_amazon_affiliate_url(normal_url, affiliate_tag):
    if "amazon" not in normal_url:
        return "Not a valid Amazon Product link."

    if not affiliate_tag:
        return "Please provide a valid affiliate tag."

    # Check if the URL already has query parameters
    separator = '&' if '?' in normal_url else '?'

    # Append the affiliate tag to the URL
    affiliate_url = f"{normal_url}{separator}tag={affiliate_tag}"

    return affiliate_url
def tiny(long_url):
    url = 'http://tinyurl.com/api-create.php?url='

    response = requests.get(url + long_url)
    short_url = response.text
    return short_url
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

def generate_search_links(keyword: str):
    encoded_kw = urllib.parse.quote(keyword)
    # print(encoded_kw)
    # Step 1: Create full text block
    amznEcomLink=tiny(create_amazon_affiliate_url(f"https://www.amazon.in/s?k={encoded_kw}",'highfivesto0c-21'))
    amznQcomLink=tiny(create_amazon_affiliate_url(f"https://www.amazon.in/s?k={encoded_kw}&i=nowstore",'highfivesto0c-21'))
    # print(amznQcomLink,amznEcomLink)
    IntialText=  (f"🔍 Found your Query '{keyword}' from Amazon, Flipkart, Myntra, Ajio and More:\n\n"
        f"Some Platforms may not have your products.So Check Accordingly \n\n"
        f"<b><U>E-Commerce 👇👇</U></b>\n"
        f"Amazon → {amznEcomLink}\n")
    earnkaro_text = (
        f"Flipkart → https://www.flipkart.com/search?q={encoded_kw}\n"
        f"Shopsy → https://www.shopsy.in/search?q={encoded_kw}\n"
        f"Ajio → https://www.ajio.com/search/?text={encoded_kw}\n"
        f"Myntra → https://www.myntra.com/{encoded_kw.replace('%20', '-')}\n"
        f"Reliance Digital → https://www.reliancedigital.in/products?q={encoded_kw}\n"
        f"JioMart → https://www.jiomart.com/search/{encoded_kw}\n"
        f"Croma → https://www.croma.com/searchB?q={encoded_kw}%3Arelevance&text={encoded_kw}\n\n"
        f"<b><U>Quick-Commerce 👇👇</U></b>(Check Your PIN)\n"
        f"Flipkart Minutes → https://www.flipkart.com/hyperlocal/pr?q={encoded_kw}&marketplace=HYPERLOCAL&sid=search.flipkart.com\n"
    )

    # Step 2: Convert all links at once
    affiliate_text = earnkaroapi(earnkaro_text)
    QCom_search_text=(
    f"Amazon Fresh → {amznQcomLink}\n"
    f"Blinkit → <a href='https://blinkit.com/s/?q={encoded_kw}'> Click Here</a>\n"
    f"Instamart → <a href='https://www.swiggy.com/instamart/search?query={encoded_kw}'> Click Here</a>\n"
    f"Zepto → <a href='https://www.zeptonow.com/search?query={encoded_kw}'> Click Here</a>\n"
    f"BigBasket → <a href='https://www.bigbasket.com/ps/?q={encoded_kw}'> Click Here</a>\n")
    return IntialText+affiliate_text + QCom_search_text
    # return search_text


# /start command
@bot.on_message(filters.private & filters.command("start") & filters.incoming)
async def start_cmd(client, message):
    await message.reply(f"👋 Welcome {message.from_user.first_name}!  from @lootsxpert \n\nSend me a product name or keyword and I'll give you search links from all Platforms.\n\n"
                        "Example: Enter <b><i>Smartwatch</i></b> or <b><i>Jeans under 500</i></b> or <b><i>Laptops </i></b>")

# Handle keywords
@bot.on_message(filters.private & ~filters.command("start"))
async def send_links(client, message):
    text = message.caption if message.caption else message.text
    if 'Livegram' in text or 'You cannot forward someone' in text:
        await message.delete()
        return None
    keyword = text.strip()
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

