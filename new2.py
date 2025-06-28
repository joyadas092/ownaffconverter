import json
from io import BytesIO

import requests
from pyrogram import Client, filters, enums
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
import logging
from urllib.parse import urlunparse, parse_qs, urlparse
from pyrogram.raw.types import MessageEntityUrl
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import asyncio
from quart import Quart
from unshortenit import UnshortenIt
from  dotenv import load_dotenv
import os
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
apitoken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2M2U2MjEwNjYwOWU1YWY4ZTc4OTU2NTEiLCJlYXJua2FybyI6IjI1MjM2ODEiLCJpYXQiOjE3MTQzMzcxMDZ9.WOP7a-VJpEvg5p1sOpujkFJlcGjk50rq55ixeyHunK4'

# Define a handler for the /start command
bot = Quart(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

source_channel_id = [-1002110764294]  # Replace with the source channel ID


def remove_amazon_affiliate_parameters(url):
    parsed_url = urlparse(url)
    # print(parsed_url)
    query_params = parse_qs(parsed_url.query)
    # print('query_params: '+str(query_params))
    if 'ru' in query_params:
        query_params = {key: value for key, value in query_params.items() if key == 'ru'}
        parsed_url = urlparse(query_params['ru'][0])
        query_params = parse_qs(parsed_url.query)

    # List of Amazon affiliate parameters to remove
    amazon_affiliate_params = ['tag', 'ref', 'linkCode', 'camp', 'creative', 'linkId', 'ref_', 'language', 'content-id',
                               '_encoding', 'dev', 'sprefix', 'srs', 'crid', 'smid', 'sid']

    # Remove the Amazon affiliate parameters from the query parameters
    cleaned_query_params = {key: value for key, value in query_params.items() if key not in amazon_affiliate_params}
    # Rebuild the URL with the cleaned query parameters
    cleaned_url = urlunparse(
        parsed_url._replace(query='&'.join([f'{key}={value[0]}' for key, value in cleaned_query_params.items()])))
    cleaned_url = cleaned_url.replace(' ', '+')

    return cleaned_url


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


def earnkaroapi(text):
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
        return 'None'
    else:
        return (data_value)


def ekconvert(text):
    unshortened_urls = {}
    urls = extract_link_from_text(text)
    for url in urls:
        if 'amazon' in url or 'tinyurl' in url or 'amzn' in url:
            # unshortened_urls[url] = tiny(
            #     create_amazon_affiliate_url(remove_amazon_affiliate_parameters(unshorten_url(url)), 'divyadeal-21'))
            unshortened_urls[url] = create_amazon_affiliate_url(remove_amazon_affiliate_parameters(unshorten_url(url)),
                                                                'divyadeal-21')
        else:
            unshortened_urls[url] = earnkaroapi(url)
    for original_url, unshortened_url in unshortened_urls.items():
        text = text.replace(original_url, unshortened_url)
    return text


@bot.route('/')
async def hello():
    return 'Hello, world!'


@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await app.send_message(message.chat.id, "ahaann")


@app.on_message(filters.chat(-1002060929372) | filters.user(5886397642))
async def handle_text(client, message):
    # app.set_parse_mode(enums.ParseMode.HTML)
    # print(message)
    Promo = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Deals HUB 🛒", url="https://t.me/addlist/FReIeSd3Hyg5NjJl"),
          InlineKeyboardButton("PriceHistory Deals 📉", url="https://t.me/+rTx5B9g6XYxmNmE1")],
         [InlineKeyboardButton("Main Channel 🔴", url="https://t.me/+HeHY-qoy3vsxYWU1")]
         ])
    Promo2 = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Deals HUB 🛒", url="https://t.me/addlist/FReIeSd3Hyg5NjJl")],
         [InlineKeyboardButton("Main Channel 🔴", url="https://t.me/+HeHY-qoy3vsxYWU1")]
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
        if "😱 Deal Time" in inputvalue:
            # Remove the part
            inputvalue = inputvalue.split("😱 Deal Time")[0]
        if 'extp' in inputvalue or 'myntr.in' in inputvalue or 'fkrt.co' in inputvalue:
            inputvalue = extp(inputvalue)

        # # print(inputvalue)
        # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        #     # app.download_media(message)
        #     await message.download(file_name=temp_file.name)

        #     with open(temp_file.name, 'rb') as f:
        #         photo_bytes = BytesIO(f.read())
        msgtext = ekconvert(inputvalue)
        await app.send_photo(message.chat.id, photo=message.photo.file_id, caption=msgtext)
        if 'amazon.in' in msgtext:
            await app.send_photo(chat_id=-1002110764294, photo=message.photo.file_id, caption=f'<b>{msgtext}</b>',
                                 reply_markup=Promo)
        else:
            await app.send_photo(chat_id=-1002198032644, photo=message.photo.file_id, caption=f'<b>{msgtext}</b>',
                                 reply_markup=Promo)

    elif message.text:
        inputvalue = message.text
        if '@Auto_Forward_Messages_Bot' in inputvalue:
            return None

        hyperlinkurl = []
        for entity in message.entities:
            # new_entities.append(entity)
            if entity.url is not None:
                hyperlinkurl.append(entity.url)
        pattern = re.compile(r'Buy Now')

        inputvalue = pattern.sub(lambda x: hyperlinkurl.pop(0), inputvalue).replace('Regular Price', 'MRP')

        if "😱 Deal Time" in inputvalue:
            # Remove the part
            inputvalue = inputvalue.split("😱 Deal Time")[0]
        if 'extp' in inputvalue or 'myntr.in' in inputvalue or 'fkrt.co' in inputvalue:
            inputvalue = extp(inputvalue)
        msgtext = ekconvert(inputvalue)

        await app.send_message(message.chat.id, text=msgtext, disable_web_page_preview=True)

        if 'amazon.in' in msgtext:
            await app.send_message(chat_id=-1002110764294, text=f'<b>{msgtext}</b>',
                                   disable_web_page_preview=True)
        else:
            await app.send_message(chat_id=-1002198032644, text=f'<b>{msgtext}</b>',
                                   disable_web_page_preview=True)
    if message.video:
        if message.caption:
            link = create_amazon_affiliate_url(
                remove_amazon_affiliate_parameters(unshorten_url(extract_link_from_text(message.caption)[0])),
                'divyadeal-21')
            # link=create_amazon_affiliate_url(remove_amazon_affiliate_parameters(), 'divyadeal-21'))
        else:
            link = 'https://amzn.to/3Vgst6o'

        # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        #     # app.download_media(message)
        #     await message.download(file_name=temp_file.name)

        #     with open(temp_file.name, 'rb') as f:
        #         video_bytes = BytesIO(f.read())
        #     with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
        #         temp_video_file.write(video_bytes.getvalue())
        #         temp_video_file.seek(0)

        # await app.send_video(chat_id=message.chat.id, video=temp_video_file.name, caption=message.caption,reply_markup=Promo)
        await app.send_video(chat_id=-1002194362897, video=message.video.file_id,
                             caption=f"<b>PRODUCT LINK ⏬⏬: \n\n<a href={link}>👉👉BUY ON AMAZON👈👈</a></b>\n\n#amazon #flipkart #meesho",
                             reply_markup=Promo2)


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
