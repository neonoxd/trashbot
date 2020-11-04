import asyncio
import logging
import os
import random

import discord
from discord.ext import commands

module_logger = logging.getLogger('trashbot.SoundBoardCog')


class SoundBoardCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.logger = module_logger
		module_logger.info("initializing SoundBoardCog")
		self.sounds = self.read_sounds()
		self.current_vc = None

	def read_sounds(self):
		path = self.bot.cvars["SNDS_PATH"]
		all_sounds = {}
		categories = [f.name for f in os.scandir(path) if f.is_dir()]
		for cat in categories:
			all_sounds[cat] = [f.name for f in os.scandir(os.path.join(path, cat))]
		return all_sounds

	def sound_path(self, category, soundfile):
		return os.path.join(self.bot.cvars["SNDS_PATH"], category, soundfile)

	async def play_file(self, vc, file):
		await asyncio.sleep(.5)
		vc.play(discord.FFmpegPCMAudio(executable=self.bot.cvars["FFMPEG_PATH"], source=file))

	def get_random_sound(self):
		categ = random.choice(list(self.sounds.keys()))
		sound = random.choice(self.sounds[categ])
		module_logger.debug(f'getting {categ}.{sound}')
		return self.sound_path(categ, sound)

	def get_random_active_vc(self):
		guild = self.bot.guilds[0]
		active_vcs = [c for c in guild.channels if c.type == discord.ChannelType.voice and len(c.members) > 0]
		if len(active_vcs) > 0:
			return random.choice(active_vcs)
		else:
			return None

	def in_vc(self):
		return self.current_vc is not None and self.current_vc.is_connected()

	async def get_or_connect_vc(self, ctx):
		vc = None
		if self.in_vc():
			vc = self.current_vc
		else:
			vc = await ctx.author.voice.channel.connect()
			self.current_vc = vc
		return vc

	@commands.command(name='sr', hidden=True)
	@commands.is_owner()
	async def reload_sounds(self, ctx):
		self.sounds = self.read_sounds_list()

	@commands.command(name='summon')
	async def summon(self, ctx):
		voice_channel = ctx.author.voice.channel
		if voice_channel is not None:
			if self.in_vc():
				await self.current_vc.disconnect()
				vc = await voice_channel.connect()
				self.current_vc = vc
			else:
				vc = await voice_channel.connect()
				self.current_vc = vc
		else:
			await ctx.send(str(ctx.author.name) + "is not in a channel.")
		await ctx.message.delete()

	def find_sound_by_name(self, name):
		file = None
		r = [(z, self.sounds[z].index(name)) for z in list(self.sounds.keys()) if name in self.sounds[z]]
		if len(r) > 0:
			cat = r[0][0]
			s_idx = r[0][1]
			f_name = self.sounds[cat][s_idx]
			file = self.sound_path(cat, f_name)
		return file

	@commands.command(name='sound')
	async def x(self, ctx, *args):
		file = None
		async with ctx.typing():
			vc = await self.get_or_connect_vc(ctx)
			await ctx.message.delete()
			await asyncio.sleep(.5)

		if len(args) == 0:
			file = self.get_random_sound()
		else:
			f_key = " ".join(args)
			file = self.find_sound_by_name(f_key)

		if file is not None:
			self.logger.debug(f'playing {os.path.basename(file)}')
			await self.play_file(vc, file)
		else:
			await ctx.send("mi")

	@commands.command(name='listsounds')
	async def listsnds(self, ctx):
		snds = ""
		for key in list(self.sounds.keys()):
			snds += f'{key}:\n\t{", ".join(self.sounds[key])}\n'
		await ctx.send(f'```yml\n{snds}```')

	@staticmethod
	def format_embed_sounds(slice, page):

		embed = discord.Embed(title="valasz vmit", description=f"{page + 1}. oldal", color=0xed0707)
		for i in range(len(slice)):
			embed.add_field(name=f"{i}.", value=slice[i], inline=True)
		embed.set_footer(text="all rights to artsits 2020 @ kTJ")

		return embed

	@commands.command(name="select", hidden=True)
	async def select(self, ctx):
		# TODO: make paginator generic
		self.logger.debug('sound selecta')

		page_size = 10
		page = 0

		act_slice = list(self.sounds.keys())[page * page_size:page * page_size + page_size]
		msg = await ctx.channel.send(embed=self.format_embed_sounds(act_slice, page))
		await ctx.message.delete()

		n_emojis = [
			"\u0030", "\u0031", "\u0032", "\u0033", "\u0034",  # 0-4
			"\u0035", "\u0036", "\u0037", "\u0038", "\u0039",  # 5-9
			"\u25C0", "\u25B6"  # left - right
		]

		for r in n_emojis[:10]:
			await msg.add_reaction(r + "\u20E3")  # 0-9 + squares
		for r in n_emojis[10:]:
			await msg.add_reaction(r)

		def check(reaction_obj, usr):
			return reaction_obj.message.id == msg.id and \
				   usr.id != msg.author.id and \
				   usr.id == ctx.message.author.id

		selection = -1
		while selection == -1:
			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)

				if reaction.emoji in ["◀", "▶"]:
					self.logger.info(f'switching page {reaction.emoji}')
					page = page + 1
					act_slice = list(self.sounds.keys())[page * page_size:page * page_size + page_size]
					await msg.edit(embed=self.format_embed_sounds(act_slice, page))
				else:
					try:
						remoji_num = reaction.emoji[:-1]
						selectable_nums = n_emojis[:10]
						if remoji_num in selectable_nums:
							selection = selectable_nums.index(remoji_num)
					except TypeError as ex:
						await ctx.send(f'te hülye vagy gec {user.mention}')
			except asyncio.TimeoutError:
				self.logger.debug("selection timed out")
				selection = -2
			except Exception as e:
				self.logger.error(e, exc_info=True)
				selection = -2
		if selection > 0:
			self.logger.debug(f'selected: {selection}. -> {act_slice[selection]}')
		await msg.delete()


def setup(bot):
	bot.add_cog(SoundBoardCog(bot))
