import asyncio
import random

import discord
import psycopg2
import requests
import io
from PIL import Image
import time
import os
from dotenv import load_dotenv
from psycopg2._psycopg import InterfaceError

import config
import shared
import datetime
import logging

load_dotenv()


def is_conn_alive(conn):
    from main import DATABASE_URL
    print("checking connection is alive")
    try:
        c = conn.cursor()
        c.execute("SELECT 1")
        print("conn alive")
        return conn
    except InterfaceError as oe:
        print("connection is closed, reopening")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        return conn


def read_slurs(conn):
    conn = is_conn_alive(conn)
    try:
        cursor = conn.cursor()
        select_slurs_query = "select * from slur_pool"
        cursor.execute(select_slurs_query)
        rows = cursor.fetchall()

        return {
            "slurs": [row[1] for row in rows],
            "chances": [row[2] for row in rows]
        }
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if conn:
            cursor.close()
            print("cursor closed")


def read_statuses(conn):
    conn = is_conn_alive(conn)
    try:
        cursor = conn.cursor()
        select_slurs_query = "select * from idle_pool"
        cursor.execute(select_slurs_query)
        rows = cursor.fetchall()

        return {
            "statuses": [row[1] for row in rows],
            "chances": [row[2] for row in rows]
        }
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if conn:
            cursor.close()
            print("cursor closed")


async def handle_beemovie_command(ctx, args):
    ctx_guild = ctx.guild.id
    guild_state = shared.state["guild"][ctx_guild]

    if "bee_state" not in guild_state:
        guild_state["bee_state"] = {"active": True, "current_part": 0}
        ctx.bot.loop.create_task(beemovie_task(ctx))
    else:
        if len(args) > 0:
            guild_state["bee_state"]["current_part"] = 0
            await ctx.send("mar nemtom hol tartottam")
        else:
            guild_state["bee_state"]["active"] = not guild_state["bee_state"]["active"]

    print(shared.state)
    if guild_state["bee_state"]["active"]:
        await ctx.send(random.choice(["szal akkor", "na mondom akkor"]))
    else:
        await ctx.send("akk m1...")


async def beemovie_task(ctx):
    ctx_guild = ctx.guild.id
    guild_state = shared.state["guild"][ctx_guild]
    bee_state = guild_state["bee_state"]

    while True:
        if bee_state["active"] and bee_state["current_part"] < len(shared.beescript):
            await ctx.send(shared.beescript[bee_state["current_part"]])
            bee_state["current_part"] += 1
            if bee_state["current_part"] == len(shared.beescript):
                bee_state["active"] = False
                bee_state["current_part"] = 0
                await asyncio.sleep(5)
                await ctx.send("na csak ennyit akartam")
        await asyncio.sleep(random.randrange(5, 10))


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
        roll_small = random.randrange(0, 1000)
        if roll_small < 1:
            logging.info("rolled %s" % roll_small)
            await mercy_maybe(bot, channel)
        elif roll_small < 5:
            logging.info("rolled %s" % roll_small)
            await channel.send("most majdnem ki nyirtam vkit")
        await asyncio.sleep(600)


async def mercy_maybe(bot, channel, timeout=30):
    logging.info("raffle created with timeout %s" % timeout)
    raffle = {
        "msgid": None,
        "date": None,
        "users": []
    }

    def check(reaction_obj, usr):
        return reaction_obj.message.id == raffle["msgid"]

    msg = await channel.send("A likolok közül kiválasztok egy szerencsés tulélöt, a töbi sajnos meg hal !! @here")
    raffle["msgid"] = msg.id
    raffle["date"] = datetime.datetime.now()
    raffle["users"] = []

    while (datetime.datetime.now() - raffle["date"]).total_seconds() < timeout \
            and int(timeout - (datetime.datetime.now() - raffle["date"]).total_seconds()) != 0:
        diff = (datetime.datetime.now() - raffle["date"]).total_seconds()

        timeout_reacc = int(timeout - diff)
        logging.info("time's tickin': {} seconds left".format(timeout_reacc))
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=timeout_reacc, check=check)
            raffle["users"].append(user.mention)
            logging.info("got reacc {} {}".format(reaction, user))
        except Exception as e:
            pass
    logging.info("raffle ended")
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
