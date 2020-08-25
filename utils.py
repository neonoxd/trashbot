import asyncio
import random

import discord
import requests
import io
from PIL import Image
import time
import os
from dotenv import load_dotenv
from discord.ext import commands
import config
import shared
import datetime
import logging

load_dotenv()


async def beemovie_task(ctx):
    while True:
        print(shared.state["beechannels"])
        if bool({k: v for k, v in shared.state["beechannels"].items() if v['attached']}):
            await ctx.send(shared.beescript[shared.state["beechannels"][ctx.channel.id]["current_page"]])
            shared.state["beechannels"][ctx.channel.id]["current_page"] += 1
        await asyncio.sleep(random.randrange(30, 300))

async def check_user_twitch(user_id):
    endpoint = "https://api.twitch.tv/kraken/streams/{}"

    headers = {
        'Client-ID': os.getenv("TWITCH_CLIENTID"),
        'Accept': 'application/vnd.twitchtv.v5+json',
    }
    url = endpoint.format(user_id)

    try:
        req = requests.get(url, headers=headers)
        jsondata = req.json()
        if req.status_code != 200:
            print("request returned with code: {}, \n response json: {}", req.status_code, jsondata)
            return {"islive": False}
        if 'stream' in jsondata:
            if jsondata['stream'] is not None:  # stream is online
                return {"islive": True, "title": jsondata["stream"]["channel"]["status"],
                        "thumbnail": jsondata["stream"]["preview"]["large"]}
            else:
                return {"islive": False}
    except Exception as e:
        return {"islive": False}


async def check_and_notify(ctx, oldstate, newstate):
    trashmap = {_k[1]: {"type": _k[0], "id": _k[2], "link": _k[3], "nick": _k[4]} for _k in shared.trashes for _v in
                tuple(_k)}

    if oldstate is None:
        print("no old state, current state: {}".format(newstate))
        lives = {k: v for k, v in newstate.items() if v['islive']}
        for live in lives.items():
            mapped = trashmap[live[0]]
            embed = discord.Embed(description=mapped["link"], title="{} fellötte a lájvszot:".format(mapped["nick"])
                                  , color=0xfc0303)
            embed.set_image(url=live[1]["thumbnail"])
            await ctx.send(embed=embed)
    elif oldstate != newstate:
        print("states dont match")
        lives = {k: v for k, v in newstate.items() if v['islive']}
        for live in lives.items():
            if not oldstate[live[0]]["islive"]:
                print("{} went live since last check".format(live[0]))
                mapped = trashmap[live[0]]
                embed = discord.Embed(description=mapped["link"], title="{} fellötte a lájvszot:".format(mapped["nick"])
                                      , color=0xfc0303)
                embed.set_image(url=live[1]["thumbnail"])
                await ctx.send(embed=embed)


async def get_trashwatch_youtube_list():
    TW_URL = os.getenv("TW_URL")
    url = "{}/list".format(TW_URL)
    try:
        req = requests.get(url, headers={})
        jsondata = req.json()
        print(type(jsondata))
        return jsondata
    except Exception as e:
        return {}


async def check_streams(ctx):
    while True:
        print("check_streams triggered")
        # is there a channel with trashwatch on
        if bool({k: v for k, v in shared.state["attachedChannels"].items() if v['attached']}):
            print("checking channels")
            streams = {}
            # get current status of channels
            for type, name, id, link, nick in shared.trashes:
                print("checking: {} : {} -> islive: ".format(name, id), end="")
                if type == "twitch":
                    streams[name] = await check_user_twitch(id)
                print(streams[name]['islive'])
            yt_streams = await get_trashwatch_youtube_list()
            print(streams)

            # set initial state of channels or refresh, and notify
            if "streamstate" not in shared.state["attachedChannels"][ctx.channel.id]:
                print("no stream state yet, adding last")
                shared.state["attachedChannels"][ctx.channel.id]["streamstate"] = streams
                await check_and_notify(ctx, None, streams)
            elif shared.state["attachedChannels"][ctx.channel.id]["streamstate"] != streams:
                await check_and_notify(ctx, shared.state["attachedChannels"][ctx.channel.id]["streamstate"], streams)
                shared.state["attachedChannels"][ctx.channel.id]["streamstate"] = streams
        else:
            print("no channels are attached to trashwatch")
        await asyncio.sleep(config.cfg["trashwatch_interval"])


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


async def think(bot, message):
    channel = message.channel

    while True:
        logging.info("thought")
        roll = random.randrange(0, 1000)
        if roll < 5:
            logging.info("rolled %s" % roll)
            await doraffle(bot, channel)
        elif roll < 10:
            logging.info("rolled %s" % roll)
            await channel.send("most majdnem ki nyirtam vkit")
        await asyncio.sleep(600)


async def doraffle(bot, channel, timeout=30):
    logging.info("raffle created with timeout %s" % timeout)
    raffle = {
        "msgid": None,
        "date": None,
        "users": []
    }

    def check(reaction_obj, user):
        return reaction_obj.message.id == raffle["msgid"]

    msg = await channel.send("A likolok közül kiválasztok egy szerencsés tulélöt, a töbi sajnos meg hal !! @here")
    raffle["msgid"] = msg.id
    raffle["date"] = datetime.datetime.now()
    raffle["users"] = []

    while (datetime.datetime.now() - raffle["date"]).total_seconds() < timeout \
            and int(timeout - (datetime.datetime.now() - raffle["date"]).total_seconds()) != 0:
        diff = (datetime.datetime.now() - raffle["date"]).total_seconds()
        logging.info("raffle time: {}".format(diff))

        timeout_reacc = int(timeout-diff)
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=timeout_reacc, check=check)
            raffle["users"].append(user.mention)
            logging.info("got reacc {} {}".format(reaction, user))
            reaction, user = None, None
        except Exception as e:
            pass
    logging.info("raffle ended")
    raffle["active"] = False
    if len(raffle["users"]) > 0:
        await channel.send("az egyetlen tul élö {}".format(random.choice(raffle["users"])))
    else:
        await channel.send("sajnos senki nem élte tul")


def roll(args):
    print(args)
    if len(args) == 1:
        return random.randrange(0, int(args[0]))
    elif len(args) == 2:
        return random.randrange(int(args[0]), int(args[1]))
    else:
        return random.randrange(0, 100)


class Slapper(commands.Converter):
    async def convert(self, ctx, argument):
        to_slap = random.choice(ctx.guild.members)
        return '{0.author.mention} pofán csapta {1.mention}-t egy jó büdös hallal mert *{2}*'.format(ctx, to_slap,
                                                                                                     argument)
