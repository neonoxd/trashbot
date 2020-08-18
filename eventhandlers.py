import asyncio
import datetime
import random
import discord
from config import cfg

last_gecizes = datetime.datetime.now()


async def handle_on_typing(bot, channel, user, when,statuses):
    print("channel: {0}, user: {1}, when: {2}".format(channel, user, when))
    await bot.change_presence(activity=discord.Game("latom h irsz geco {}".format(user)))
    await asyncio.sleep(5)
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


async def handle_on_message(bot, message):
    global last_gecizes
    now = datetime.datetime.now()

    if (now - last_gecizes).total_seconds() > 10 \
            and message.author.id in cfg["goofies"] and cfg["prefix"] not in message.content \
            and random.choice([True, False]):
        last_gecizes = datetime.datetime.now()
        await message.channel.send("kit érdekel <@{}>".format(message.author.id))


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
