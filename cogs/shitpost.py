import asyncio
import logging
import random

import discord
import requests
from discord.ext import commands

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


def has_link(string):
	import re
	# findall() has been used
	# with valid conditions for urls in string
	regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
	url = re.findall(regex, string)
	return [x[0] for x in url]


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


async def think(bot, message):
	channel = message.channel
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

	bg = Image.open('resources/bg.png', 'r')
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

	output = Image.open('resources/finally.jpg', 'r')

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
	ctx_guild = ctx.guild.id
	state = self.bot.cvars["state"]
	guild_state = state["guild"][ctx_guild]
	bee_state = guild_state["bee_state"]

	while True:
		if bee_state["active"] and bee_state["current_part"] < len(self.beescript):
			await ctx.send(self.beescript[bee_state["current_part"]])
			bee_state["current_part"] += 1
			if bee_state["current_part"] == len(self.beescript):
				bee_state["active"] = False
				bee_state["current_part"] = 0
				await asyncio.sleep(5)
				await ctx.send("na csak ennyit akartam")
		await asyncio.sleep(random.randrange(5, 10))


class ShitpostCog(commands.Cog):
	def __init__(self, bot):
		module_logger.info("initializing Shitpost")
		self.bot = bot
		self.logger = module_logger
		with open('resources/lists/zene.txt', 'r', encoding="utf8") as file:
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

		cimg = await get_captcha(self.bot.cvars["PHTOKEN"])
		await ctx.send(file=discord.File(cimg, 'getsee.png'))

	@commands.command(name='tenemos')
	async def tenemos(self, ctx):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.send(file=discord.File('resources/tenemos.jpg'))

	@commands.command(name='zene')
	async def zene(self, ctx):
		self.logger.info("command called: {}".format(ctx.command))
		embed = discord.Embed(description="-Leg job zenék",
							  title=random.choice(self.trek_list), color=0xfc0303)
		await ctx.send(embed=embed)

	@commands.command(name='beemovie')
	async def bmc(self, ctx, *args):
		self.logger.info("command called: {}".format(ctx.command))
		ctx_guild = ctx.guild.id
		state = self.bot.cvars["state"]
		guild_state = state["guild"][ctx_guild]

		if "bee_state" not in guild_state:
			guild_state["bee_state"] = {"active": True, "current_part": 0}
			ctx.bot.loop.create_task(beemovie_task(self, ctx))
		else:
			if len(args) > 0:
				guild_state["bee_state"]["current_part"] = 0
				await ctx.send("mar nemtom hol tartottam")
			else:
				guild_state["bee_state"]["active"] = not guild_state["bee_state"]["active"]

		print(state)
		if guild_state["bee_state"]["active"]:
			await ctx.send(random.choice(["szal akkor", "na mondom akkor"]))
		else:
			await ctx.send("akk m1...")

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return

		import datetime
		now = datetime.datetime.now()

		# setup state
		state = self.bot.cvars["state"]
		msg_guild = message.guild.id
		if msg_guild not in state["guild"]:
			state["guild"][msg_guild] = {"last_slur": now}
			self.logger.info("thinking activated for guild {}, channel: {}"
							 .format(message.guild.name, message.channel.name))
			self.bot.loop.create_task(think(self.bot, message))

		guild_state = state["guild"][msg_guild]
		msg_channel = message.channel.id
		if msg_channel not in guild_state:
			guild_state[msg_channel] = {}
			guild_state[msg_channel]["last_msgs"] = []

		# surprise spammers
		channel_state = guild_state[msg_channel]
		if len(message.content) > 0 and 'k!' not in message.content:  # TODO extract prefix
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
		roll = random.randrange(0, 100)

		# flip words meme
		posts = [
			"🆗 gya gec ⚰️\nfeltaláltam\n🧔🏿🤙🏻🧪{0}",
			"🆗 halod\n🧔🏿🤙🏻🧪{0}",
			"mondjuk inkab\n🧔🏿🤙🏻🧪{0}"
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

		# skippers smh
		if any(w in message.content for w in ["-skip", "!skip"]) and roll < 40:
			self.logger.info("got lucky with roll chance: %s" % roll)
			await message.channel.send("az jo köcsög volt")

		# random trash replies
		elif (now - guild_state["last_slur"]).total_seconds() > 600 \
				and "k!" not in message.content \
				and roll < 2:
			guild_state["last_slur"] = datetime.datetime.now()
			self.logger.info("got lucky with roll chance: %s" % roll)
			await message.channel.send(random.choices(population=self.bot.cvars["slurps"]["slurs"],
													  weights=self.bot.cvars["slurps"]["chances"])[0].format(
				message.author.id))
		# tts react
		if message.tts:
			for react in random.choice([["🇬", "🇪", "🇨", "🇮", "♿"], ["🆗"], ["🤬"], ["👀"]]):
				await message.add_reaction(react)

		# unflip
		if message.content == "(╯°□°）╯︵ ┻━┻":
			await message.channel.send("┬─┬ ノ( ゜-゜ノ)")

	@commands.Cog.listener()
	@commands.guild_only()
	async def on_typing(self, channel, user, when):
		await self.bot.change_presence(activity=discord.Game("latom h irsz geco {}".format(user)))
		await asyncio.sleep(5)
		await self.bot.change_presence(activity=discord.Game(
			random.choices(population=self.bot.cvars["statuses"]["statuses"],
						   weights=self.bot.cvars["statuses"]["chances"])[0]
		))


def setup(bot):
	bot.add_cog(ShitpostCog(bot))
