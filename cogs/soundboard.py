import asyncio
import datetime
import logging
import os
import random
from typing import List

import discord
from discord import Member, VoiceState, app_commands
from discord.ext import commands
from discord.ext.commands import Context

from utils.helpers import get_resource_name_or_user_override
from utils.state import TrashBot

module_logger = logging.getLogger('trashbot.SoundBoardCog')


class SoundBoardCog(commands.Cog):
    def __init__(self, bot: TrashBot):
        self.bot = bot
        self.logger = module_logger
        module_logger.info("initializing SoundBoardCog")
        self.sounds = self.read_sounds()
        self.current_vc = None
        
    async def sounds_autocomplete(self, interaction: discord.Interaction, current: str) \
        -> List[app_commands.Choice[str]]:
        category = interaction.namespace.category or None
        choices = [os.path.splitext(snd)[0] for snd in self.sounds[category]] if category is not None else []
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]
    
    async def categories_autocomplete(self, i: discord.Interaction, current: str) \
        -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in list(self.sounds.keys()) if current.lower() in choice.lower()
        ]
        
    @app_commands.command(name="sound")
    @app_commands.autocomplete(category=categories_autocomplete, sound_file=sounds_autocomplete)
    @app_commands.describe(category="sound source category")
    async def slash_sound(self, interaction: discord.Interaction, category:str, sound_file:str):
        module_logger.debug(f"playing {sound_file} from {category}")
        vc = await self.get_or_connect_vc(interaction)
        await asyncio.sleep(.5)
        file = self.find_sound_by_name(sound_file)
        if file is not None:
            self.logger.debug(f'playing {os.path.basename(file)}')
            await interaction.response.send_message("nyomom ;)", ephemeral=True, delete_after=1)
            await self.play_file(vc, file)
        else:
            await interaction.response.send_message("mi")

    def read_sounds(self):
        path = self.bot.globals.sounds_path
        if not os.path.exists(path):
            return {}
        all_sounds = {}
        categories = [f.name for f in os.scandir(path) if f.is_dir()]
        for cat in categories:
            all_sounds[cat] = [f.name for f in os.scandir(os.path.join(path, cat))]
        return all_sounds

    def sound_path(self, category, soundfile):
        return os.path.join(self.bot.globals.sounds_path, category, soundfile)

    async def play_file(self, vc, file):
        await asyncio.sleep(.5)
        vc.play(discord.FFmpegPCMAudio(executable=self.bot.globals.ffmpeg_path, source=file))

    def find_sound_by_name(self, name):
        file = None
        sounds = self.sounds
        found_sounds = []

        for category in list(sounds.keys()):
            for idx, sound in enumerate(sounds[category]):
                if name == sound or name == os.path.splitext(sound)[0]:
                    found_sounds.append((category, idx))

        if len(found_sounds) > 0:
            cat = found_sounds[0][0]
            s_idx = found_sounds[0][1]
            f_name = self.sounds[cat][s_idx]
            file = self.sound_path(cat, f_name)
        return file

    def get_random_sound(self):
        categ = random.choice(list(self.sounds.keys()))
        sound = random.choice(self.sounds[categ])
        module_logger.debug(f'getting {categ}.{sound}')
        return self.sound_path(categ, sound)

    def get_random_active_vc(self):
        guild = self.bot.guilds[0]
        active_vcs = [c for c in guild.channels if c.type == discord.ChannelType.voice and len(c.members) > 0]
        if len(active_vcs) > 0:
            return random.choice(active_vcs)
        else:
            return None

    def in_vc(self):
        return self.current_vc is not None and self.current_vc.is_connected()

    async def get_or_connect_vc(self, ctx: Context | discord.Interaction):
        if isinstance(ctx, Context):
            usr = ctx.author
        else:
            usr = ctx.user
            
        if self.in_vc():
            vc = self.current_vc
        else:
            vc = await usr.voice.channel.connect()
            self.current_vc = vc
        return vc

    @commands.command(name='reloadsounds')
    async def reload(self, ctx: Context):
        module_logger.debug("reloading sounds")
        self.sounds = self.read_sounds()

    @commands.command(name='summon', aliases=['join'])
    async def summon(self, ctx: Context):
        channel = ctx.message.author.voice.channel
        voice = discord.utils.get(ctx.guild.voice_channels, name=channel.name)
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice_client is None:
            self.current_vc = await voice.connect()
            await self.play_file(self.current_vc, self.find_sound_by_name('aaaaaaaa')) #kiabal joinkor
        else:
            await voice_client.move_to(channel)
            await self.play_file(voice_client, self.find_sound_by_name('aaaaaaaa')) #kiabal channel valtaskor
        await ctx.message.delete()

    async def play_source_if_vc(self, source, volume: float):
        if self.in_vc():
            vc = self.current_vc
            await asyncio.sleep(0.5)
            vc.play(discord.FFmpegPCMAudio(executable=self.bot.globals.ffmpeg_path, source=source))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):

        if before.channel is None and after.channel is not None:  # user connected
            await self.on_join_vc(member, before, after)

        if before.channel is not None and after.channel is None:  # user disconnected
            await self.on_leave_vc(member, before, after)

    async def on_join_vc(self, member: Member, before: VoiceState, after: VoiceState):
        await self.bump_jamal_join(member, after.channel.guild.id)
        await self.play_sound_for_goofy_on_vc_event(member, self.bot.globals.greetings["join"])

    async def on_leave_vc(self, member: Member, before: VoiceState, after: VoiceState):
        await self.play_sound_for_goofy_on_vc_event(member, self.bot.globals.greetings["exit"])

    async def play_sound_for_goofy_on_vc_event(self, member: Member, sound_map):
        goofy_short_id = next((k for k, v in self.bot.globals.goofies.items() if v == member.id), None)
        if goofy_short_id in sound_map:
            exit_value = sound_map[goofy_short_id]
            snd = exit_value if type(exit_value) is str else random.choice(exit_value)
            await self.play_source_if_vc(get_resource_name_or_user_override(f"sounds/{snd}"), .5)

    async def bump_jamal_join(self, member, guild_id):
        if str(self.bot.globals.goofies["jamal"]) == str(member.id):
            self.bot.state.get_guild_state_by_id(guild_id).last_shaolin_appearance = datetime.datetime.now()

    @commands.command(name='sound')
    async def play_sound(self, ctx: Context, *args):
        async with ctx.typing():
            vc = await self.get_or_connect_vc(ctx)
            await ctx.message.delete()
            await asyncio.sleep(.5)

        if len(args) == 0:
            file = self.get_random_sound()
        else:
            f_key = " ".join(args)
            file = self.find_sound_by_name(f_key)

        if file is not None:
            self.logger.debug(f'playing {os.path.basename(file)}')
            await self.play_file(vc, file)
        else:
            await ctx.send("mi")

    @commands.command(name='listsounds')
    async def list_sounds(self, ctx: Context):
        snds = ""
        for key in list(self.sounds.keys()):
            snds += f'{key}:\n\t{", ".join([os.path.splitext(snd)[0] for snd in self.sounds[key]])}\n'
        await ctx.send(f'```yml\n{snds}```')

    @staticmethod
    def format_embed_sounds(sounds_slice, page):
        embed = discord.Embed(title="valasz vmit", description=f"{page + 1}. oldal", color=0xed0707)
        for i in range(len(sounds_slice)):
            embed.add_field(name=f"{i}.", value=sounds_slice[i])
        embed.set_footer(text="all right to artsits 2022 @ kTJ")

        return embed

    @commands.command(name="select", hidden=True)
    async def select(self, ctx: Context, *args):
        # TODO: make paginator generic, fix reading new sound list format
        self.logger.debug('sound selecta')

        chosen_category = args[0] if len(args) > 0 else random.choice(list(self.sounds.keys()))

        page_size = 10
        page = 0

        act_slice = list(self.sounds[chosen_category])[page * page_size:page * page_size + page_size]
        msg = await ctx.channel.send(embed=self.format_embed_sounds(act_slice, page))
        await ctx.message.delete()

        n_emojis = [
            "\u0030", "\u0031", "\u0032", "\u0033", "\u0034",  # 0-4
            "\u0035", "\u0036", "\u0037", "\u0038", "\u0039",  # 5-9
            "\u25C0", "\u25B6"  # left - right
        ]

        for r in n_emojis[:10]:
            await msg.add_reaction(r + "\u20E3")  # 0-9 + squares
        for r in n_emojis[10:]:
            await msg.add_reaction(r)

        def check(reaction_obj, usr):
            return reaction_obj.message.id == msg.id and \
                   usr.id != msg.author.id and \
                   usr.id == ctx.message.author.id

        selection = -1
        while selection == -1:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)

                if reaction.emoji in ["◀", "▶"]:
                    self.logger.info(f'switching page {reaction.emoji}')
                    page = page + 1 if reaction.emoji == "▶" else page - 1
                    act_slice = list(self.sounds[chosen_category])[page * page_size:page * page_size + page_size]
                    await msg.edit(embed=self.format_embed_sounds(act_slice, page))
                else:
                    try:
                        remoji_num = reaction.emoji[:-1]
                        selectable_nums = n_emojis[:10]
                        if remoji_num in selectable_nums:
                            selection = selectable_nums.index(str(remoji_num))
                    except TypeError as ex:
                        await ctx.send(f'te hülye vagy gec {user.mention}')
            except asyncio.TimeoutError:
                self.logger.debug("selection timed out")
                selection = -2
            except Exception as e:
                self.logger.error(e, exc_info=True)
                selection = -2
        if selection >= 0:
            self.logger.debug(f'selected: {selection}. -> {act_slice[selection]}')
            vc = await self.get_or_connect_vc(ctx)
            file = self.sound_path(chosen_category, act_slice[selection])
            await self.play_file(vc, file)

        await msg.delete()


async def setup(bot: TrashBot):
    await bot.add_cog(SoundBoardCog(bot))
