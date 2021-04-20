import logging
import time

from discord.ext import commands

module_logger = logging.getLogger('trashbot.AdminCog')


def command_list_aware(cls):
    """class decorator to collect set-command methods"""
    cls.setter_commands = {}
    for name, method in cls.__dict__.items():
        if hasattr(method, "is_set_command"):
            cls.setter_commands[method.command_name] = method
            module_logger.debug(f"found set-command method [{method.command_name}] - {name}")
    return cls


def set_command(name=None):
    """decorator to mark set-command methods"""
    def inner(func):
        func.is_set_command = True
        func.command_name = name
        return func

    return inner


@command_list_aware
class AdminCog(commands.Cog):
    def __init__(self, bot):
        module_logger.info("initializing AdminCog")
        self.bot = bot
        self.logger = module_logger

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Get the bot's current websocket and API latency."""
        start_time = time.time()
        message = await ctx.send("Testing Ping...")
        end_time = time.time()

        await message.edit(
            content=f"Pong! {round(self.bot.latency * 1000)}ms\nAPI: {round((end_time - start_time) * 1000)}ms")

    @commands.command(name='set', hidden=True)
    @commands.is_owner()
    async def setter_command(self, ctx, *args):
        try:
            module_logger.debug(f"set command invoked with args: {args}")
            command = args[0]
            params = args[1:]
            await ctx.message.delete()
            await self.setter_commands[command](self, ctx, params)
        except IndexError:
            module_logger.error("command argument missing")
        except KeyError:
            module_logger.error(f"no such command: {args[0]}")
        except Exception as e:
            module_logger.error(f"failed to invoke command")
            module_logger.error(e, exc_info=True)

    @set_command(name='phtoken')
    async def cmd_set_ph_token(self, ctx, args):
        module_logger.debug(f"cmd_set_ph_token called with args {args}")
        self.bot.globals.ph_token = args[0]

    @set_command(name='tension')
    async def cmd_set_tension(self, ctx, args):
        module_logger.debug(f"cmd_set_tension called with args {args}")
        try:
            new_tension = int(args[0])
            from cogs.shitpost import set_daily_tension
            await set_daily_tension(self.bot, new_tension)
        except Exception as e:
            module_logger.error("something went wrong")
            module_logger.error(e, exc_info=True)


def setup(bot):
    bot.add_cog(AdminCog(bot))
