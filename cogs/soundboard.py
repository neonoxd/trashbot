import asyncio
import logging
import os
import random

import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import Context

from utils.state import TrashBot

module_logger = logging.getLogger('trashbot.SoundBoardCog')


class SoundBoardCog(commands.Cog):
	def __init__(self, bot: TrashBot):
		self.bot = bot
		self.logger = module_logger
		module_logger.info("initializing SoundBoardCog")
		self.sounds = self.read_sounds()
		self.current_vc = None

	def read_sounds(self):
		path = self.bot.globals.sounds_path
		if not os.path.exists(path):
			return {}
		all_sounds = {}
		categories = [f.name for f in os.scandir(path) if f.is_dir()]
		for cat in categories:
			all_sounds[cat] = [f.name for f in os.scandir(os.path.join(path, cat))]
		return all_sounds

	def sound_path(self, category, soundfile):
		return os.path.join(self.bot.globals.sounds_path, category, soundfile)

	async def play_file(self, vc, file):
		await asyncio.sleep(.5)
		vc.play(discord.FFmpegPCMAudio(executable=self.bot.globals.ffmpeg_path, source=file))

	def find_sound_by_name(self, name):
		file = None
		sounds = self.sounds
		found_sounds = []

		for category in list(sounds.keys()):
			for idx, sound in enumerate(sounds[category]):
				if name == sound or name == os.path.splitext(sound)[0]:
					found_sounds.append((category, idx))

		if len(found_sounds) > 0:
			cat = found_sounds[0][0]
			s_idx = found_sounds[0][1]
			f_name = self.sounds[cat][s_idx]
			file = self.sound_path(cat, f_name)
		return file

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

	async def get_or_connect_vc(self, ctx: Context):
		if self.in_vc():
			vc = self.current_vc
		else:
			vc = await ctx.author.voice.channel.connect()
			self.current_vc = vc
		return vc

	@commands.command(name='reloadsounds')
	async def reload(self, ctx: Context):
		module_logger.debug("reloading sounds")
		self.sounds = self.read_sounds()

	@commands.command(name='summon')
	async def summon(self, ctx: Context):
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

	async def play_source_if_vc(self, source, delay):
		if self.in_vc():
			vc = self.current_vc
			await asyncio.sleep(delay)
			vc.play(discord.FFmpegPCMAudio(executable=self.bot.globals.ffmpeg_path, source=source))

	@commands.Cog.listener()
	async def on_voice_state_update(self, member: Member, before, after):

		join_map = {
			self.bot.globals.goofies["sz"]: f"resources/sounds/door{random.randrange(1,4)}.ogg",
			self.bot.globals.goofies["d"]: f"resources/sounds/join_hola.wav",
			self.bot.globals.goofies["ps"]: f"resources/sounds/pspsps.mp3",
			self.bot.globals.goofies["m"]: f"resources/sounds/DUKNUK14.ogg",
			self.bot.globals.goofies["denik"]: f"resources/sounds/ittvokgec.ogg"
		}

		exit_map = {
			self.bot.globals.goofies["d"]: f"resources/sounds/out_chau.wav"
		}

		if before.channel is None and after.channel is not None:  # user connected
			if member.id in join_map:
				await self.play_source_if_vc(join_map[member.id], .5)

		if before.channel is not None and after.channel is None:  # user disconnected
			if member.id in exit_map:
				await self.play_source_if_vc(exit_map[member.id], .5)

	@commands.command(name='sound')
	async def play_sound(self, ctx: Context, *args):
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
	async def list_sounds(self, ctx: Context):
		snds = ""
		for key in list(self.sounds.keys()):
			snds += f'{key}:\n\t{", ".join([os.path.splitext(snd)[0] for snd in self.sounds[key]])}\n'
		await ctx.send(f'```yml\n{snds}```')

	@staticmethod
	def format_embed_sounds(sounds_slice, page):
		embed = discord.Embed(title="valasz vmit", description=f"{page + 1}. oldal", color=0xed0707)
		for i in range(len(sounds_slice)):
			embed.add_field(name=f"{i}.", value=sounds_slice[i])
		embed.set_footer(text="all right to artsits 2022 @ kTJ")

		return embed

	@commands.command(name="select", hidden=True)
	async def select(self, ctx: Context, *args):
		# TODO: make paginator generic, fix reading new sound list format
		self.logger.debug('sound selecta')

		chosen_category = args[0] if len(args) > 0 else random.choice(list(self.sounds.keys()))

		page_size = 10
		page = 0

		act_slice = list(self.sounds[chosen_category])[page * page_size:page * page_size + page_size]
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
					page = page + 1 if reaction.emoji == "▶" else page - 1
					act_slice = list(self.sounds[chosen_category])[page * page_size:page * page_size + page_size]
					await msg.edit(embed=self.format_embed_sounds(act_slice, page))
				else:
					try:
						remoji_num = reaction.emoji[:-1]
						selectable_nums = n_emojis[:10]
						if remoji_num in selectable_nums:
							selection = selectable_nums.index(str(remoji_num))
					except TypeError as ex:
						await ctx.send(f'te hülye vagy gec {user.mention}')
			except asyncio.TimeoutError:
				self.logger.debug("selection timed out")
				selection = -2
			except Exception as e:
				self.logger.error(e, exc_info=True)
				selection = -2
		if selection >= 0:
			self.logger.debug(f'selected: {selection}. -> {act_slice[selection]}')
			vc = await self.get_or_connect_vc(ctx)
			file = self.sound_path(chosen_category, act_slice[selection])
			await self.play_file(vc, file)

		await msg.delete()


async def setup(bot: TrashBot):
	await bot.add_cog(SoundBoardCog(bot))
