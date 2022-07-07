import asyncio
import logging

import discord
from discord.ext import commands

from cogs.impl.shitpost import command_befli, command_captcha, \
	command_tenemos, command_zene, command_beemovie, command_tension, event_voice_state_update, event_message, \
	command_cz, announce_friday_mfs, command_gabo, command_dog, command_gba

module_logger = logging.getLogger('trashbot.Shitpost')


class ShitpostCog(commands.Cog):
	def __init__(self, bot):
		module_logger.info("initializing Shitpost")
		self.bot = bot
		self.logger = module_logger
		with open('resources/lists/best.list', 'r', encoding="utf8") as file:
			self.trek_list = file.read().split("\n\n")
		with open('resources/beemovie.txt', 'r', encoding="utf8") as file:
			self.beescript = file.read().split("\n\n  \n")
		with open('resources/lists/dog.list', 'r', encoding="utf8") as file:
			self.dogeatdogworld = file.read().split("\n\n")

	@commands.command(name='befli', hidden=True)
	async def befli(self, ctx):
		await command_befli(self, ctx)

	@commands.command(name='friday', hidden=True)
	async def friday(self, ctx):
		await ctx.message.delete()
		await announce_friday_mfs(self.bot)

	@commands.command(name='captcha')
	async def captcha(self, ctx):
		await command_captcha(self, ctx)

	@commands.command(name='tenemos')
	async def tenemos(self, ctx):
		await command_tenemos(self, ctx)

	@commands.command(name="gabo")
	async def gabo(self, ctx, *args):
		await command_gabo(self, ctx, args)

	@commands.command(name="sanity")
	async def szabo(self, ctx):
		guild = ctx.bot.guilds[0]
		sz_vc = [
			c for c in guild.channels if c.type == discord.ChannelType.voice
			and len([member for member in c.members if member.id == ctx.bot.globals.sz_id]) > 0
		]
		await ctx.message.delete()
		if len(sz_vc) > 0 and len(sz_vc[0].members) > 5:
			msg = await ctx.channel.send("**sanity check...**")
			await asyncio.sleep(2)
			await msg.edit(content="**sanity check...** ❌")
			await asyncio.sleep(3)
			await ctx.message.channel.send(file=discord.File("resources/img/insanity.webp"), content="good luck :)")
		else:
			msg = await ctx.channel.send("**sanity check...**")
			await asyncio.sleep(2)
			await msg.edit(content="**sanity check...** ✅")

	@commands.command(name='zene')
	async def zene(self, ctx):
		await command_zene(self, ctx)

	@commands.command(aliases=['kutya', 'dogeatdog', 'kiskutya'])
	async def harap(self, ctx):
		await command_dog(self, ctx)

	@commands.command(name='beemovie')
	async def bmc(self, ctx, *args):
		await command_beemovie(self, ctx, args)

	@commands.command(name='tension')
	async def show_tension(self, ctx):
		await command_tension(self, ctx)

	@commands.command(name='gba')
	async def gabo(self, ctx):
		await command_gba(self, ctx)

	@commands.command(name='cz')
	async def cege(self, ctx):
		await command_cz(self, ctx)

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		await event_voice_state_update(self, member, before, after)

	@commands.Cog.listener()
	async def on_message(self, message):
		await event_message(self, message)

# @commands.Cog.listener()
# @commands.guild_only()
# async def on_typing(self, channel, user, when):
#	await event_typing(self, channel, user, when)


def setup(bot):
	bot.add_cog(ShitpostCog(bot))
