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

    if "-skip" in message.content:
        await message.channel.send("az jo köcsög volt")

    if (now - last_gecizes).total_seconds() > 120 \
            and cfg["prefix"] not in message.content \
            and random.randrange(0,100) < 11:
        last_gecizes = datetime.datetime.now()
        await message.channel.send(random.choice(shared.beszolasok).format(message.author.id))

    if message.tts:
        await message.add_reaction("🇬")
        await message.add_reaction("🇪")
        await message.add_reaction("🇨")
        await message.add_reaction("🇮")

    #guild = message.channel.guild
    #emoji = discord.utils.get(guild.emojis, name='alien1')
    #if emoji:
    #    await message.add_reaction(emoji)

    await bot.process_commands(message)
