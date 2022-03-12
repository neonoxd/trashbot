import asyncio
import datetime
import io
import logging
import os
import random
import aiohttp
import discord
import timeago
from discord import Embed
from discord.ext import commands

from utils.helpers import create_alphanumeric_string

module_logger = logging.getLogger('trashbot.MiscCog')


class MiscCog(commands.Cog):
	def __init__(self, bot):
		module_logger.info("initializing MiscCog")
		self.bot = bot
		self.logger = module_logger

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		module_logger.debug(f"user updated {before}")
		guild_state = self.bot.state.get_guild_state_by_id(before.guild.id)
		if after.id in guild_state.forced_nicks:
			forced_nick = guild_state.forced_nicks[after.id]["nick"]
			if after.nick != forced_nick:
				await after.edit(nick=guild_state.forced_nicks[after.id]["nick"])

	@commands.command(name="mik")
	async def mik(self, ctx):
		now = datetime.datetime.now()
		embed = Embed(title="ezek fönek sogor 🤣", color=0xFF5733)
		event_list_str = []
		queue = ctx.bot.globals.queued_hotpots

		for r in list(queue.keys()):
			time_ago = timeago.format(queue[r]["when"], now, "hu")
			event_str = """"""
			event_str = event_str + f"""`[{time_ago}] - {queue[r]['author']} - {r}`"""
			event_list_str.append(event_str)

		if len(event_list_str):
			embed.add_field(name="\u200b", value="\n".join(event_list_str))

			embed.set_author(name="Kovács Tibor József", url="https://www.facebook.com/tibikevok.jelolj/",
							icon_url="https://cdn.discordapp.com/attachments/248727639127359490/913774079423684618/422971_115646341961102_1718197155_n.jpg")

			await ctx.send(embed=embed)

	@commands.command(name="kik", hidden=True)
	async def whomst(self, ctx):
		now = datetime.datetime.now()
		guild_state = self.bot.state.get_guild_state_by_id(ctx.message.guild.id)
		t_locale = random.choice(['zh_CN', 'hu', 'en'])
		if self.bot.user.mentioned_in(ctx.message):
			embed = Embed(title="kb ezek vagy nemtom", color=0xFF5733)
			event_list_str = []

			if len(guild_state.last_vc_events):
				for r in list(reversed(guild_state.last_vc_events)):
					event_str = """"""
					user = r.user.nick if r.user.nick is not None else r.user.name
					when = datetime.datetime.fromtimestamp(r.when)
					event_str = event_str + f"`[{timeago.format(when, now, t_locale)}] "
					if r.event:
						event_str = event_str + f"""{user} jött ide: {r.channel.name}`"""
					else:
						event_str = event_str + f"""{user} ment a g*ecibe`"""
					event_list_str.append(event_str)
			else:
				when = ctx.bot.globals.startup_at
				event_str = f"`[{timeago.format(when, now, t_locale)}] {random.choice(['sz*rtak a világra engem', 'keltem fel'])}`"
				event_list_str.append(event_str)

			embed.add_field(name="\u200b", value="\n".join(event_list_str))

			embed.set_author(name="Kovács Tibor József", url="https://www.facebook.com/tibikevok.jelolj/",
							 icon_url="https://cdn.discordapp.com/attachments/248727639127359490/913774079423684618/422971_115646341961102_1718197155_n.jpg")

			await ctx.send(embed=embed)

	@commands.command(name="ki", hidden=True)
	async def who(self, ctx, *args):
		guild_state = self.bot.state.get_guild_state_by_id(ctx.message.guild.id)
		if self.bot.user.mentioned_in(ctx.message):
			last_events = guild_state.last_vc_events

			if not len(last_events):
				await ctx.send("nemtom most keltem nem figyeltem")
			else:
				question = " ".join(args).replace("?", "").strip()

				if len(args) == 0:
					last_event = last_events[-1]

					await ctx.send(
						f"{random.choice(['ö', 'nem vok spicli de ö', 'sztem ö'])}" +
						f"{random.choice(['t láttam asszem feljönni', ' jött erre']) if last_event.event else ' lépett le'}: " +
						f"{last_event.user.name}"
					)

				elif question in ["joinolt", "van itt", "jött fel", "van itt"]:
					last_joined = next((event for event in last_events if event.event), None)
					if last_joined is not None:
						await ctx.send(
							f"{random.choice(['talán én...de az is lehet hogy ő', 'ez a köcsög', 'ö', 'ha valaki akk ö'])}: {last_joined.user.name}"
						)
					else:
						await ctx.send("senki...")

				elif question in ["volt az", "lépett ki", "lépett le", "dczett", "disconnectelt"]:
					last_left = next((event for event in last_events if not event.event), None)
					if last_left is not None:
						await ctx.send(
							f"{random.choice(['ez a köcsög', 'ö', 'ha valaki akk ö'])} lépett le: {last_left.user.name}"
						)
					else:
						await ctx.send("senki...")

			if random.randrange(0, 5) > 2:
				await asyncio.sleep(5)
				await ctx.send('👀')

	@commands.command(name='say', aliases=['mondd'])
	async def say(self, ctx, *args):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.message.delete()
		await ctx.send(' '.join(args))

	@commands.command(name='impostor', hidden=True)
	async def impost(self, ctx, *args):
		await ctx.message.delete()
		if len(args) > 0:
			impostor = args[0]
		else:
			impostor = random.choice(ctx.message.channel.members).mention
		tmpl = f""".      　。　　　　•　    　ﾟ　　。
　　.　　　.　　　  　　.　　　　　。　　   。　.
 　.　　      。　        ඞ   。　    .    •
   •        {impostor} was the impostor.　 。　.
　 　　。　　 　　　　ﾟ　　　.　    　　　.
,　　　　.　 .　　       ."""
		await ctx.send(tmpl)

	@commands.command(name="kot")
	async def kot(self, ctx):
		async with aiohttp.ClientSession() as session:
			async with session.get('http://aws.random.cat/meow') as r:
				if r.status == 200:
					js = await r.json()
					await ctx.send(js['file'])

	@commands.command(name="cook")
	async def cook(self, ctx, *args):
		if not len(args):
			await ctx.message.delete()
			return
		description = ' '.join(args)[:350]

		boundary = f'----WebKitFormBoundary{create_alphanumeric_string(16)}'
		request_id = create_alphanumeric_string(5)

		headers = {
			"accept": "*/*",
			"accept-language": "hu-HU,hu;q=0.9,en-US;q=0.8,en;q=0.7",
			"content-type": f"multipart/form-data; boundary={boundary}",
			"sec-fetch-dest": "empty",
			"sec-fetch-mode": "cors",
			"sec-fetch-site": "same-site",
			"sec-gpc": "1",
			"Referer": "https://hotpot.ai/",
			"Referrer-Policy": "strict-origin-when-cross-origin"
		}

		with aiohttp.MultipartWriter('form-data', boundary=boundary) as mpwriter:

			self.add_weird_form_field(mpwriter, "requestId", request_id)
			self.add_weird_form_field(mpwriter, "inputText", f"{description} in the style of an oil painting")
			self.add_weird_form_field(mpwriter, "outputDim", "256")
			self.add_weird_form_field(mpwriter, "numIterations", "400")

			await ctx.message.delete()
			queue = ctx.bot.globals.queued_hotpots
			queue[description] = {
				"author": ctx.message.author.name,
				"when": datetime.datetime.now()
			}
			module_logger.info(f"{ctx.message.author.id} queued: {description}")
			url = "https://ml.hotpot.ai"
			timeout = aiohttp.ClientTimeout(total=3600)
			try:
				async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
					async with session.post(url + '/text-art-api-bin', data=mpwriter) as r:
						if r.status == 200:
							js = await r.read()
							img = io.BytesIO(js)
							await ctx.send(file=discord.File(img, "hotpot.png"),
										   content=f"{description}\ntölle: {ctx.message.author.mention}")
							del queue[description]
						else:
							module_logger.error(r.status)
							module_logger.error(r.headers)
							module_logger.error(await r.read())
							del queue[description]
			except asyncio.TimeoutError as e:
				await ctx.send(f"ENNEK ANYI: {description}")
				del queue[description]
			except Exception as e:
				await ctx.send(f"AT VERTEK ENGEMET: {description}")
				if description in queue:
					module_logger.error(e, exc_info=True)
					del queue[description]

	@staticmethod
	def add_weird_form_field(mpwriter, fieldname, value):
		part = mpwriter.append(value)
		part.set_content_disposition("form-data", name=fieldname)
		part.headers.pop(aiohttp.hdrs.CONTENT_LENGTH, None)
		part.headers.pop(aiohttp.hdrs.CONTENT_TYPE, None)
		return part

	@commands.command(name="trash")
	async def get_live_statuses(self, ctx):
		import requests

		class Channel:
			def __init__(self, name, url, status=False):
				self.name = name
				self.url = url
				self.status = status

		live_keyword = '"LIVE"'
		cookies = dict(cookies_are=self.bot.globals.yt_cookie)
		headers = {"Content-Type": "text/html"}

		channel_list_path = 'usr/lists/trashyt.list' if os.path.isfile(
			'usr/lists/trashyt.list') else 'resources/lists/trashyt.list'
		with open(channel_list_path, 'r', encoding="utf8") as file:
			channel_list = file.readlines()

		channels_to_check = [Channel(channel_entry.split(";")[0], channel_entry.split(";")[1]) for channel_entry in channel_list]

		statuses = []
		for channel in channels_to_check:
			response = requests.get(f"https://www.youtube.com/{channel.url}", headers=headers, cookies=cookies)
			statuses.append(f"{channel.name} - {'LIVE' if live_keyword in response.content.decode('UTF-8') else 'OFFLINE'} - https://www.youtube.com/{channel.url.strip()}")
		await ctx.send("\r\n".join(statuses))


def setup(bot):
	bot.add_cog(MiscCog(bot))
