import asyncio
import datetime
import random
import discord
from config import cfg
import shared
import logging


async def handle_on_typing(bot, channel, user, when):
    await bot.change_presence(activity=discord.Game("latom h irsz geco {}".format(user)))
    await asyncio.sleep(5)
    await bot.change_presence(activity=discord.Game(random.choices(population=shared.statuses["statuses"],
                                                                   weights=shared.statuses["chances"])[0]))


def has_link(string):
    import re
    # findall() has been used
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]

async def handle_on_message(bot, message):
    # initialize state
    msg_guild = message.guild.id
    if msg_guild not in shared.state["guild"]:
        from utils import think
        shared.state["guild"][msg_guild] = {"last_slur": datetime.datetime.now()}
        # init sentience
        logging.info("thinking activated for guild {}, channel: {}"
                     .format(message.guild.name, message.channel.name))
        bot.loop.create_task(think(bot, message))
    guild_state = shared.state["guild"][msg_guild]

    # init message tracker
    msg_channel = message.channel.id
    if msg_channel not in guild_state:
        guild_state[msg_channel] = {}
        guild_state[msg_channel]["last_msgs"] = []

    # surprise spammers
    channel_state = guild_state[msg_channel]
    if len(message.content) > 0:
        if len(channel_state["last_msgs"]) == 3:
            del channel_state["last_msgs"][0]
            channel_state["last_msgs"].append(hash(message.content))
        else:
            channel_state["last_msgs"].append(hash(message.content))
        msgs = channel_state["last_msgs"]
        if msgs[1:] == msgs[:-1] and len(msgs) == 3:
            await asyncio.sleep(1)
            await message.channel.send(message.content)

    # roll for sentience
    now = datetime.datetime.now()
    roll = random.randrange(0, 100)

    fwd = {
        "ki": "be",
        "fel": "le",
        "össze": "szét",
        "oda": "vissza",
        "fönn": "lenn",
        "fent": "lent",
        "felül": "alul",
        "áll": "ül"
    }
    words = {**fwd, **dict([(value, key) for key, value in fwd.items()])}
    themsg = ""
    if len(message.content.split(" ")) == 1 and len(has_link(message.content)) == 0:
        for word in words.keys():
            if word in message.content:
                themsg = message.content.replace(word, words[word])
    if len(themsg) > 0 and roll > 50:
        await message.channel.send("🆗 gya gec ⚰️\nfeltaláltam\n🧔🏿🤙🏻🧪{0}".format(themsg))

    if "-skip" in message.content and roll < 40:
        logging.info("got lucky with roll chance: %s" % roll)
        await message.channel.send("az jo köcsög volt")

    elif (now - guild_state["last_slur"]).total_seconds() > 600 \
            and cfg["prefix"] not in message.content \
            and roll < 2:
        guild_state["last_slur"] = datetime.datetime.now()
        logging.info("got lucky with roll chance: %s" % roll)
        await message.channel.send(random.choices(population=shared.slurps["slurs"],
                                                  weights=shared.slurps["chances"])[0].format(message.author.id))

    if message.tts:
        for react in random.choice([["🇬", "🇪", "🇨", "🇮", "♿"], ["🆗"], ["🤬"], ["👀"]]):
            await message.add_reaction(react)

    if message.content == "(╯°□°）╯︵ ┻━┻":
        await message.channel.send("┬─┬ ノ( ゜-゜ノ)")

    await bot.process_commands(message)
