import asyncio
import json
import logging

import aiohttp
import discord
from discord.ext import commands
import uuid
import os


module_logger = logging.getLogger('trashbot.TtsEngine')


class TtsEngine(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		module_logger.info("initializing TtsEngine")

	@commands.command(name="trams")
	async def trams(self, ctx, *, args):
		url = "https://mumble.stream/speak"
		headers = {
			"Accept": "application/json",
			"Content-Type": "application/json"
		}
		body = {
			"speaker": "donald-trump",
			"text": args
		}
		module_logger.info(f'asking tramps to say {args}')

		await ctx.message.delete()

		async with ctx.typing():
			async with aiohttp.ClientSession() as session:
				async with session.post(url=url, headers=headers, data=json.dumps(body)) as r:
					if r.status == 200:
						f = await r.read()
						filename = f'{str(uuid.uuid4())}.wav'
						with open(filename,'wb') as f2:
							f2.write(f)
					else:
						t = await r.text()
						module_logger.error("something went wrong")
						await ctx.send("mind1...")

		ctx.voice_client.play(discord.FFmpegPCMAudio(executable=self.bot.cvars["FFMPEG_PATH"], source=filename), after=lambda e: os.remove(filename))


def setup(bot):
	bot.add_cog(TtsEngine(bot))
