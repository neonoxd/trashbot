import asyncio
import logging
import random

import discord
from discord.ext import commands

module_logger = logging.getLogger('trashbot.SoundBoardCog')


class SoundBoardCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.logger = module_logger
		self.sounds = self.read_sounds_list()

	def read_sounds_list(self):
		import os
		sounds = []
		path = self.bot.cvars["SNDS_PATH"]
		root_dirname = os.path.basename(path)

		print(f'sounds path: {path} \n rootdirname: {root_dirname}')

		for root, subdirs, files in os.walk(self.bot.cvars["SNDS_PATH"]):
			for file in files:
				sounds.append(os.path.join(root, file))
		all = {os.path.basename(k) : k for k in sounds }
		print(all)
		return all

	async def dl_sounds(self):
		pass

	async def playaudio(self, channel, file):
		vc = await channel.connect()
		await asyncio.sleep(.5)
		vc.play(discord.FFmpegPCMAudio(executable=self.bot.cvars["FFMPEG_PATH"], source=file))
		while vc.is_playing():
			await asyncio.sleep(.1)
		await vc.disconnect()

	def get_random_sound(self):
		return self.sounds[random.choice(list(self.sounds.keys()))]

	def get_random_vc(self):
		guild = self.bot.guilds[0]
		active_vcs = [c for c in guild.channels if c.type == discord.ChannelType.voice and len(c.members) > 0]
		if len(active_vcs) > 0:
			return random.choice(active_vcs)
		else:
			return None

	@commands.command(name='p')
	async def x(self, ctx):
		vc = self.get_random_vc()
		await self.playaudio(vc, self.get_random_sound())

	@commands.command(name="play")
	async def play(self, ctx):
		voice_channel = ctx.author.voice.channel
		channel = None
		if voice_channel != None:
			channel = voice_channel.name
			vc = await voice_channel.connect()
			await asyncio.sleep(.5)
			vc.play(discord.FFmpegPCMAudio(executable=self.bot.cvars["FFMPEG_PATH"],
										   source=self.sounds['lerepulatgomb.wav']))
			# Sleep while audio is playing.
			while vc.is_playing():
				await asyncio.sleep(.1)
			await vc.disconnect()
		else:
			await ctx.send(str(ctx.author.name) + "is not in a channel.")
		await ctx.message.delete()


def setup(bot):
	bot.add_cog(SoundBoardCog(bot))
