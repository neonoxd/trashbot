import asyncio
import json
import logging
import os
import random
import time
import subprocess
from typing import Optional, Literal

import aiohttp
import discord
from discord import Member, app_commands
from discord.ext import commands
from discord.ext.commands import Context, Greedy

from utils.helpers import get_resource_name_or_user_override
from utils.state import TrashBot

from cogs.warner import WarnerCog

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
    def __init__(self, author):
        self.logger = module_logger
        self.author = author
        with open(editor_allowlist_config, "r") as f:
            allowlist_config = json.loads(f.read())
            options = [
                discord.SelectOption(label=cfg_k, emoji="📜", description=allowlist_config[cfg_k])
                for cfg_k in list(allowlist_config.keys())
            ]
            super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.author:
            url = f'{editor_url}/request/{self.values[0]}'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    if r.status == 200:
                        resp = await r.read()
                        await interaction.response.edit_message(content=None, view=SimpleView(discord.ui.Button(label="Open Editor Site", url=resp.decode())))
                    else:
                        self.logger.warning(f"resp {r}")
        else:
            pass


class SimpleView(discord.ui.View):
    def __init__(self, *items, timeout=180):
        super().__init__(timeout=timeout)
        for item in items:
            self.add_item(item)


@command_list_aware
class AdminCog(commands.Cog):
    def __init__(self, bot: TrashBot):
        module_logger.info("initializing AdminCog")
        self.bot = bot
        self.logger = module_logger

    @commands.command(name="sync", hidden=True)
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        """
            do bist stollen
            synchronizes slash commands with server
        """
        await ctx.message.delete()
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            self.logger.debug(f"synced: {len(synced)} commands")
            self.logger.debug("\n".join([str((cmd.name, cmd.type)) for cmd in synced]))

            await ctx.send(
                f"{len(synced)} trükköt tud a báttya{'!' if spec is None else '!?'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"tanit a báttya {ret}/{len(guilds)}.")

    @app_commands.command(name="edit-usercontent")
    async def edit(self, interaction: discord.Interaction):
        """ /edit-usercontent """
        await interaction.response.send_message("Editable files:", view=SimpleView(EditorFileSelect(interaction.user)), ephemeral=True)

    @app_commands.command(name="add-usercontent")
    async def addusercontent(self, interaction: discord.Interaction) -> None:
        """ /add-usercontent """
        url = f'{editor_url}/request_upload'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    resp = await r.read()
                    await interaction.response.send_message(content=resp.decode(), ephemeral=True)
                else:
                    self.logger.warning(f"resp {r}")

    @commands.is_owner()
    @app_commands.command(name="reload")
    async def reload_cfg(self, interaction: discord.Interaction, action: Literal['warns', 'goofies']) -> None:
        bot = self.bot
        if action == 'warns':
            cog: Optional[WarnerCog] = bot.get_cog('WarnerCog')
            cog.warns = cog.read_warns()
            await interaction.response.send_message(content="újratöltve", ephemeral=True, delete_after=5)
        elif action == 'goofies':
            with open(get_resource_name_or_user_override("config/goofies.json"), 'r', encoding="utf8") as file:
                bot.globals.goofies = json.loads(file.read())
                for b_key in list(bot.globals.goofies.keys()):
                    bot.globals.goofies[b_key] = int(bot.globals.goofies[b_key])
        else:
            await interaction.response.send_message(content="miva", ephemeral=True, delete_after=5)

    @commands.command(name="info", hidden=True)
    async def dump_info(self, ctx: commands.Context):
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
    async def clear(self, ctx: commands.Context, user: Member):
        state = ctx.bot.state.get_guild_state_by_id(ctx.guild.id)
        state.clear_nick(user)
        await user.edit(nick=None)

    @commands.command(name='rr', hidden=True)
    async def reload_resources(self, ctx: commands.Context):
        with open(get_resource_name_or_user_override("lists/slur.list"), 'r', encoding="utf8") as file:
            ctx.bot.globals.slurs = file.readlines()

        with open(get_resource_name_or_user_override("lists/status.list"), 'r', encoding="utf8") as file:
            ctx.bot.globals.statuses = file.readlines()

        await ctx.bot.change_presence(activity=discord.Game(
            random.choice(ctx.bot.globals.statuses)
        ))

    @commands.command(name='rs', hidden=True)
    async def roll_status(self, ctx: commands.Context):
        await ctx.bot.change_presence(activity=discord.Game(
            random.choice(ctx.bot.globals.statuses)
        ))
        
    @commands.command(name='update', hidden=True)
    @commands.is_owner()
    async def update(self, ctx: commands.Context):
        await ctx.message.delete()
        subprocess.Popen(["./update.sh"]) 

    @commands.command(name='set', hidden=True)
    @commands.is_owner()
    async def setter_command(self, ctx: commands.Context, *args):
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
    async def cmd_set_ph_token(self, ctx: commands.Context, args):
        module_logger.debug(f"cmd_set_ph_token called with args {args}")
        self.bot.globals.ph_token = args

    @set_command(name='nick')
    async def cmd_set_nick(self, ctx: commands.Context, member, *nick):
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
    async def cmd_set_tension(self, ctx: commands.Context, *args):
        module_logger.debug(f"cmd_set_tension called with args {args}")
        try:
            new_tension = int(args[0])
            from cogs.impl.shitpost_impl import set_daily_tension
            await set_daily_tension(self.bot, new_tension)
        except Exception as e:
            module_logger.error("something went wrong")
            module_logger.error(e, exc_info=True)

    @staticmethod
    async def autoclear_task(ctx: commands.Context, member: Member):
        module_logger.debug(f"queued nick autoclear task for member in 60 mins {member}")
        await asyncio.sleep(60 * 60)
        state = ctx.bot.state.get_guild_state_by_id(ctx.guild.id)
        state.clear_nick(member)


async def setup(bot: TrashBot):
    await bot.add_cog(AdminCog(bot))
