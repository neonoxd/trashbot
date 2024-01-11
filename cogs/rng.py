import logging
import random

from discord.ext import commands
from discord.ext.commands import Context

from utils.state import TrashBot

module_logger = logging.getLogger('trashbot.RandomsCog')


class RandomsCog(commands.Cog):
	def __init__(self, bot: TrashBot):
		module_logger.info("initializing RandomsCog")
		self.bot = bot
		self.logger = module_logger

	@commands.command(name='vandam')
	async def vandam(self, ctx: Context, *args):
		from cogs.impl.shitpost_impl import mercy_maybe
		self.logger.info("command called: {}".format(ctx.command))
		if len(args) > 0:
			await mercy_maybe(self.bot, ctx.channel, int(args[0]))
		else:
			await mercy_maybe(self.bot, ctx.channel)

	@commands.command(name='roll', aliases=['gurit'])
	async def roll_cmd(self, ctx: Context, *args):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.send(str(roll(*args)))

	@commands.command(name='arena')
	async def fight(self, ctx: Context, *args):
		self.logger.info("command called: {}".format(ctx.command))
		if len(args) == 0:
			return
		await ctx.send("a ketrec harc gyöz tese: {}".format(random.choice(args)))


def roll(*args) -> int:
	if len(args) == 1:
		return random.randrange(0, int(args[0]))
	elif len(args) == 2:
		return random.randrange(*map(int, args))
	else:
		return random.randrange(0, 100)


async def setup(bot: TrashBot):
	await bot.add_cog(RandomsCog(bot))
