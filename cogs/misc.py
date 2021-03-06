import logging

import aiohttp
from discord.ext import commands

module_logger = logging.getLogger('trashbot.MiscCog')


class MiscCog(commands.Cog):
	def __init__(self, bot):
		module_logger.info("initializing MiscCog")
		self.bot = bot
		self.logger = module_logger

	@commands.command(name='say')
	async def say(self, ctx, *args):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.message.delete()
		await ctx.send(' '.join(args))

	@commands.command(name='impostor', hidden=True)
	async def impost(self, ctx, *args):
		await ctx.message.delete()
		if len(args) > 0:
			tmpl = f""".      　。　　　　•　    　ﾟ　　。
	　　.　　　.　　　  　　.　　　　　。　　   。　.
	 　.　　      。　        ඞ   。　    .    •
	   •        {args[0]} was the impostor.　 。　.
	　 　　。　　 　　　　ﾟ　　　.　    　　　.
	,　　　　.　 .　　       ."""
			await ctx.send(tmpl)

	@commands.command(name="kot")
	async def say(self, ctx):
		async with aiohttp.ClientSession() as session:
			async with session.get('http://aws.random.cat/meow') as r:
				if r.status == 200:
					js = await r.json()
					await ctx.send(js['file'])


def setup(bot):
	bot.add_cog(MiscCog(bot))
