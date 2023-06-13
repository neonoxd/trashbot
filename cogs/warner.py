import asyncio
import json
import logging
import os.path
import random
from datetime import datetime
from io import BytesIO
from typing import Literal, Optional

import discord.utils
from discord import app_commands
from discord.ext import commands
from tabulate import tabulate

from utils.helpers import find_member_by_id
from utils.state import TrashBot

module_logger = logging.getLogger('trashbot.WarnerCog')
warnpath = "usr/warns.json"


def read_warns():
    if not os.path.isfile(warnpath):
        with open(warnpath, "w", encoding="utf8") as f:
            f.write("{}")
            return {}
    else:
        with open(warnpath, "r", encoding="utf8") as f:
            return json.loads(f.read())


class WarnerCog(commands.Cog):
    def __init__(self, bot: TrashBot):
        self.bot = bot
        self.logger = module_logger
        module_logger.info(f"initializing {self.__cog_name__}")
        self.warns = read_warns()

    @app_commands.command(name="warn")
    @app_commands.describe(member='a tag, a báttya, az ipse akit felnyomsz', reason="a vádirat miszerint")
    @app_commands.rename(member="ipse", reason="vád")
    async def warn_command(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """ nyomj fel valakit """
        module_logger.info(f"selected: {member}")
        async with interaction.channel.typing():
            module_logger.debug(f"{interaction.user} warns {member} for {reason}")
            if len(reason) > 150:
                await interaction.response.send_message(content="ennyit nem tok megjegyezni báttya")
            else:
                try:
                    msg = await self.do_save_warn(str(interaction.user.id), str(member.id), reason)
                    await interaction.response.send_message(content=msg)
                except Exception as e:
                    module_logger.error(e)
                    await interaction.response.send_message(content="vmi nem jo gyerekeg", ephemeral=True, delete_after=5)
        raise Exception("xd")

    @app_commands.command(name="warn-cfg")
    @commands.is_owner()
    async def warn_config(self, interaction: discord.Interaction, action: Literal['reload-warns']):
        if action == 'reload-warns':
            self.warns = read_warns()
            await interaction.response.send_message(content="újratöltve", ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message(content="miva", ephemeral=True, delete_after=5)

    @app_commands.command(name="warns-all")
    @app_commands.describe(dump='csévében-e')
    async def list_warns_all(self, interaction: discord.Interaction, dump: Optional[bool] = False):
        module_logger.debug("getting all warns")
        await interaction.response.defer(thinking=True)
        ids = list(self.warns.keys())
        all_warns = []
        for warned_id in ids:
            usr_warns = self.warns[warned_id]
            edited_warns = [
                                [
                                    find_member_by_id(interaction.guild, warn[0]),
                                    *warn[1:],
                                    find_member_by_id(interaction.guild, warned_id)
                                ]
                                for warn in usr_warns
                            ]
            all_warns += edited_warns
        all_warns = sorted(all_warns, key=lambda x: x[2])
        warn_string = self.format_warns_all(all_warns, dump)
        if dump:
            await interaction.followup.send("iesmik", file=discord.File(BytesIO(warn_string.encode()), "warns.csv"))
        else:
            warns = self.split_warns(warn_string)
            if warns == "nicse":
                await interaction.followup.send_message(warns)
            else:
                await interaction.followup.send(f"hát iga h:\n```{warns[0]}```")

                for warn in warns[1:]:
                    await asyncio.sleep(1)
                    await interaction.followup.send(f"még\n```{warn}```")

    @app_commands.command(name="warns")
    async def list_warns(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        victim = member or interaction.user
        guild = interaction.guild
        member_id_str = str(victim.id)
        warns = "nicse"
        
        if member_id_str in self.warns:
            module_logger.debug(f"getting warns for {member_id_str}")
            all_warns = sorted(self.warns[member_id_str], key=lambda x: x[2])
            warn_string = self.format_warns(guild, all_warns)
            warns = self.split_warns(warn_string)
            
        if warns == "nicse":
            await interaction.response.send_message(warns)
        else:
            await interaction.response.defer(thinking=True)
            await interaction.followup.send(f"hát {victim.mention} ilyenekbe van h:\n```{warns[0]}```")

            for warn in warns[1:]:
                await asyncio.sleep(1)
                await interaction.followup.send(f"s még\n```{warn}```")

    @staticmethod
    def format_warns(guild, warns):
        headers = ["KI", "MIKO", "MER"]
        data = [[find_member_by_id(guild, warn[0]), datetime.fromtimestamp(warn[2]).strftime('%Y-%m-%d %H:%M:%S'), warn[1]] for warn in warns]
        tabbed = tabulate(data, headers=headers, showindex=True)
        return tabbed

    @staticmethod
    def format_warns_all(warns, dump):
        headers = ["KI", "KIT", "MIKO", "MER"]
        data = []

        for warn in warns:
            data.append(
                [warn[0], warn[3], datetime.fromtimestamp(warn[2]).strftime('%Y-%m-%d %H:%M:%S'), warn[1]]
            )

        if dump:
            module_logger.debug("dumping as file warns")
            out = ";\t".join(headers)+"\n"
            for warnline in data:
                out += ";\t".join([str(warnparam) for warnparam in warnline])+"\n"
            return out
        else:
            tabbed = tabulate(data, headers=headers, showindex=True)
            return tabbed

    @staticmethod
    def split_warns(tabbed):
        splitted = tabbed.split("\n")
        msgs = []
        out = ""
        for line in splitted:
            temp = out + line + "\n"
            if len(temp) > 2000:
                msgs.append(out)
                out = splitted[0] + "\n" + splitted[1] + "\n"
                out += line + "\n"
            else:
                out = temp

        if out != splitted[0] + "\n" + splitted[1] + "\n":
            msgs.append(out)
        return msgs

    async def do_save_warn(self, id: str, warned_id: str, reason: str):
        module_logger.info(f"doing warn: {id} {warned_id}, {reason}")
        warn = [id, reason, datetime.now().timestamp()]
        if warned_id in self.warns:
            self.warns[warned_id].append(warn)
        else:
            self.warns[warned_id] = [warn]
        with open(warnpath, "w", encoding="utf8") as f:
            f.write(json.dumps(self.warns, indent=4, ensure_ascii=False))
        module_logger.info("saved warn")
        msg = "megjegyeztem 😂"
        if len(self.warns[warned_id]) > 2:
            msg += f" {random.choice(['má sokadik', 'de enyi', 'nem elsö'])} 😂 {len(self.warns[warned_id])}"
        return msg


async def setup(bot: TrashBot):
    await bot.add_cog(WarnerCog(bot))
