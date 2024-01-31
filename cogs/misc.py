import asyncio
import datetime
import io
import logging
import random
from typing import Optional
import os

import aiohttp
import discord
import timeago
from discord import Embed, app_commands
from discord.ext import commands
from discord.ext.commands import Context
from discord import VoiceChannel

from utils.helpers import create_alphanumeric_string, get_resource_name_or_user_override
from utils.state import TrashBot
from utils.helpers import get_image_as_bytes
from utils.helpers import get_member_voice_channel
from datetime import datetime, time

module_logger = logging.getLogger('trashbot.MiscCog')


class MiscCog(commands.Cog):
	def __init__(self, bot: TrashBot):
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

	@app_commands.command(name="google-translate", description="mia neved angolul")
	async def google_translate(self, interaction: discord.Interaction, text: Optional[str] = None):

		if text is None:
			await interaction.response.send_message(file=discord.File(get_resource_name_or_user_override("img/tutoiral.jpg")))
		else:
			tl_map = {
				"a": "gee", "b": "eh", "c": "fin", "d": "tr", "e": "go", "f": "tax", "g": "stock", "k": "ou", "l": "08",
				"m": "in", "n": "fr", "o": "oo", "p": "ee", "q": "aa", "r": "ii", "s": "oo", "t": "uu", "u": "y",
				"v": "g", "w": "1", "x": "2", "y": "3", "z": "4",
			}
			translated_input = "".join([tl_map[tl] if tl in tl_map else " " for tl in text])

			if self.bot.state.is_expired("google-translate"):
				self.bot.state.add_timeout("google-translate", expiry_td=datetime.timedelta(minutes=10))
				await interaction.response.send_message(
					content=translated_input,
					file=discord.File(get_resource_name_or_user_override("img/accurate.png"))
				)
			else:
				await interaction.response.send_message(content=translated_input)

	@app_commands.command(name="laci", description="mikó vót")
	async def jamal(self, interaction: discord.Interaction):
		member_id = self.bot.globals.goofies["jamal"]
		guild = interaction.guild
		is_in_voice_channel = await get_member_voice_channel(member_id, guild)
		member = guild.get_member(member_id)

		if is_in_voice_channel: #laci on
			voice_channel: VoiceChannel = member.voice.channel
			response_text = random.choice(['konkretan most is itvan: ','lacibátya itt van most: ','FENTVAAAAAN!!! ITT: ','kajak feljöt 🙂🙂 itt: '])

			if datetime.now().weekday() not in [4, 5]: #not friday or saturday
            	#how much can he stay on today
				today_at_22 = datetime.combine(datetime.now().date(), time(22, 0))
				if datetime.now() < today_at_22: #are we before 22 today
					remaining_shaolin_time = f"\n{timeago.format(today_at_22, datetime.now(), 'hu')} mennie kell 😨😨"
				else:
					remaining_shaolin_time= f"\n{random.choice(['még fön van','lol még fentvan 🙂🙂','menj ma aludni 😂😂'])}"

			await interaction.response.send_message(f"{response_text} {str(voice_channel.name)} {remaining_shaolin_time}")

		else: #laci not on
			last_dt = self.bot.state.get_guild_state_by_id(interaction.guild.id).last_shaolin_appearance
			await interaction.response.send_message(f"{timeago.format(last_dt, datetime.now(), 'hu')} láttuk a férget legutóbb")
			

	@app_commands.command(name="ki", description="kik vót")
	async def who_simple_cmd(self, interaction: discord.Interaction):
		""" /ki """
		guild_state = self.bot.state.get_guild_state_by_id(interaction.guild.id)
		
		last_events = guild_state.last_vc_events

		if not len(last_events):
			await interaction.response.send_message("nemtom most keltem nem figyeltem")
		else:
			last_event = last_events[-1]
			if str(last_event.user.id) == str(self.bot.globals.goofies["jamal"]):
				await interaction.response.send_message(f"# LACI")
			else:
				await interaction.response.send_message(
				f"{random.choice(['ö', 'nem vok spicli de ö', 'sztem ö'])}" +
				f"{random.choice(['t láttam asszem feljönni', ' jött erre']) if last_event.event else ' lépett le'}: " +
				f"{last_event.user.name}"
			)

	@app_commands.command(name="kik", description="kik voltak szok")
	async def who_cmd(self, interaction: discord.Interaction):
		""" /kik """
		now = datetime.now()
		guild_state = self.bot.state.get_guild_state_by_id(interaction.guild.id)
		t_locale = random.choice(['zh_CN', 'hu', 'en'])
		embed = Embed(title="kb ezek vagy nemtom", color=0xFF5733)
		event_list_str = []

		if len(guild_state.last_vc_events):
			for r in list(reversed(guild_state.last_vc_events)):
				event_str = """"""
				user = r.user.nick if r.user.nick is not None else r.user.name
				when = datetime.fromtimestamp(r.when)
				event_str = event_str + f"`[{timeago.format(when, now, t_locale)}] "
				if r.event:
					event_str = event_str + f"""{user} jött ide: {r.channel.name}`"""
				else:
					event_str = event_str + f"""{user} ment a g*ecibe`"""
				event_list_str.append(event_str)
		else:
			when = self.bot.globals.startup_at
			event_str = f"`[{timeago.format(when, now, t_locale)}] {random.choice(['sz*rtak a világra engem', 'keltem fel'])}`"
			event_list_str.append(event_str)

		embed.add_field(name="\u200b", value="\n".join(event_list_str))

		embed.set_author(name="Kovács Tibor József", url="https://www.facebook.com/tibikevok.jelolj/",
							icon_url="https://cdn.discordapp.com/attachments/248727639127359490/913774079423684618/422971_115646341961102_1718197155_n.jpg")

		await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)

	@commands.command(name="ki", hidden=True)
	async def who(self, ctx: Context, *args):
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
	async def say(self, ctx: Context, *args):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.message.delete()
		await ctx.send(' '.join(args))

	@commands.command(name='impostor', hidden=True)
	async def impost(self, ctx: Context, *args):
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

	@app_commands.command(name="kot", description="kuld egy cecat")
	async def kot(self, interaction: discord.Interaction):
		await interaction.response.defer(thinking=True)
		async with aiohttp.ClientSession() as session:
			apikey = os.getenv("KOT_APIKEY")
			url = f'https://api.thecatapi.com/v1/images/search?api_key={apikey}&has_breeds=1'
			async with session.get(url) as r:
				if r.status == 200:
					js = await r.json()
					cat_data = js[0]
					image_url = cat_data['url']
					##	width = cat_data.get('width', 'nincsen')
					##	height = cat_data.get('height', 'nincsen')
					breeds = cat_data.get('breeds', [])
					origin = breeds[0].get('origin', 'nemtom')
					weight_data = breeds[0].get('weight', {})
					metric_weight = weight_data.get('metric', 'nemtomxd')
					if breeds and 'country_code' in breeds[0]:
						cc=breeds[0]['country_code']
					##ha van countrycode
					if cc:
						flag = f':flag_{cc.lower()}:'
					else:
						flag = ''

						##assemble message text			
					table_message= f""" 
                        {random.choice(['ceca🙂🙂🙂','macseg 🙂','mi a gyasz ez', 'majnem olyan mint a pütyök 🙂', 'ittvan', 'uj macsk 😘 kovács KKovács Gizella ErzsébetErzsébet 😘'])}
`|hol: {str(origin)}` {str(flag)} `|kilo: {str(metric_weight)}|` """
						##in case API sends breeds info - always if set in url: append breeds
					if breeds: 		
						breed_names = ', '.join(breed.get('name', 'nemtomxd') for breed in breeds)
						table_message += f"""`|fajta: {str(breed_names)}|`"""
						##assemble image
					image_bytes = await get_image_as_bytes(image_url)
					file = discord.File(io.BytesIO(image_bytes), filename="macsek.png")
						##send complete msg
					await interaction.followup.send(content=table_message, file=file)
				elif r.status == 429:
					await interaction.followup.send(f"sok a kérés báttya! ezt külték: {r.status}")
					self.logger.warning(f"resp {r}")
				else:
					self.logger.warning(f"resp {r}")

	@commands.command(name="cook")
	async def cook(self, ctx: Context, *args):
		"""
			DEPRECATED: probably got banned
			FIXME: maybe
		"""
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
				"when": datetime.now()
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
	async def get_live_statuses(self, ctx: Context):
		import requests

		class Channel:
			def __init__(self, name, url, status=False):
				self.name = name
				self.url = url
				self.status = status

		live_keyword = '"LIVE"'
		cookies = dict(cookies_are=self.bot.globals.yt_cookie)
		headers = {"Content-Type": "text/html"}

		with open(get_resource_name_or_user_override("lists/trashyt.list"), 'r', encoding="utf8") as file:
			channel_list = file.readlines()

		channels_to_check = [Channel(channel_entry.split(";")[0], channel_entry.split(";")[1]) for channel_entry in channel_list]

		statuses = []
		for channel in channels_to_check:
			response = requests.get(f"https://www.youtube.com/{channel.url}", headers=headers, cookies=cookies)
			statuses.append(f"{channel.name} - {'LIVE' if live_keyword in response.content.decode('UTF-8') else 'OFFLINE'} - <https://www.youtube.com/{channel.url.strip()}>")
		await ctx.send("\n".join(statuses))


async def setup(bot: TrashBot):
	await bot.add_cog(MiscCog(bot))
