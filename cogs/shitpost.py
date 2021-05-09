import asyncio
import logging
import random
import datetime

import discord
import requests
from discord.ext import commands

from cogs.rng import roll
from utils.helpers import has_link

module_logger = logging.getLogger('trashbot.Shitpost')

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


async def mercy_maybe(bot, channel, timeout=30):
	import datetime
	module_logger.info("raffle created with timeout %s" % timeout)
	cur_round = {
		"msgid": None,
		"date": None,
		"users": []
	}

	def check(reaction_obj, usr):
		return reaction_obj.message.id == cur_round["msgid"] and usr.mention not in cur_round["users"]

	msg = await channel.send("A likolok közül kiválasztok egy szerencsés tulélöt, a töbi sajnos meg hal !! @here")
	cur_round["msgid"] = msg.id
	cur_round["date"] = datetime.datetime.now()
	cur_round["users"] = []

	while (datetime.datetime.now() - cur_round["date"]).total_seconds() < timeout \
		and int(timeout - (datetime.datetime.now() - cur_round["date"]).total_seconds()) != 0:
		diff = (datetime.datetime.now() - cur_round["date"]).total_seconds()

		timeout_reacc = int(timeout - diff)
		module_logger.info("time's tickin': {} seconds left".format(timeout_reacc))
		try:
			reaction, user = await bot.wait_for('reaction_add', timeout=timeout_reacc, check=check)
			cur_round["users"].append(user.mention)
			module_logger.info("got reacc {} {}".format(reaction, user))
		except Exception as e:
			pass
	module_logger.info(f"raffle ended, users: {cur_round['users']}")
	if len(cur_round["users"]) > 0:
		await channel.send("az egyetlen tul élö {}".format(random.choice(cur_round["users"])))
	else:
		await channel.send("sajnos senki nem élte tul")


async def think(bot, channel):
	module_logger.debug(f"thinking activated for channel {channel} - {channel.id} on {channel.guild.name}")
	while True:
		roll_small = random.randrange(0, 1000)
		if roll_small < 1:
			module_logger.info("rolled %s" % roll_small)
			await mercy_maybe(bot, channel)
		elif roll_small < 5:
			module_logger.info("rolled %s" % roll_small)
			await channel.send("most majdnem ki nyirtam vkit")
		await asyncio.sleep(600)


