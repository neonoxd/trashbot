import asyncio
import random
import requests
import io
from PIL import Image
import time
import os
from dotenv import load_dotenv
from discord.ext import commands
import config
import shared

load_dotenv()


def check_user_twitch(user):
    endpoint = "https://api.twitch.tv/kraken/streams/{}"

    API_HEADERS = {
        'Client-ID': os.getenv("TWITCH_CLIENTID"),
        'Accept': 'application/vnd.twitchtv.v5+json',
    }
    url = endpoint.format(user)

    try:
        req = requests.get(url, headers=API_HEADERS)
        jsondata = req.json()
        if 'stream' in jsondata:
            if jsondata['stream'] is not None:  # stream is online
                return {"islive": True, "title": jsondata["stream"]["channel"]["status"],
                        "thumbnail": jsondata["stream"]["preview"]["large"]}
            else:
                return {"islive": False}
    except Exception as e:
        return {"islive": False}


def check_user_yt(channel_id):
    apikey = os.getenv("YT_APIKEY")
    url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={0}&type=video&eventType=live&key={1}"
    req = requests.get(url=url.format(channel_id, apikey))
    jsondata = req.json()
    try:
        is_live = jsondata["items"][0]["snippet"]["liveBroadcastContent"] == "live"
        thumbnail = jsondata["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        title = jsondata["items"][0]["snippet"]["title"]

        return {"islive": is_live, "thumbnail": thumbnail, "title": title}
    except Exception as e:
        return {"islive": False}


async def check_streams(ctx):
    while True:
        print("checking stream")
        streams = {}
        for usr, channel in config.trash_list["yt"].items():
            print("checking: {} : {} -> ".format(usr, channel), end="")
            streams[usr] = check_user_yt(channel)
            print(streams[usr]['islive'])
        for usr, channel in config.trash_list["twitch"].items():
            print("checking: {} : {} -> ".format(usr, channel), end="")
            streams[usr] = check_user_twitch(channel)
            print(streams[usr]['islive'])

        print(streams)
        shared.state["attachedChannels"][ctx.channel.id]["streamstate"]=streams
        #await ctx.send(streams)
        await asyncio.sleep(30)


async def get_captcha(captcha_id):
    response = requests.get('https://hardverapro.hu/captcha/{0}.png'.format(captcha_id), params={'t': time.time()})
    img = io.BytesIO(response.content)

    rgb_image = Image.open(img).convert("RGBA")
    double_size = (rgb_image.size[0] * 2, rgb_image.size[1] * 2)
    image = rgb_image.resize(double_size)

    bg = Image.open('resources/bg.png', 'r')
    text_img = Image.new('RGBA', (bg.width, bg.height), (0, 0, 0, 0))
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
