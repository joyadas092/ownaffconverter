import json
import tempfile
from io import BytesIO

import requests
from pyrogram import Client, filters, enums
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
import logging

from pyrogram.raw.types import MessageEntityUrl
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import asyncio
from quart import Quart
from unshortenit import UnshortenIt

api_id= '26566076'
api_hash= '40ce27837b95819c42cac67b46a2dc2b'
bot_token='6866466311:AAG3EnZWlDSTWNqstw_F52a2Uw8ULbJ8Fr0'
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
apitoken='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2M2U2MjEwNjYwOWU1YWY4ZTc4OTU2NTEiLCJlYXJua2FybyI6IjI1MjM2ODEiLCJpYXQiOjE3MTQzMzcxMDZ9.WOP7a-VJpEvg5p1sOpujkFJlcGjk50rq55ixeyHunK4'

# Define a handler for the /start command
bot = Quart(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

source_channel_id = [-1002110764294]  # Replace with the source channel ID
def ekconvert(text):
    url = "https://ekaro-api.affiliaters.in/api/converter/public"

    # inputtext = input('enter deal: ')
    payload = json.dumps({
        "deal": f"{text}",
        "convert_option": "convert_only"
    })
    headers = {
        'Authorization': f'Bearer {apitoken}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)
    response_dict = json.loads(response.text)

    # Extract the "data" part from the dictionary
    data_value = response_dict.get('data')
    if 'We could not locate an affiliate URL to send' in data_value:
        return None
    else:
        return(data_value)

def extract_link_from_text(text):
    # Regular expression pattern to match a URL
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    return urls

def unshorten_url(short_url):
    unshortener = UnshortenIt()
    shorturi = unshortener.unshorten(short_url)
    # print(shorturi)
    return shorturi
def extp(text):
    unshortened_urls = {}
    urls = extract_link_from_text(text)
    for url in urls:
        unshortened_urls[url] = unshorten_url(url)
    for original_url, unshortened_url in unshortened_urls.items():
        text = text.replace(original_url, unshortened_url)
    return text

@bot.route('/')
async def hello():
    return 'Hello, world!'

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await app.send_message(message.chat.id,"ahaann")


@app.on_message(filters.chat(-1002060929372)|filters.user(5886397642))
async def handle_text(client, message):
    # app.set_parse_mode(enums.ParseMode.HTML)
    # print(message)
    Promo = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Join Deals HUB", url="https://t.me/addlist/FYEMFZCWeTY2ZmE1")],
         [InlineKeyboardButton("Join Main Channel", url="https://t.me/Deals_and_Discounts_Channel/37444")]
         ])
    if message.photo:
        text = message.caption if message.caption else message.text
        inputvalue = text
        # print(message.chat.id)

        hyperlinkurl = []
        for entity in message.caption_entities:
            # new_entities.append(entity)
            if entity.url is not None:
                hyperlinkurl.append(entity.url)
        pattern = re.compile(r'Buy Now')

        inputvalue = pattern.sub(lambda x: hyperlinkurl.pop(0), inputvalue).replace('Regular Price', 'MRP')
        if 'amazon' not in inputvalue or 'tinyurl' not in inputvalue or 't.me' not in inputvalue:
            if "😱 Deal Time" in inputvalue:
            # Remove the part
                inputvalue = inputvalue.split("😱 Deal Time")[0]
            if 'extp' in inputvalue or 'myntr.in' in inputvalue or 'fkrt.co' in inputvalue:
                inputvalue=extp(inputvalue)
            
            # print(inputvalue)
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                # app.download_media(message)
                await message.download(file_name=temp_file.name)
    
                with open(temp_file.name, 'rb') as f:
                    photo_bytes = BytesIO(f.read())
            msgtext = ekconvert(inputvalue)
            await app.send_photo(message.chat.id, photo=photo_bytes, caption=msgtext)
            await app.send_photo(chat_id=-1002110764294, photo=photo_bytes, caption=f'<b>{msgtext}</b>',
                                reply_markup=Promo)

    elif message.text:
        inputvalue = message.text

        hyperlinkurl = []
        for entity in message.entities:
            # new_entities.append(entity)
            if entity.url is not None:
                hyperlinkurl.append(entity.url)
        pattern = re.compile(r'Buy Now')

        inputvalue = pattern.sub(lambda x: hyperlinkurl.pop(0), inputvalue).replace('Regular Price', 'MRP')

        if 'amazon' not in inputvalue or 'tinyurl' not in inputvalue or 't.me' not in inputvalue:
            if "😱 Deal Time" in inputvalue:
            # Remove the part
                inputvalue = inputvalue.split("😱 Deal Time")[0]
            if 'extp' in inputvalue or 'myntr.in' in inputvalue or 'fkrt.co' in inputvalue:
                inputvalue=extp(inputvalue)
            msgtext=ekconvert(inputvalue)
    
            await app.send_message(message.chat.id, text=msgtext, disable_web_page_preview=True)
            await app.send_message(chat_id=-1002110764294, text=f'<b>{msgtext}</b>',
                                   disable_web_page_preview=True)


@bot.before_serving
async def before_serving():
    await app.start()


@bot.after_serving
async def after_serving():
    await app.stop()

# if __name__ == '__main__':

    # bot.run(port=8000)
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run_task(host='0.0.0.0', port=8090))
    loop.run_forever()
