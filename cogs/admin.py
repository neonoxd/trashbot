import asyncio
import json
import logging
import time
import random
import os

import aiohttp
import discord
from discord import Member
from discord.ext import commands

from utils.helpers import get_resource_name_or_user_override

module_logger = logging.getLogger('trashbot.AdminCog')

editor_url = os.getenv("EDITOR_API_URL")
editor_allowlist_config = os.getenv("EDITOR_ALLOWLIST_CFG")


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


class EditorFileSelect(discord.ui.Select):
    def __init__(self):
        self.logger = module_logger
        with open(editor_allowlist_config, "r") as f:
            allowlist_config = json.loads(f.read())
            options = [
                discord.SelectOption(label=cfg_k, emoji="📜", description=allowlist_config[cfg_k])
                for cfg_k in list(allowlist_config.keys())
            ]
            super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        url = f'{editor_url}/request/{self.values[0]}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    resp = await r.read()
                    await interaction.response.send_message(content=resp.decode(), ephemeral=True)
                else:
                    self.logger.warning(f"resp {r}")


class EditorFileSelectView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(EditorFileSelect())


@command_list_aware
class AdminCog(commands.Cog):
    def __init__(self, bot):
        module_logger.info("initializing AdminCog")
        self.bot = bot
        self.logger = module_logger

    @commands.command(name="edit", hidden=True)
    async def edit(self, ctx):
        await ctx.message.delete()
        await ctx.send("Editable files:", view=EditorFileSelectView())

    @commands.command(name="info", hidden=True)
    async def dump_info(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(title="Van itt minden", description="ez meg az")
        embed.set_author(name="Kovács Tibor József", url="https://www.facebook.com/tibikevok.jelolj/",
                         icon_url="https://cdn.discordapp.com/attachments/248727639127359490/913774079423684618/422971_115646341961102_1718197155_n.jpg")

        dump = self.bot.globals.verinfo
        for key in list(dump.keys()):
            embed.add_field(name=key, value=dump[key], inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Get the bot's current websocket and API latency."""
        start_time = time.time()
        message = await ctx.send("Testing Ping...")
        end_time = time.time()

        await message.edit(
            content=f"Pong! {round(self.bot.latency * 1000)}ms\nAPI: {round((end_time - start_time) * 1000)}ms")

    @commands.command(name='clear', hidden=True)
    async def clear(self, ctx, user: Member):
        state = ctx.bot.state.get_guild_state_by_id(ctx.guild.id)
        state.clear_nick(user)
        await user.edit(nick=None)

    @commands.command(name='rr', hidden=True)
    async def reload_resources(self, ctx):
        with open(get_resource_name_or_user_override("lists/slur.list"), 'r', encoding="utf8") as file:
            ctx.bot.globals.slurs = file.readlines()

        with open(get_resource_name_or_user_override("lists/status.list"), 'r', encoding="utf8") as file:
            ctx.bot.globals.statuses = file.readlines()

        await ctx.bot.change_presence(activity=discord.Game(
            random.choice(ctx.bot.globals.statuses)
        ))

    @commands.command(name='rs', hidden=True)
    async def roll_status(self, ctx):
        await ctx.bot.change_presence(activity=discord.Game(
            random.choice(ctx.bot.globals.statuses)
        ))

    @commands.command(name='set', hidden=True)
    @commands.is_owner()
    async def setter_command(self, ctx, *args):
        try:
            module_logger.debug(f"set command invoked with args: {args}")
            command = args[0]
            params = args[1:]
            await ctx.message.delete()
            await self.setter_commands[command](self, ctx, *params)
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
        self.bot.globals.ph_token = args

    @set_command(name='nick')
    async def cmd_set_nick(self, ctx, member, *nick):
        converter = commands.MemberConverter()
        _member = await converter.convert(ctx, member)
        module_logger.debug(f"cmd_set_nick called with args {member} {nick}")
        module_logger.debug(f"{_member.id}")
        state = ctx.bot.state.get_guild_state_by_id(ctx.guild.id)
        _nick = " ".join(nick)
        await _member.edit(nick=_nick)
        state.force_nick(_member, _nick, ctx.author)
        ctx.bot.loop.create_task(self.autoclear_task(ctx, _member))

    @set_command(name='tension')
    async def cmd_set_tension(self, ctx, *args):
        module_logger.debug(f"cmd_set_tension called with args {args}")
        try:
            new_tension = int(args[0])
            from cogs.impl.shitpost import set_daily_tension
            await set_daily_tension(self.bot, new_tension)
        except Exception as e:
            module_logger.error("something went wrong")
            module_logger.error(e, exc_info=True)

    @staticmethod
    async def autoclear_task(ctx, member: Member):
        module_logger.debug(f"queued nick autoclear task for member in 60 mins {member}")
        await asyncio.sleep(60 * 60)
        state = ctx.bot.state.get_guild_state_by_id(ctx.guild.id)
        state.clear_nick(member)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
