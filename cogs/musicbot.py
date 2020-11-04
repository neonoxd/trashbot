import asyncio
import logging

import discord
import youtube_dl as youtube_dl
from discord.ext import commands
import os

from discord import opus

from pydub import AudioSegment
from os import listdir
import numpy as np
import math


def bass_line_freq(track):
	sample_track = list(track)

	# c-value
	est_mean = np.mean(sample_track)

	# a-value
	est_std = 3 * np.std(sample_track) / (math.sqrt(2))

	bass_factor = int(round((est_std - est_mean) * 0.005))

	return bass_factor


def load_opus_lib():
	if opus.is_loaded():
		return

	try:
		opus._load_default()
		return
	except OSError:
		pass

	raise RuntimeError('Could not load an opus lib.')


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
	'format': 'bestaudio/best',
	'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
	'restrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
	'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
	'options': '-vn'
}
# dotenv.load_dotenv()
ffmpg = os.getenv("FFMPEG_PATH")

module_logger = logging.getLogger('trashbot.MusicBot')


class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)
		self.data = data
		self.title = data.get('title')
		self.url = data.get('url')
		self.link = f'https://www.youtube.com/watch?v={data.get("id")}'

	@classmethod
	async def extract_data(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0]

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0]
			module_logger.debug(f'playin : {data}')

		filename = data['url'] if stream else ytdl.prepare_filename(data)
		print(f'streaming fnam: {filename}')

		return cls(discord.FFmpegPCMAudio(filename, executable=ffmpg, options=["-vn"]), data=data)


class MusicBot(commands.Cog):
	def __init__(self, bot):
		load_opus_lib()
		self.bot = bot
		self.queue = []
		module_logger.info("initializing MusicBot")

	@commands.command()
	async def join(self, ctx, *, channel: discord.VoiceChannel):
		"""Joins a voice channel"""

		if ctx.voice_client is not None:
			return await ctx.voice_client.move_to(channel)

		await channel.connect()

	# @commands.command()
	# async def play(self, ctx, *, query):
	# 	"""Plays a file from the local filesystem"""
	#
	# 	source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
	# 	ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
	#
	# 	await ctx.send('Now playing: {}'.format(query))

	@commands.command()
	async def yt(self, ctx, *, url):
		"""Plays from a url (almost anything youtube_dl supports)"""

		async with ctx.typing():
			player = await YTDLSource.from_url(url, loop=self.bot.loop)
			ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

		await ctx.send(f'akkor nyomom a következőt: {player.title}\n{player.link}')

	@commands.command()
	async def stream(self, ctx, *, url):
		"""Streams from a url (same as yt, but doesn't predownload)"""

		async with ctx.typing():
			player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
			ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

		await ctx.send('Now playing: {}'.format(player.title))

	@commands.command()
	async def volume(self, ctx, volume: int):
		"""Changes the player's volume"""

		if ctx.voice_client is None:
			return await ctx.send("Not connected to a voice channel.")

		ctx.voice_client.source.volume = volume / 100
		await ctx.send("Changed volume to {}%".format(volume))

	@commands.command()
	async def stop(self, ctx):
		"""Stops and disconnects the bot from voice"""

		await ctx.voice_client.disconnect()

	@yt.before_invoke
	@stream.before_invoke
	async def ensure_voice(self, ctx):
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				await ctx.send("You are not connected to a voice channel.")
				raise commands.CommandError("Author not connected to a voice channel.")
		elif ctx.voice_client.is_playing():
			ctx.voice_client.stop()


def setup(bot):
	bot.add_cog(MusicBot(bot))