async def get_captcha(captcha_id):
	import io
	from PIL import Image
	import time
	url = f'https://hardverapro.hu/captcha/{captcha_id}.png'
	module_logger.debug(f'url = {url}')
	response = requests.get(url, params={'t': time.time()})
	img = io.BytesIO(response.content)

	rgb_image = Image.open(img).convert("RGBA")
	double_size = (rgb_image.size[0] * 2, rgb_image.size[1] * 2)
	image = rgb_image.resize(double_size)

	bg = Image.open('resources/img/bg.png', 'r')
	text_img = Image.new('RGBA', (bg.width, bg.height), (0, 0, 0, 0))
	text_img.paste(bg, ((text_img.width - bg.width) // 2, (text_img.height - bg.height) // 2))
	text_img.paste(image, ((text_img.width - image.width) // 2, (text_img.height - image.height) // 2), image)
	img_byte_arr = io.BytesIO()
	text_img.save(img_byte_arr, format='PNG')
	img_byte_arr.seek(0)
	return img_byte_arr


def get_befli(bottom_text):
	from PIL import Image
	from PIL import ImageFont
	from PIL import ImageDraw
	import io

	output = Image.open('resources/img/finally.jpg', 'r')

	bg_w, bg_h = output.size
	draw = ImageDraw.Draw(output)
	font = ImageFont.truetype("impact.ttf", 72)

	top_text = random.choice(["VÉGRE GEC", "FELTALÁLTAM GECO"])
	tw, th = font.getsize(top_text)

	bw, bh = font.getsize(bottom_text)

	draw.text((bg_w / 2 - tw / 2, 0), top_text, (0, 0, 0), font=font)
	draw.text((bg_w / 2 - bw / 2, (bg_h - bh) - 10), bottom_text, (0, 0, 0), font=font)

	img_byte_arr = io.BytesIO()
	output.save(img_byte_arr, format='PNG')
	img_byte_arr.seek(0)
	return img_byte_arr


async def beemovie_task(self, ctx):
	guild_id = ctx.guild.id
	state = self.bot.state.get_guild_state_by_id(guild_id)

	while True:
		if state.bee_active and state.bee_page < len(self.beescript):
			await ctx.send(self.beescript[state.bee_page])
			state.bee_page += 1
			if state.bee_page == len(self.beescript):
				state.bee_active = False
				state.bee_page = 0
				await asyncio.sleep(5)
				await ctx.send("na csak ennyit akartam")
		await asyncio.sleep(random.randrange(5, 10))


async def reset_alert_states(bot):
	module_logger.info("resetting peter_alert state for all guilds")
	for guild_state in bot.state.guilds:
		guild_state.peter_alert = False
		guild_state.ghost_alerted_today = False


async def set_daily_tension(bot, tension=None):
	# TODO: option to only set it for 1 guild
	for guild_state in bot.state.guilds:
		module_logger.debug(f'setting tension for guild : {guild_state.id}')

		guild_state.tension = tension if tension is not None else roll("100")
		guild = discord.utils.get(bot.guilds, id=guild_state.id)
		channel = guild.system_channel

		plus90 = [
			"https://www.youtube.com/watch?v=CDJhBTUg9Zw",  # rero zone
			"Grandmasta Pete - Mérés",
			"x̰̫̘̮́͠ḑ̨̟̝͎͓̮̬͎̜͍̬̬͍͉͕̹̘͞",
			"nem bántás nap",
			"https://www.youtube.com/watch?v=Xf6Geh82vXg"
		]

		plus50 = [
			"régi kazetá pejáco javitás",
			"xanox44 homemade vape video"
		]

		sub50 = [
			"https://www.youtube.com/watch?v=A_6wm8HVaVY",
			"Aleksandr Pistoletov - Gladiator",
			"Kibaszott Stryker",
			"lecsalos live"
		]

		t_str = f'{guild_state.tension}%'
		if guild_state.tension > 90:
			tension = random.choice([t_str] + plus90)
		elif guild_state.tension in [69, 420]:
			tension = t_str
		elif guild_state.tension > 50:
			tension = random.choice([t_str] + plus50)
		else:
			tension = random.choice([t_str] + sub50)

		t_msg = f'mai vilag tenszion: **{tension}**'

		#  IDEA: roll for random skulls, tbd what they do

		skulls = []

		if guild_state.tension < 50:
			skulls.append("cement: off")

		if guild_state.tension == 69:
			skulls.append("NICE 😏")

		if len(skulls) > 0:
			t_msg += f'\n **skulls:** {", ".join(skulls)}'

		await channel.send(t_msg)


class ShitpostCog(commands.Cog):
	def __init__(self, bot):
		module_logger.info("initializing Shitpost")
		self.bot = bot
		self.logger = module_logger
		with open('resources/lists/best.list', 'r', encoding="utf8") as file:
			self.trek_list = file.read().split("\n\n")
		with open('resources/beemovie.txt', 'r', encoding="utf8") as file:
			self.beescript = file.read().split("\n\n  \n")

	@commands.command(name='befli', hidden=True)
	async def befli(self, ctx):
		self.logger.info("command befli: {}".format(ctx.command))
		beflimg = get_befli("befli")
		await ctx.send(file=discord.File(beflimg, 'befli.jpg'))

	@commands.command(name='captcha')
	async def captcha(self, ctx):
		self.logger.info("command called: {}".format(ctx.command))

		cimg = await get_captcha(self.bot.globals.ph_token)
		await ctx.send(file=discord.File(cimg, 'getsee.png'))

	@commands.command(name='tenemos')
	async def tenemos(self, ctx):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.send(file=discord.File('resources/img/tenemos.jpg'))

	@commands.command(name='zene')
	async def zene(self, ctx):
		self.logger.info("command called: {}".format(ctx.command))
		embed = discord.Embed(description="-Leg job zenék",
							  title=random.choice(self.trek_list), color=0xfc0303)
		await ctx.send(embed=embed)

	@commands.command(name='beemovie')
	async def bmc(self, ctx, *args):
		self.logger.info("command called: {}".format(ctx.command))

		guild_id = ctx.guild.id
		guild_state = self.bot.state.get_guild_state_by_id(guild_id)

		if not guild_state.bee_initialized:
			guild_state.bee_initialized = True
			guild_state.bee_active = True
			ctx.bot.loop.create_task(beemovie_task(self, ctx))
		else:
			if len(args) > 0:
				guild_state.bee_page = 0
				await ctx.send("mar nemtom hol tartottam")
			else:
				guild_state.bee_active = not guild_state.bee_active

		if guild_state.bee_active:
			await ctx.send(random.choice(["szal akkor", "na mondom akkor"]))
		else:
			await ctx.send("akk m1...")

	@commands.command(name='tension')
	async def show_tension(self, ctx):
		tension = self.bot.state.get_guild_state_by_id(ctx.guild.id).tension
		module_logger.warning(tension)
		await ctx.channel.send(f'mai vilag tenszio: **{tension}%**')

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):

		if before.channel is None and after.channel is not None:  # user connected
			guild = after.channel.guild
			guild_state = self.bot.state.get_guild_state_by_id(guild.id)
			guild_state.last_vc_joined = member

			#  p alert
			if self.bot.globals.p_id == member.id:
				if not guild_state.peter_alert and guild_state.tension > 90:
					await guild.system_channel.send(file=discord.File('resources/img/peter_alert.png'))
					guild_state.peter_alert = True
					module_logger.debug("PETER ALERT!!!!!!!")

			#  ghosts alert
			elif member.id in self.bot.globals.ghost_ids:
				if not guild_state.ghost_alerted_today and guild_state.tension < 90:
					msg_text = f"*{self.bot.globals.t_states[guild_state.ghost_state % 3]}*"
					guild_state.increment_ghost()
					await after.channel.guild.system_channel.send(msg_text)
					guild_state.ghost_alerted_today = True
		elif before.channel is not None and after.channel is None:  # user disconnected
			#  sz shleep event
			if self.bot.globals.sz_id == member.id:
				now = datetime.datetime.now()
				if now.hour >= 21 or now.hour <= 3:
					guild = before.channel.guild
					await guild.system_channel.send(file=discord.File('resources/img/szabosleep.png'))

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user or not message.guild:
			return

		now = datetime.datetime.now()
		chance = random.randrange(0, 100)

		guild_state = self.bot.state.get_guild_state_by_id(message.guild.id)
		current_tension = guild_state.tension

		if guild_state.get_channel_state_by_id(message.channel.id) is None:
			guild_state.track_channel(message.channel.id)

		await self.sentience_spam(message)

		await self.sentience_flipper(message, chance)

		if current_tension is not None and current_tension > 50:
			await self.sentience_reply(message, now, chance)

		if message.author.id in [self.bot.globals.p_id, self.bot.globals.sz_id] and chance == 17:
			await message.channel.send(file=discord.File("resources/img/forklift.png", 'forklift.png'),
									   content=message.author.mention)

		# async for entry in message.guild.audit_logs(limit=100, action=discord.AuditLogAction.member_disconnect):
		#	module_logger.warning(f'auditlog {entry.id} - {entry.action}, user: {entry.user}, tgt: {entry.target}')

		if message.tts:
			for react in random.choice([["🇬", "🇪", "🇨", "🇮", "♿"], ["🆗"], ["🤬"], ["👀"]]):
				await message.add_reaction(react)

		if message.content == "(╯°□°）╯︵ ┻━┻":
			await message.channel.send("┬─┬ ノ( ゜-゜ノ)")

	@commands.Cog.listener()
	@commands.guild_only()
	async def on_typing(self, channel, user, when):
		await self.bot.change_presence(activity=discord.Game("latom h irsz geco {}".format(user)))
		await asyncio.sleep(5)
		await self.bot.change_presence(activity=discord.Game(
			random.choice(self.bot.globals.statuses)
		))

	async def sentience_spam(self, message):
		# surprise spammers
		guild_state = self.bot.state.get_guild_state_by_id(message.guild.id)
		channel_state = guild_state.get_channel_state_by_id(message.channel.id)
		if len(message.content) > 0 and 'k!' not in message.content and not self.bot.user.mentioned_in(message):  # TODO extract prefix
			channel_state.add_msg(message)
			if channel_state.shall_i():
				await asyncio.sleep(1)
				await message.channel.send(message.content)

	async def sentience_reply(self, message, now, roll):
		guild_state = self.bot.state.get_guild_state_by_id(message.guild.id)
		# skippers smh
		if any(skip_word in message.content for skip_word in ["-skip", "!skip"]) and roll < 40:
			self.logger.info("got lucky with roll chance: %s" % roll)
			await message.channel.send("az jo köcsög volt")

		# random trash replies
		elif (now - guild_state.last_slur_dt).total_seconds() > 600 \
				and "k!" not in message.content \
				and roll < 2:
			guild_state.last_slur_dt = datetime.datetime.now()
			self.logger.info("got lucky with roll chance: %s" % roll)
			await message.channel.send(random.choice(self.bot.globals.slurs).format(message.author.id))

	@staticmethod
	async def sentience_flipper(message, roll):
		# flip words meme
		posts = [
			"🆗 gya gec ⚰️\nfeltaláltam\n🧔🏿🤙🏻🧪{0}",
			"🆗 halod\n🧔🏿🤙🏻🧪{0}",
			"mondjuk inkab\n🧔🏿🤙🏻🧪{0}",
			"{0}?👀",
			"mmmmmmmmmmmmmmmm...{0}?"
		]
		words = {**fwd, **dict([(value, key) for key, value in fwd.items()])}
		themsg = ""
		if len(message.content.split(" ")) == 1 and len(has_link(message.content)) == 0 and \
				'k!' not in message.content:
			for word in words.keys():
				if word in message.content:
					themsg = message.content.replace(word, words[word])
		if len(themsg) > 0 and roll > 50:
			if len(themsg) < 16 and roll > 80:
				beflimg = get_befli(themsg)
				await message.channel.send(file=discord.File(beflimg, 'befli.jpg'))
			else:
				await message.channel.send(random.choice(posts).format(themsg))


def setup(bot):
	bot.add_cog(ShitpostCog(bot))
