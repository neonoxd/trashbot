import logging
import random

from discord.ext import commands

module_logger = logging.getLogger('trashbot.RandomsCog')


class RandomsCog(commands.Cog):
	def __init__(self, bot):
		module_logger.info("initializing RandomsCog")
		self.bot = bot
		self.logger = module_logger

	@commands.command(name='vandam')
	async def vandam(self,ctx, *args):
		from cogs.impl.shitpost import mercy_maybe
		self.logger.info("command called: {}".format(ctx.command))
		if len(args) > 0:
			await mercy_maybe(self.bot, ctx.channel, int(args[0]))
		else:
			await mercy_maybe(self.bot, ctx.channel)

	@commands.command(name='roll', aliases=['gurit'])
	async def roll_cmd(self, ctx, *args):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.send(roll(args))

	@commands.command(name='arena')
	async def fight(self,ctx, *args):
		self.logger.info("command called: {}".format(ctx.command))
		if len(args) == 0:
			return
		await ctx.send("a ketrec harc gyöz tese: {}".format(random.choice(args)))


def roll(args):
	if len(args) == 1:
		return random.randrange(0, int(args[0]))
	elif len(args) == 2:
		return random.randrange(int(args[0]), int(args[1]))
	else:
		return random.randrange(0, 100)


def setup(bot):
	bot.add_cog(RandomsCog(bot))
