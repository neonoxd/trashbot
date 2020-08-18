import asyncio
import random
import requests
import io
from PIL import Image
import time
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()


def checkUser(user):
    TWITCH_STREAM_API_ENDPOINT_V5 = "https://api.twitch.tv/kraken/streams/{}"

    API_HEADERS = {
        'Client-ID': os.getenv("TWITCH_CLIENTID"),
        'Accept': 'application/vnd.twitchtv.v5+json',
    }
    url = TWITCH_STREAM_API_ENDPOINT_V5.format(user)

    try:
        req = requests.get(url, headers=API_HEADERS)
        jsondata = req.json()
        print(jsondata)
        if 'stream' in jsondata:
            if jsondata['stream'] is not None:  # stream is online
                return {"islive":True, "title":jsondata["stream"]["channel"]["status"], "thumbnail":jsondata["stream"]["preview"]["large"]}
            else:
                return {"islive": False}
    except Exception as e:
        return {"islive": False}


def checkuserYt(channelId):
    apikey = os.getenv("YT_APIKEY")
    url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={0}&type=video&eventType=live&key={1}"
    req = requests.get(url=url.format(channelId, apikey))
    jsondata = req.json()
    try:
        live = jsondata["items"][0]["snippet"]["liveBroadcastContent"]
        thumbnail = jsondata["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        title = jsondata["items"][0]["snippet"]["title"]
        is_live = True

        return {"islive": is_live, "thumbnail": thumbnail, "title": title}
    except Exception as e:
        return {"islive": False}


async def check_streams(ctx):
    while True:
        print("checking stream")
        streams = {
            "tibi": checkuserYt("UCxA1n--ZPGIWzFEZ98aLzTQ"),
            "nagylaci": checkuserYt("UCxFpm3Qlpbe2Nunm02rtXXw"),
            "martin": checkuserYt("UCVXMCQyIAhvbrH0lyRb9MMQ"),
            "sodi": checkUser("235138165"),
            "bturbo": checkUser("37738094")
        }
        print(streams)
        await ctx.send(streams)
        await asyncio.sleep(30)


def get_captcha(captchaId):
    response = requests.get('https://hardverapro.hu/captcha/{0}.png'.format(captchaId), params={'t': time.time()})
    img = io.BytesIO(response.content)

    image = Image.open(img).convert("RGBA")
    bg = Image.open('bg.png', 'r')
    text_img = Image.new('RGBA', (600, 320), (0, 0, 0, 0))
    text_img.paste(bg, ((text_img.width - bg.width) // 2, (text_img.height - bg.height) // 2))
    text_img.paste(image, ((text_img.width - image.width) // 2, (text_img.height - image.height) // 2), image)
    img_byte_arr = io.BytesIO()
    text_img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


class Slapper(commands.Converter):
    async def convert(self, ctx, argument):
        to_slap = random.choice(ctx.guild.members)
        return '{0.author.mention} pofán csapta {1.mention}-t egy jó büdös hallal mert *{2}*'.format(ctx, to_slap,
                                                                                                     argument)
