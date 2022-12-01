import asyncio
import logging

import discord
from discord import Message, Member
from discord.ext import commands
from discord.ext.commands import Context, Bot

module_logger = logging.getLogger('trashbot.Shitpost')


class ShitpostCog(commands.Cog):
	def __init__(self, bot: Bot):
		module_logger.info("initializing Shitpost")
		self.bot = bot
		self.logger = module_logger
		with open('resources/beemovie.txt', 'r', encoding="utf8") as file:
			self.beescript = file.read().split("\n\n  \n")

	@commands.command(name='befli', hidden=True)
	async def befli(self, ctx: Context):
		from cogs.impl.shitpost import command_befli
		await command_befli(self, ctx)

	@commands.command(name='friday', hidden=True)
	async def friday(self, ctx: Context):
		from cogs.impl.shitpost import announce_friday_mfs
		await ctx.message.delete()
		await announce_friday_mfs(self.bot)

	@commands.command(name='captcha')
	async def captcha(self, ctx: Context):
		from cogs.impl.shitpost import command_captcha
		await command_captcha(self, ctx)

	@commands.command(name='tenemos')
	async def tenemos(self, ctx: Context):
		from cogs.impl.shitpost import command_tenemos
		await command_tenemos(self, ctx)

	@commands.command(name="gabo")
	async def gabo(self, ctx: Context, *args):
		from cogs.impl.shitpost import command_gabo
		await command_gabo(self, ctx, args)

	@commands.command(name="sanity")
	async def szabo(self, ctx: Context):
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

	@commands.command(name='beemovie')
	async def bmc(self, ctx: Context, *args):
		from cogs.impl.shitpost import command_beemovie
		await command_beemovie(self, ctx, args)

	@commands.command(name='tension')
	async def show_tension(self, ctx: Context):
		from cogs.impl.shitpost import command_tension
		await command_tension(self, ctx)

	@commands.command(name='gba')
	async def gba(self, ctx: Context):
		from cogs.impl.shitpost import command_gba
		await command_gba(self, ctx)

	@commands.command(name='cz')
	async def cege(self, ctx: Context):
		from cogs.impl.shitpost import command_cz
		await command_cz(self, ctx)

	@commands.Cog.listener()
	async def on_voice_state_update(self, member: Member, before, after):
		from cogs.impl.shitpost import event_voice_state_update
		await event_voice_state_update(self, member, before, after)

	@commands.Cog.listener()
	async def on_message(self, message: Message):
		from cogs.impl.shitpost import event_message
		await event_message(self, message)


async def setup(bot: Bot):
	await bot.add_cog(ShitpostCog(bot))
