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

    return(data_value)
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
    if message.photo:
        text = message.caption if message.caption else message.text
        inputvalue = text

    # elif message.text:
    #     inputvalue = message.text
    # # print(message)
    #     # print(message.entities)
    # # print(inputvalue)
    hyerlinkurl=[]
    new_entities=[]

    if message.entities:
        for entity in message.entities:
            new_entities.append(entity)
            if entity.url is not None:
                hyerlinkurl.append(entity.url)
        # print(hyerlinkurl)
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
        for entity in message.caption_entities:
            new_entities.append(entity)
            if entity.url is not None:
                hyerlinkurl.append(entity.url)
        # print(hyerlinkurl)

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # app.download_media(message)
            await message.download(file_name=temp_file.name)

            with open(temp_file.name, 'rb') as f:
                photo_bytes = BytesIO(f.read())
        affurls=[]
        for url in hyerlinkurl:
            affurls.append(ekconvert(url))
            # affurl=ekconvert(url)
            # # print(affurl)
            # affurls.append()
        # print(affurls)
        # modified_caption = message.caption
        # for url in affurl:
        #     count=1
        #     modified_caption = modified_caption.replace("Buy Now", f'<a href="{url}">Buy now</a>', 1)
        #     # print(modified_caption)
        #     # count==count+1
        n = 0
        for entity in new_entities:
            if entity.type == enums.MessageEntityType.TEXT_LINK:

                entity.url=affurls[n]
                n=n+1
            # print(entity)
        await app.send_photo(message.chat.id, photo=photo_bytes,caption=inputvalue,caption_entities=new_entities)
        await app.send_photo(chat_id=-1002110764294, photo=photo_bytes, caption=inputvalue, caption_entities=new_entities,reply_markup=Promo)



if __name__ == '__main__':
    app.run()