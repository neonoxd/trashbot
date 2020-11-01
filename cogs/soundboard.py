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
		self.sounds = self.read_sounds_list()
		self.current_vc = None


	def read_sounds_list(self):
		sounds = []
		path = self.bot.cvars["SNDS_PATH"]
		root_dirname = os.path.basename(path)
		for root, subdirs, files in os.walk(self.bot.cvars["SNDS_PATH"]):
			for file in files:
				sounds.append(os.path.join(root, file))
		return {os.path.basename(k): k for k in sounds}

	async def dl_sounds(self):
		pass

	async def play_file(self, vc, file):
		await asyncio.sleep(.5)
		vc.play(discord.FFmpegPCMAudio(executable=self.bot.cvars["FFMPEG_PATH"], source=file))

	def get_random_sound(self):
		return self.sounds[random.choice(list(self.sounds.keys()))]

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

	@commands.command(name='play')
	async def x(self, ctx, *args):
		vc = await self.get_or_connect_vc(ctx)
		await asyncio.sleep(.5)
		if len(args) == 0:
			file = self.get_random_sound()
		else:
			filekey = " ".join(args)
			file = self.sounds[filekey]
		self.logger.debug(f'playing {os.path.basename(file)}')
		await self.play_file(vc, file)
		await ctx.message.delete()

	@commands.command(name='listsounds')
	async def listsnds(self, ctx):
		await ctx.send(f'```{list(self.sounds.keys())}```')


def setup(bot):
	bot.add_cog(SoundBoardCog(bot))
