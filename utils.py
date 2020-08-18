import random

import requests
import io
from PIL import Image
import time

from discord.ext import commands


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
        return '{0.author.mention} pofán csapta {1.mention}-t egy jó büdös hallal mert *{2}*'.format(ctx, to_slap, argument)
