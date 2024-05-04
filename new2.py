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
        "convert_option": "convert_only",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
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

    return(data_value)

def extract_link_from_text(text):
    # Regular expression pattern to match a URL
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    return urls[0] if urls else None

def unshorten_url(short_url):
    unshortener = UnshortenIt()
    shorturi = unshortener.unshorten(short_url)
    # print(shorturi)
    return shorturi

@bot.route('/')
async def hello():
    return 'Hello, world!'

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await app.send_message(message.chat.id,"ahaann")


@app.on_message(filters.chat(-1002060929372))
async def handle_text(client, message):
    # app.set_parse_mode(enums.ParseMode.HTML)
    # print(message)
    Promo = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Join Deals HUB", url="https://t.me/addlist/FYEMFZCWeTY2ZmE1")],
         [InlineKeyboardButton("Join Main Channel", url="https://t.me/Deals_and_Discounts_Channel/37444")]
         ])
    # if message.photo:
    #     text = message.caption if message.caption else message.text
    #     inputvalue = text


    # elif message.text:
    #     inputvalue = message.text
    # # print(message)
    #     # print(message.entities)
    # # print(inputvalue)
    inputvalue = ''
    hyerlinkurl=[]
    new_entities=[]

    if message.entities:
        for entity in message.entities:
            new_entities.append(entity)
            if entity.url is not None:
                hyerlinkurl.append(entity.url)
                inputvalue = entity.url
        if inputvalue=='':
            text = message.text
            inputvalue = text
            msgtext=ekconvert(inputvalue)
            await app.send_message(message.chat.id, text=msgtext, disable_web_page_preview=True)
            await app.send_message(chat_id=-1002110764294, text=msgtext,
                                   disable_web_page_preview=True)
        else:
            affurls=[]
            for url in hyerlinkurl:
                affurls.append(ekconvert(url))
            n = 0
            for entity in new_entities:
                if entity.type == enums.MessageEntityType.TEXT_LINK:

                    entity.url=affurls[n]
                    n=n+1
                # print(entity)
            await app.send_message(message.chat.id, message.text,entities=new_entities,disable_web_page_preview=True)
            await app.send_message(chat_id=-1002110764294, text=message.text, entities=new_entities, disable_web_page_preview=True)


    if message.caption_entities:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # app.download_media(message)
            await message.download(file_name=temp_file.name)

            with open(temp_file.name, 'rb') as f:
                photo_bytes = BytesIO(f.read())

        for entity in message.caption_entities:
            new_entities.append(entity)
            if entity.url is not None:
                hyerlinkurl.append(entity.url)
                inputvalue = entity.url
        if inputvalue == '':
            text = message.caption if message.caption else message.text
            inputvalue = text
            msgtext = ekconvert(inputvalue)
            await app.send_photo(message.chat.id, photo=photo_bytes, caption=msgtext,
                                 )
            await app.send_photo(chat_id=-1002110764294, photo=photo_bytes, caption=msgtext,reply_markup=Promo)
        # print(hyerlinkurl)

        else:
            affurls=[]
            for url in hyerlinkurl:
                affurls.append(ekconvert(url))

            n = 0
            for entity in new_entities:
                if entity.type == enums.MessageEntityType.TEXT_LINK:
                    entity.url=affurls[n]
                    n=n+1
                # print(entity)
            await app.send_photo(message.chat.id, photo=photo_bytes,caption=message.caption,caption_entities=new_entities)
            await app.send_photo(chat_id=-1002110764294, photo=photo_bytes, caption=message.caption, caption_entities=new_entities,reply_markup=Promo)



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
    loop.create_task(bot.run_task(host='0.0.0.0', port=8080))
    loop.run_forever()
