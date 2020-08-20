import asyncio
import datetime
import random
import discord
from config import cfg
import shared

last_gecizes = datetime.datetime.now()


async def handle_on_typing(bot, channel, user, when):
    await bot.change_presence(activity=discord.Game("latom h irsz geco {}".format(user)))
    await asyncio.sleep(5)
    await bot.change_presence(activity=discord.Game(random.choice(shared.statuses)))


async def handle_on_message(bot, message):
    global last_gecizes
    now = datetime.datetime.now()
    roll = random.randrange(0, 100)

    if "-skip" in message.content and roll < 70:
        print("got lucky with roll chance: %s" % roll)
        await message.channel.send("az jo köcsög volt")

    if (now - last_gecizes).total_seconds() > 600 \
            and cfg["prefix"] not in message.content \
            and roll < 11:
        last_gecizes = datetime.datetime.now()
        print("got lucky with roll chance: %s" % roll)
        await message.channel.send(random.choice(shared.beszolasok).format(message.author.id))

    if message.tts:
        await message.add_reaction("🇬")
        await message.add_reaction("🇪")
        await message.add_reaction("🇨")
        await message.add_reaction("🇮")
        await message.add_reaction("♿")

    await bot.process_commands(message)
