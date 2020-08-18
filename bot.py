import io
import random
import time
import os

import discord
import requests
from PIL import Image
from discord.ext import commands
from dotenv import load_dotenv

from config import cfg

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PHToken = "92a95ab0a3f4d2de"

with open('zene.txt', 'r', encoding="utf8") as file:
    zenek = file.read().split("\n\n")


def getCaptcha(captchaId):
    response = requests.get('https://hardverapro.hu/captcha/{0}.png'.format(captchaId), params={'t': time.time()})
    img = io.BytesIO(response.content)

    image = Image.open(img).convert("RGBA")
    bg = Image.open('bg.png', 'r')
    text_img = Image.new('RGBA', (600, 320), (0, 0, 0, 0))
    text_img.paste(bg, ((text_img.width - bg.width) // 2, (text_img.height - bg.height) // 2))
    text_img.paste(image, ((text_img.width - image.width) // 2, (text_img.height - image.height) // 2), image)
    imgByteArr = io.BytesIO()
    text_img.save(imgByteArr, format='PNG')
    imgByteArr.seek(0)
    return imgByteArr


bot = commands.Bot(command_prefix=cfg["prefix"])

class Slapper(commands.Converter):
    async def convert(self, ctx, argument):
        to_slap = random.choice(ctx.guild.members)
        return '{0.author.mention} pofán csapta {1.mention}-t egy jó büdös hallal mert *{2}*'.format(ctx, to_slap, argument)

@bot.command(name='hal')
async def slap(ctx, *, reason: Slapper):
    await ctx.send(reason)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print("{}".format(message))
    print("{}".format(message.content))
    print(message.author.id)
    if message.author.id == 232184416259014657 and cfg["prefix"] not in message.content:
        await message.channel.send("kit érdekel <@{}>".format(message.author.id))
    await bot.process_commands(message)


@bot.command(name='captcha', description="random PH captcha")
async def captcha(ctx):
    cimg = getCaptcha(PHToken)
    await ctx.send(file=discord.File(cimg, 'geci.png'))


@bot.command(name='zene', description="random leg job zene idézet")
async def zene(ctx):
    await ctx.send(random.choice(zenek))


@bot.command(name='arena', description="ketrecharc bunyo, hasznalat: {0}arena @user1 @user2 ...".format(cfg["prefix"]))
async def fight(ctx, *args):
    if len(args)==0:
        return
    await ctx.send("a ketrec harc gyöz tese: {}".format(random.choice(args)))


@bot.command(name='say', description="bemondom ha irsz utana valamit")
async def captcha(ctx, *args):
    await ctx.send(' '.join(args))


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("bohoc kodom"))
    print("ready")


@bot.event
async def on_typing(channel, user, when):
    await bot.change_presence(activity=discord.Game("latom h irsz geco {}".format(user)))
bot.run(TOKEN)
