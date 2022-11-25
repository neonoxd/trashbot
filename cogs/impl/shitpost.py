import asyncio
import datetime
import io
import logging
import random
import glob
import os
import discord
import requests
from PIL import Image, ImageDraw, ImageFont
from discord.utils import get

from utils.helpers import has_link, replace_str_index, get_user_nick_or_name, find_font_file

module_logger = logging.getLogger('trashbot.Shitpost.impl')

flip_map = {
    "ki": "be",
    "fel": "le",
    "össze": "szét",
    "oda": "vissza",
    "fönn": "lenn",
    "fent": "lent",
    "felül": "alul",
    "áll": "ül"
}


async def command_befli(cog, ctx):
    cog.logger.info("command befli: {}".format(ctx.command))
    finally_image = generate_finally_image("befli")
    await ctx.send(file=discord.File(finally_image, 'befli.jpg'))


async def command_captcha(cog, ctx):
    cog.logger.info("command called: {}".format(ctx.command))
    captcha_img = await get_captcha(cog.bot.globals.ph_token)
    await ctx.send(file=discord.File(captcha_img, 'getsee.png'))


async def command_gabo(cog, ctx, args):
    cog.logger.info(f"command called: {ctx.command} with args {args}")
    await ctx.message.delete()
    if len(args) < 1:
        return
    img = await get_gabo(" ".join(args))
    await ctx.send(file=discord.File(img, 'pg.png'))


async def command_tenemos(cog, ctx):
    cog.logger.info("command called: {}".format(ctx.command))
    await ctx.send(file=discord.File('resources/img/tenemos.jpg'))


async def command_zene(cog, ctx):
    cog.logger.info("command called: {}".format(ctx.command))
    await ctx.send(embed=embed_for("zene", random.choice(cog.trek_list), ctx.message.author))


async def command_dog(cog, ctx):
    cog.logger.info("command called: {}".format(ctx.command))
    await ctx.send(embed=embed_for("dog", random.choice(cog.dogeatdogworld), ctx.message.author))


async def command_kocsi(cog, ctx):
    cog.logger.info("command called: {}".format(ctx.command))
    await ctx.send(embed=embed_for("kocsi", random.choice(cog.kocsiposta), ctx.message.author))


def embed_for(page_name, embed_content, who):
    page_map = {
        "kocsi": {
            "name": "Halálos iramban 3, A KOCSI",
            "url": "https://www.facebook.com/kocsikocsikocsi",
            "pfp": "https://scontent-vie1-1.xx.fbcdn.net/v/t1.6435-9/64678650_2494663417240150_2089116631585259520_n.jpg?_nc_cat=100&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=FTPnmr24Sy4AX9-1guK&_nc_ht=scontent-vie1-1.xx&oh=00_AfCckmSGj0IXrqBMT5gBwH8EhGGL8Nl_dKbkl4iw6pNEwQ&oe=63A87CEE",
            "color": 0x0000ff
        },
        "dog": {
            "name": "Kiskutya megnő, oszt megharapja a nagyot",
            "url": "https://www.facebook.com/kiskutyamegno",
            "pfp": "https://scontent-vie1-1.xx.fbcdn.net/v/t39.30808-6/307536737_213833987634926_7133737757398353005_n.jpg?_nc_cat=100&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=b9a7hQT9HScAX-LdfLJ&tn=js4JzOtCZte-4dPs&_nc_ht=scontent-vie1-1.xx&oh=00_AfBiT1z45PDS8FeUhRn7vQL5nMknNRh7M1rp6ka4QXtyMg&oe=6386917F",
            "color": 0x03fc03
        },
        "zene": {
            "name": "Leg job zenék",
            "url": "https://www.facebook.com/legjobzenek",
            "pfp": "https://scontent-vie1-1.xx.fbcdn.net/v/t39.30808-6/305612470_496312765832307_2357745445834312423_n.jpg?_nc_cat=106&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=bmL4QyzXU8YAX-q4UMR&_nc_ht=scontent-vie1-1.xx&oh=00_AfCsy21l279Yw_pjL1ey0XISxauZXbj5jI00uZsWPGveRw&oe=6386117D",
            "color": 0xfc0303
        }
    }

    pm = page_map[page_name]

    embed = discord.Embed(description=embed_content, title="", color=pm["color"])
    embed.set_author(name=pm["name"], url=pm["url"], icon_url=pm["pfp"])
    embed.set_footer(text=f"Generázva neki: {who}")
    return embed


async def command_beemovie(cog, ctx, args):
    cog.logger.info("command called: {}".format(ctx.command))

    guild_id = ctx.guild.id
    guild_state = cog.bot.state.get_guild_state_by_id(guild_id)

    if not guild_state.bee_initialized:
        guild_state.bee_initialized = True
        guild_state.bee_active = True
        ctx.bot.loop.create_task(beemovie_task(cog, ctx))
    else:
        if len(args) > 0:
            guild_state.bee_page = 0
            await ctx.send("mar nemtom hol tartottam")
        else:
            guild_state.bee_active = not guild_state.bee_active

    if guild_state.bee_active:
        await ctx.send(random.choice(["szal akkor", "na mondom akkor"]))
    else:
        await ctx.send("akk m1...")


async def command_tension(cog, ctx):
    tension = cog.bot.state.get_guild_state_by_id(ctx.guild.id).tension
    module_logger.warning(tension)
    await ctx.channel.send(f'mai vilag tenszio: **{tension}%**')


async def command_gba(cog, ctx):
    module_logger.info(f"[CMD::GBA] called by [{ctx.message.author}]")
    await ctx.message.delete()
    author = get_user_nick_or_name(ctx.message.author)
    if cog.bot.globals.is_expired("gba"):
        newnick = get_kutfuras()
        module_logger.info(f"[CMD::GBA] generated nick [{newnick}]")
        cog.bot.globals.add_timeout("gba", expiry_td=datetime.timedelta(minutes=1))
        member = get(cog.bot.get_all_members(), id=cog.bot.globals.gba_id)
        await member.edit(nick=newnick)
        await ctx.send(f"{author} szerint: {member.mention}")
    else:
        await ctx.send("pill...")


async def command_cz(cog, ctx):
    module_logger.info(f"[CMD::CZ] called by [{ctx.message.author}]")
    await ctx.message.delete()
    author = get_user_nick_or_name(ctx.message.author)
    if cog.bot.globals.is_expired("cz"):
        newnick = get_breveg()
        module_logger.info(f"[CMD::CZ] generated nick [{newnick}]")
        cog.bot.globals.add_timeout("cz", expiry_td=datetime.timedelta(minutes=1))
        member = get(cog.bot.get_all_members(), id=cog.bot.globals.cz_id)
        await member.edit(nick=newnick)
        await ctx.send(f"{author} szerint: {member.mention}")
    else:
        await ctx.send("pill...")


async def event_voice_state_update(cog, member, before, after):
    from utils.state import VCEvent
    now = datetime.datetime.now()
    if before.channel is None and after.channel is not None:  # user connected
        guild = after.channel.guild
        guild_state = cog.bot.state.get_guild_state_by_id(guild.id)
        guild_state.push_last_vc_event(VCEvent(1, member, after.channel, datetime.datetime.timestamp(now)))

        #  elmano alert
        if cog.bot.globals.m_id == member.id:
            if cog.bot.globals.is_expired("m") and guild_state.tension % 2 == 0:
                cog.bot.globals.add_timeout("m", expiry_td=datetime.timedelta(minutes=60))
                await guild.system_channel.send(file=discord.File('resources/img/elmano.gif'))

        #  cz alert
        if cog.bot.globals.cz_id == member.id:
            if cog.bot.globals.is_expired("cz") and guild_state.tension % 2 == 0:
                cog.bot.globals.add_timeout("cz", expiry_td=datetime.timedelta(minutes=1))
                await member.edit(nick=get_breveg())
                await guild.system_channel.send(file=discord.File('resources/img/peter2_alert.jpg'))

        #  p alert
        if cog.bot.globals.p_id == member.id:
            if cog.bot.globals.is_expired("p") and guild_state.tension % 2 == 0:
                cog.bot.globals.add_timeout("p", expiry_td=datetime.timedelta(minutes=60))
                await guild.system_channel.send(file=discord.File('resources/img/peter_alert.png'))

        #  sz alert
        if cog.bot.globals.sz_id == member.id:
            if cog.bot.globals.is_expired("sz"):
                cog.bot.globals.add_timeout("sz", expiry_td=datetime.timedelta(minutes=60))
                await guild.system_channel.send(file=discord.File('resources/img/brunya_alezredes_alert.png'))
                module_logger.debug("BABO ALERT :v")

        #  ghosts alert
        elif member.id in cog.bot.globals.ghost_ids:
            if not guild_state.ghost_alerted_today and guild_state.tension < 90:
                msg_text = f"*{cog.bot.globals.t_states[guild_state.ghost_state % 3]}*"
                guild_state.increment_ghost()
                await after.channel.guild.system_channel.send(msg_text)
                guild_state.ghost_alerted_today = True

    elif before.channel is not None and after.channel is None:  # user disconnected
        guild = before.channel.guild
        guild_state = cog.bot.state.get_guild_state_by_id(guild.id)
        guild_state.last_vc_left = member
        guild_state.push_last_vc_event(VCEvent(0, member, before.channel, datetime.datetime.timestamp(now)))

        #  sz shleep event
        if cog.bot.globals.sz_id == member.id:
            now = datetime.datetime.now()
            if cog.bot.globals.is_expired("sz"):
                module_logger.debug("expired")
                if now.hour >= 21 or now.hour <= 3:
                    guild = before.channel.guild
                    cog.bot.globals.add_timeout("sz", expiry_td=datetime.timedelta(minutes=1))
                    await guild.system_channel.send(file=discord.File('resources/img/szabosleep.png'))
            else:
                await guild.system_channel.send(
                    random.choice(["?", "ájjál le", f"{member.mention} 😡💢", "megmeresztema tüdödet"]))

        #  l shleep event
        if cog.bot.globals.l_id == member.id:
            now = datetime.datetime.now()
            if cog.bot.globals.is_expired("l"):
                module_logger.debug("expired")
                if now.hour >= 21 or now.hour <= 3:
                    guild = before.channel.guild
                    cog.bot.globals.add_timeout("l", expiry_td=datetime.timedelta(minutes=1))
                    await guild.system_channel.send(file=discord.File('resources/img/lacsleep.jpg'))
            else:
                module_logger.debug("GABO LEPKED! :@")
                await guild.system_channel.send(
                    random.choice(["?", f"{member.mention} 😡💢"]))

        if cog.bot.globals.dzs_id == member.id:
            if cog.bot.globals.is_expired("dzs") and guild_state.tension % 2 == 0:
                cog.bot.globals.add_timeout("dzs", expiry_td=datetime.timedelta(minutes=60))
                await guild.system_channel.send("-Dzsoki")
                module_logger.debug("dzsoki leave!")


async def handle_maymay(message):
    files = {os.path.splitext(os.path.basename(f))[0]: f for f in glob.glob("./usr/img/maymay/*")}
    msg_part = message.content.split(">")[1]

    if msg_part == "?":
        await message.reply(f"`{', '.join(list(files.keys()))}`")
        return True

    if msg_part not in files:
        return

    match = files[msg_part]

    module_logger.debug(f"sending maymay [{msg_part}]")

    if os.path.isdir(match):
        multi_files = glob.glob(f"{match}/*")
        randomfile = random.choice(multi_files)
        await message.reply(file=discord.File(randomfile), content=f"> {os.path.basename(randomfile)}",
                            mention_author=False)
    elif os.path.isfile(match):
        await message.reply(file=discord.File(match), mention_author=False)

    return True


def get_kutfuras():
    kutfuras = [
        "Ütvekúrás", "baszex", "baszopás", "bakúrás", "banyalás", "baszék", "basztal", "baszexrény",
        "baszínes televízió", "baszója", "baszósz", "basztalicskázás", "baszikra", "baszike", "baszindróma",
        "fasztarisznya", "tökömtokja", "baromfi", "mérgesfarkas póz", "horkolós szex", "batöcskölés", "bapengetés",
        "bafuck", "basuck", "bapicsa", "baloldal", "baszkurálás", "szexrény", "szextáns", "kúrás", "kúrátor",
        "kúratórium", "faszrahúzás", "szoptatás", "lufibaverés", "single player sex", "bakamatyolás", "szexburger",
        "szexométer", "baszomatic", "baszeged", "depressziós maszturbálás", "bebaszopás", "nagy szext nyomtatás",
        "kurelás", "kurva a péniszen", "szex", "pina", "fasz", "kurva", "geci", "ondó", "spermium", "megtermékenyítés",
        "gyermeknemzés", "csajszibarack", "női pénisz", "punci", "vagina", "sunci", "nuni", "kuki", "fütyi", "fütyülős",
        "broki", "bráner", "agyonkúrás", "baszeplős", "baszínesceruza", "baszív", "porszívós maszturbálás", "kakiszex",
        "popsipattogtatás", "pinában való búvárkodás", "fej szeretkezés", "kígyószelidítés", "anyád hátán kúrás",
        "megaszex", "koccanás", "kufircolás", "baszopikálás", "kardozás", "angry dragon", "rejtett dugasz",
        "zuhanyzós baszex", "dugaszolás", "kakas és labda tortúra", "jamaikai vasutas", "batupírozás", "baszkerev",
        "baszintetizátor", "dugasovics", "baszerver", "baszán", "faszán", "baszámítógép", "baszimpla", "baszotyizás",
        "bakugratás", "kúrt kokain", "pina", "fasz", "geci", "picsa", "szex", "baszopás", "kúrás", "nyalás", "szopás",
        "dugás", "szeretkezés", "pöcsölés", "töcskölés", "közösülés", "pajzánkodás", "kufircolás", "kamatyolás",
        "lovaglás", "gyermeknemzés", "ondó", "spermium", "ah ah", "sex", "kúria", "baszirom", "baszelep", "baszorító",
        "baszoros", "babszint", "baszintezés", "baszont", "baszalámi", "baszumó", "baszita", "baszúnyog", "szopovics",
        "baszopovics", "hancúrozás", "ágypárbaj", "ágyékcsata", "bauxit", "basztálin", "basztornó", "baszatáska",
        "baszúrás", "baszarás", "baszittya", "baszeretkezés", "basteve", "baszínezőfüzet", "baszépítkezés",
        "baszárítógép", "baszőrme", "baszülés", "baszütés", "baszamár", "baszolárium", "baszimulátor", "baszaxás",
        "baszakács", "baszíj", "baszűr", "baszmitek", "baszap istván", "baszimonetta", "baszellős", "baszél", "baszabó",
        "baszabolcs", "baszabadság", "baszem", "baszemét", "átbaszás", "kibaszás", "megbaszás", "szétbaszás",
        "összebaszás", "visszabaszás", "felbaszás", "lebaszás", "odabaszás", "baszextasy", "baszeletelt párizsi",
        "baszállítógép", "baszállító autó", "Aberrált", "Abortuszmaradék", "Abszolút hülye", "Agyalágyult", "Agyatlan", 
        "Agybatetovált", "Ágybavizelős", "Agyfasz", "Agyhalott", "Agyonkúrt", "Agyonvert", "Agyrákos", "AIDS-es",
        "Alapvetően fasz", "Animalsex-mániás", "Antibarom", "Aprófaszú", "Arcbarakott", "Aszaltfaszú", "Aszott",
        "Átbaszott", "Azt a kurva de fasz", "Balfasz", "Balfészek", "Baromfifasz", "Basz-o-matic", "Baszhatatlan",
        "Basznivaló", "Bazmeg", "Bazdmeg", "Bazd meg", "Bazzeg", "Bebaszott", "Befosi", "Békapicsa", "Bélböfi",
        "Beleiből kiforgatott", "Bélszél", "Brunya", "Büdösszájú", "Búvalbaszott", "Buzeráns", "Buzernyák", "Buzi",
        "Buzikurva", "Cafat", "Cafka", "Céda", "Cérnafaszú", "Cigány", "Cottonfej", "Cseszett", "Csibefasz", "Csipszar",
        "Csirkefaszú", "Csitiri", "Csöcs", "Csöcsfej", "Csöppszar", "Csupaszfarkú", "Cuncipunci", "Deformáltfaszú",
        "Dekorált pofájú", "Döbbenetesen segg", "Dobseggű", "Dughatatlan", "Dunyhavalagú", "Duplafaszú", "Ebfasz",
        "Egyszerűen fasz", "Elbaszott", "Eleve hülye", "Extrahülye", "Fantasztikusan segg", "Fasszopó", "Fasz",
        "Fasz-emulátor", "Faszagyú", "Faszarc", "Faszfej", "Faszfészek", "Faszkalap", "Faszkarika", "Faszkedvelő",
        "Faszkópé", "Faszogány", "Faszpörgettyű", "Faszsapka", "Faszszagú", "Faszszopó", "Fasztalan", "Fasztarisznya",
        "Fasztengely", "Fasztolvaj", "Faszváladék", "Faszverő", "Feka", "Félrebaszott", "Félrefingott", "Félreszart",
        "Félribanc", "Fing", "Fölcsinált", "Fölfingott", "Fos", "Foskemence", "Fospisztoly", "Fospumpa", "Fostalicska",
        "Fütyi", "Fütyinyalogató", "Fütykös", "Geci", "Gecinyelő", "Geciszaró", "Geciszívó", "Genny", "Gennyesszájú",
        "Gennygóc", "Genyac", "Genyó", "Gólyafos", "Görbefaszú", "Gyennyszopó", "Gyíkfing", "Hájpacni", "Hatalmas nagy fasz",
        "Hátbabaszott", "Házikurva", "Hererákos", "Hígagyú", "Hihetetlenül fasz", "Hikomat", "Hímnőstény", "Hímringyó",
        "Hiperstrici", "Hitler-imádó", "Hitlerista", "Hivatásos balfasz", "Hú de segg", "Hugyagyú", "Hugyos", "Hugytócsa",
        "Hüje", "Hüle", "Hülye", "Hülyécske", "Hülyegyerek", "Inkubátor-szökevény", "Integrált barom", "Ionizált faszú",
        "IQ bajnok", "IQ fighter", "IQ hiányos", "Irdatlanul köcsög", "Íveltfaszú", "Jajj de barom", "Jókora fasz", "Kaka",
        "Kakamatyi", "Kaki", "Kaksi", "Kecskebaszó", "Kellően fasz", "Képlékeny faszú", "Keresve sem található fasz",
        "Kétfaszú", "Kétszer agyonbaszott", "Ki-bebaszott", "Kibaszott", "Kifingott", "Kiherélt", "Kikakkantott", "Kikészült",
        "Kimagaslóan fasz", "Kimondhatatlan pöcs", "Kis szaros", "Kisfütyi", "Klotyószagú", "Kojak-faszú", "Kopárfaszú",
        "Korlátolt gecizésű", "Kotonszökevény", "Középszar", "Kretén", "Kuki", "Kula", "Kunkorított faszú", "Kurva",
        "Kurvaanyjú", "Kurvapecér", "Kutyakaki", "Kutyapina", "Kutyaszar", "Lankadtfaszú", "Lebaszirgált", "Lebaszott",
        "Lecseszett", "Leírhatatlanul segg", "Lemenstruált", "Leokádott", "Lepkefing", "Leprafészek", "Leszart", "Leszbikus",
        "Lőcs", "Lőcsgéza", "Lófasz", "Lógócsöcsű", "Lóhugy", "Lotyó", "Lucskos", "Lugnya", "Lyukasbelű", "Lyukasfaszú",
        "Lyukát vakaró", "Lyuktalanított", "Mamutsegg", "Maszturbációs görcs", "Maszturbagép", "Maszturbáltatott",
        "Megfingatott", "Megkettyintett", "Megkúrt", "Megszopatott", "Mesterséges faszú", "Méteres kékeres", "Mikrotökű",
        "Molyfing", "Műfaszú", "Muff", "Multifasz", "Műtöttpofájú", "Náci", "[ REDACTED ]", "Nikotinpatkány", "Nimfomániás",
        "Nuna", "Nunci", "Nuncóka", "Nyalábfasz", "Nyasgem", "Nyelestojás", "Nyúlszar", "Oltári nagy fasz",
        "Ondónyelő", "Orbitálisan hülye", "Ordenálé", "Összebaszott", "Ötcsillagos fasz", "Óvszerezett",
        "Pénisz", "Peremesfaszú", "Picsa", "Picsafej", "Picsameresztő", "Picsánnyalt", "Picsánrugott",
        "Picsányi", "Pina", "Pinna", "Pisa", "Pisaszagú", "Pisis", "Pöcs", "Pöcsfej", "Porbafingó", "Pornóbuzi", "Pornómániás",
        "Pudvás", "Pudváslikú", "Puhafaszú", "Punci", "Puncimókus", "Puncis", "Punciutáló", "Puncivirág", "Qki", "Qrva",
        "Qtyaszar", "Rágcsáltfaszú", "Redva", "Rendkívül fasz", "Rétó-román", "Ribanc", "Riherongy", "Rivalizáló", "Rőfös fasz",
        "Rojtospicsájú", "Rongyospinájú", "Roppant hülye", "Rossz kurva", "Saját nemével kefélő", "Segg", "Seggarc", "Seggdugó",
        "Seggfej", "Seggnyaló", "Seggszőr", "Seggtorlasz", "Strici", "Suttyó", "Sutyerák", "Szálkafaszú", "Szar", "Szaralak",
        "Szárazfing", "Szarbojler", "Szarcsimbók", "Szarevő", "Szarfaszú", "Szarházi", "Szarjankó", "Szarnivaló", "Szarosvalagú",
        "Szarrá vágott", "Szarrágó", "Szarszagú", "Szarszájú", "Szartragacs", "Szarzsák", "Szégyencsicska", "Szifiliszes",
        "Szivattyús kurva", "Szófosó", "Szokatlanul fasz", "Szop-o-matic", "Szopógép", "Szopógörcs", "Szopós kurva", "Szopottfarkú",
        "Szűklyukú", "Szúnyogfaszni", "Szuperbuzi", "Szuperkurva", "Szűzhártya-repedéses", "Szűzkurva", "Szűzpicsa", "Szűzpunci",
        "Tikfos", "Tikszar", "Tompatökű", "Törpefaszú", "Toszatlan", "Toszott", "Totálisan hülye", "Tyű de picsa", "Tyúkfasznyi",
        "Tyúkszar", "Vadfasz", "Valag", "Valagváladék", "Végbélféreg", "Xar", "Zsugorított faszú"
            ]

    out = random.choice(kutfuras)
    return replace_str_index(out, 0, out[0].capitalize())


def get_breveg():
    consonants = [char for char in "bcdfghjklmnpqrstvwxz"] + ["gy", "cz", "dzs", "ty", "br"]
    prebuilts = [
        "hét", "gét", "rét", "új", "már", "gép", "tér", "vér", "zágráb", "zárt", "kétabony", "hosszú", "bánat", "dér"
    ]
    enders = [
        "végi", "helyi", "ési", "réti", "gényi", "esi", "melletti", "közi", "kerti", "faszú", "téri", "falvi", "fejű"
    ]

    out = ""
    if random.choice([True, False]):
        pre = random.choice(prebuilts)
        out += pre
        if pre == "dér" and random.randrange(0, 100) > 40:
            out += "heni"
        else:
            out += random.choice(enders)
    else:
        start = random.choice(consonants) + "é"
        end = random.choice(enders)
        mid = random.choice(consonants) if (start[-1:] not in consonants and end[:-1] not in consonants) \
                                           or random.choice([True, False]) else ""
        out = f"{start}{mid}{end}"

    return replace_str_index(out, 0, out[0].capitalize())


async def event_message(cog, message):
    if message.author == cog.bot.user or not message.guild:
        return
    msg_content = str(message.content)
    if len(msg_content) > 0 and msg_content[0] == ">":
        if await handle_maymay(message):
            return

    now = datetime.datetime.now()
    chance = random.randrange(0, 100)

    guild_state = cog.bot.state.get_guild_state_by_id(message.guild.id)
    current_tension = guild_state.tension

    if guild_state.get_channel_state_by_id(message.channel.id) is None:
        guild_state.track_channel(message.channel.id)

    if cog.bot.globals.is_expired("spam"):
        await sentience_spam(cog, message)

    await sentience_flipper(cog, message, chance)

    await sentience_mock_image(cog, message)

    await sentience_answer_question(cog, message, chance)

    if len(message.content) > 250 and chance > 69:
        module_logger.debug(f"long msg procc /w chance {chance}")
        gifs = [
            "https://tenor.com/view/noted-note-the-office-writing-taking-notes-gif-15981193",
            "https://tenor.com/view/write-that-down-taking-notes-school-universities-university-gif-17937210"
        ]
        await message.reply(content=random.choice(gifs), mention_author=True)

    if current_tension is not None and current_tension > 50:
        await sentience_reply(cog, message, now, chance)

    if message.author.id in [cog.bot.globals.p_id, cog.bot.globals.sz_id, cog.bot.globals.cz_id] \
            and random.randrange(0, 1000) == 17:
        if message.author.id == cog.bot.globals.cz_id:
            await message.author.edit(nick=get_breveg())
        await message.channel.send(
            file=discord.File("resources/img/forklift.png", 'forklift.png'),
            content=message.author.mention
        )
        await roll_status(cog.bot)

    if message.tts:
        for react in random.choice([["🇬", "🇪", "🇨", "🇮", "♿"], ["🆗"], ["🤬"], ["👀"]]):
            await message.add_reaction(react)
            await roll_status(cog.bot)

    if message.content == "(╯°□°）╯︵ ┻━┻":
        await message.channel.send("┬─┬ ノ( ゜-゜ノ)")


async def sentience_spam(cog, message):
    # surprise spammers
    guild_state = cog.bot.state.get_guild_state_by_id(message.guild.id)
    channel_state = guild_state.get_channel_state_by_id(message.channel.id)
    if len(message.content) > 0 and 'k!' not in message.content and not cog.bot.user.mentioned_in(
            message):  # TODO extract prefix
        channel_state.add_msg(message)
        if channel_state.shall_i():
            await asyncio.sleep(1)
            await message.channel.send(message.content)
            cog.bot.globals.add_timeout("spam", expiry_td=datetime.timedelta(minutes=5))


async def sentience_flipper(cog, message, roll):
    # flip words meme
    posts = [
        "🆗 gya gec ⚰️\nfeltaláltam\n🧔🏿🤙🏻🧪{0}",
        "🆗 halod\n🧔🏿🤙🏻🧪{0}",
        "mondjuk inkab\n🧔🏿🤙🏻🧪{0}",
        "{0}?👀",
        "mmmmmmmmmmmmmmmm...{0}?"
    ]
    words = {**flip_map, **dict([(value, key) for key, value in flip_map.items()])}
    themsg = ""
    if len(message.content.split(" ")) == 1 and len(has_link(message.content)) == 0 and \
            'k!' not in message.content:
        for word in words.keys():
            if word in message.content:
                themsg = message.content.replace(word, words[word])
    if len(themsg) > 0 and roll > 50:
        if len(themsg) < 16 and roll > 80:
            beflimg = generate_finally_image(themsg)
            await message.channel.send(file=discord.File(beflimg, 'befli.jpg'))
        else:
            await message.channel.send(random.choice(posts).format(themsg))

        await cog.bot.change_presence(activity=discord.Game(
            random.choice(cog.bot.globals.statuses)
        ))


async def sentience_mock_image(cog, message):
    # how/soyjak meme
    chance = 0.995
    roll = random.random()
    image_types = [
        ".jpg",
        ".jpeg",
        ".png"
    ]
    if roll > chance and len(message.attachments) > 0 and any(
            attachment.filename.lower().endswith(imgtype) for imgtype in image_types for attachment in
            message.attachments):
        for attachment in message.attachments:
            await attachment.save(attachment.filename)
            mockimg = get_mock_image(attachment.filename)
            await message.channel.send(file=discord.File(mockimg, 'mock.png'))
            os.remove(attachment.filename)  # might not work on the server os

        await cog.bot.change_presence(activity=discord.Game(
            random.choice(cog.bot.globals.statuses)
        ))


async def sentience_answer_question(cog, message, roll):
    answers = [
        "tollem kerdezed?",
        "jo kerdes batya",
        "ilyen hulye kerdest te😂"
    ]
    if roll > 80 and message.content.endswith("?"):
        cog.logger.info("uncle answered a question")
        await message.reply(random.choice(answers))
        await cog.bot.change_presence(activity=discord.Game(
            random.choice(cog.bot.globals.statuses)
        ))


async def event_typing(cog, channel, user, when):
    await cog.bot.change_presence(activity=discord.Game("latom h irsz geco {}".format(user)))
    await asyncio.sleep(5)
    await cog.bot.change_presence(activity=discord.Game(
        random.choice(cog.bot.globals.statuses)
    ))


async def roll_status(bot):
    await bot.change_presence(activity=discord.Game(
        random.choice(bot.globals.statuses)
    ))


async def sentience_reply(cog, message, now, roll):
    guild_state = cog.bot.state.get_guild_state_by_id(message.guild.id)
    # skippers smh
    if any(skip_word in message.content for skip_word in ["-skip", "!skip"]) and roll < 40:
        cog.logger.info("got lucky with roll chance: %s" % roll)
        await message.channel.send("az jo köcsög volt")
        await roll_status(cog.bot)

    # random trash replies
    elif (now - guild_state.last_slur_dt).total_seconds() > 600 \
            and "k!" not in message.content \
            and roll < 2:
        guild_state.last_slur_dt = datetime.datetime.now()
        cog.logger.info("got lucky with roll chance: %s" % roll)
        await message.channel.send(random.choice(cog.bot.globals.slurs).format(message.author.id))
        await roll_status(cog.bot)


async def mercy_maybe(bot, channel, timeout=30):
    import datetime
    module_logger.info("raffle created with timeout %s" % timeout)
    cur_round = {
        "msgid": None,
        "date": None,
        "users": []
    }

    def check(reaction_obj, usr):
        return reaction_obj.message.id == cur_round["msgid"] and usr.mention not in cur_round["users"]

    msg = await channel.send("A likolok közül kiválasztok egy szerencsés tulélöt, a töbi sajnos meg hal !! @here")
    await roll_status(bot)
    cur_round["msgid"] = msg.id
    cur_round["date"] = datetime.datetime.now()
    cur_round["users"] = []

    while (datetime.datetime.now() - cur_round["date"]).total_seconds() < timeout \
            and int(timeout - (datetime.datetime.now() - cur_round["date"]).total_seconds()) != 0:
        diff = (datetime.datetime.now() - cur_round["date"]).total_seconds()

        timeout_reacc = int(timeout - diff)
        module_logger.info("time's tickin': {} seconds left".format(timeout_reacc))
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=timeout_reacc, check=check)
            cur_round["users"].append(user.mention)
            module_logger.info("got reacc {} {}".format(reaction, user))
        except Exception as e:
            pass
    module_logger.info(f"raffle ended, users: {cur_round['users']}")
    if len(cur_round["users"]) > 0:
        await channel.send("az egyetlen tul élö {}".format(random.choice(cur_round["users"])))
    else:
        await channel.send("sajnos senki nem élte tul")


async def think(bot, channel):
    module_logger.debug(f"thinking activated for channel {channel} - {channel.id} on {channel.guild.name}")
    while True:
        roll_small = random.randrange(0, 1000)
        if roll_small < 1:
            module_logger.info("rolled %s" % roll_small)
            await mercy_maybe(bot, channel)
        elif roll_small < 5:
            module_logger.info("rolled %s" % roll_small)
            await channel.send("most majdnem ki nyirtam vkit")
        await asyncio.sleep(600)


async def get_captcha(captcha_id):
    import io
    from PIL import Image
    import time
    url = f'https://hardverapro.hu/captcha/{captcha_id}.png'
    module_logger.debug(f'url = {url}')
    response = requests.get(url, params={'t': time.time()})
    img = io.BytesIO(response.content)

    rgb_image = Image.open(img).convert("RGBA")
    double_size = (rgb_image.size[0] * 2, rgb_image.size[1] * 2)
    image = rgb_image.resize(double_size)

    bg = Image.open('resources/img/bg.png', 'r')
    text_img = Image.new('RGBA', (bg.width, bg.height), (0, 0, 0, 0))
    text_img.paste(bg, ((text_img.width - bg.width) // 2, (text_img.height - bg.height) // 2))
    text_img.paste(image, ((text_img.width - image.width) // 2, (text_img.height - image.height) // 2), image)
    img_byte_arr = io.BytesIO()
    text_img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


async def get_gabo(input_text):
    fontpath = find_font_file('arial.ttf')[0]

    def break_fix(text, width, font, draw):
        if not text:
            return
        lo = 0
        hi = len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            t = text[:mid]
            w, h = draw.textsize(t, font=font)
            if w <= width:
                lo = mid
            else:
                hi = mid - 1
        t = text[:lo]
        w, h = draw.textsize(t, font=font)
        yield t, w, h
        yield from break_fix(text[lo:], width, font, draw)

    def fit_text(base_img, text, color, font):
        width = base_img.size[0] - 2
        draw = ImageDraw.Draw(base_img)
        sized_font = ImageFont.FreeTypeFont(font.path, 1)
        for size in range(1, 150):
            pieces = list(break_fix(text, width, sized_font, draw))
            height = sum(p[2] for p in pieces)
            if height > base_img.size[1] - 100:
                break
            sized_font = ImageFont.FreeTypeFont(font.path, size)
        module_logger.debug(f"calculated fontsize {sized_font.size}")
        y = (base_img.size[1] - height) // 2
        for t, w, h in pieces:
            x = (base_img.size[0] - w) // 2
            draw.text((x, y), t, font=sized_font, fill=color)
            y += h

    bg = Image.open('resources/img/pgbg.jpg', 'r')
    arial = ImageFont.FreeTypeFont(fontpath, 1)

    text_img = Image.new('RGBA', (bg.width, bg.height), (255, 255, 255, 255))
    text_img.paste(bg, ((text_img.width - bg.width) // 2, (text_img.height - bg.height) // 2))

    img = Image.new('RGBA', (507, 432), color="#685745")
    fit_text(img, input_text, (255, 255, 255), arial)
    text_img.paste(img, ((text_img.width - img.width) // 2 - 30, (text_img.height - img.height) // 2 - 20))
    img_byte_arr = io.BytesIO()
    text_img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


def generate_finally_image(bottom_text):
    from PIL import Image
    from PIL import ImageFont
    from PIL import ImageDraw
    import io

    output = Image.open('resources/img/finally.jpg', 'r')

    bg_w, bg_h = output.size
    draw = ImageDraw.Draw(output)
    font = ImageFont.truetype("impact.ttf", 72)

    top_text = random.choice(["VÉGRE GEC", "FELTALÁLTAM GECO"])
    tw, th = font.getsize(top_text)

    bw, bh = font.getsize(bottom_text)

    draw.text((bg_w / 2 - tw / 2, 0), top_text, (0, 0, 0), font=font)
    draw.text((bg_w / 2 - bw / 2, (bg_h - bh) - 10), bottom_text, (0, 0, 0), font=font)

    img_byte_arr = io.BytesIO()
    output.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


def get_mock_image(msg_image):
    import io
    from PIL import Image

    module_logger.debug('mock image')
    img = Image.open(f'{msg_image}', 'r').convert("RGBA")
    frame_size = (447, 330)  # XDDD🚨
    image = img.resize(frame_size)

    template_paths = [
        'resources/img/memetemplates/hogy.png',
        'resources/img/memetemplates/mi.png',
        'resources/img/memetemplates/question_marks.png',
        'resources/img/memetemplates/soyjaks_pointing.png',
    ]

    template_choice = random.choice(template_paths)
    bg = Image.open(template_choice, 'r').convert("RGBA")
    text_img = Image.new('RGBA', (bg.width, bg.height), (0, 0, 0, 0))
    if template_choice == 'resources/img/memetemplates/soyjaks_pointing.png':
        text_img.paste(image, (1 + (text_img.width - image.width) // 3, -1 + (text_img.height - image.height) // 7),
                       image)
        text_img = Image.alpha_composite(text_img, bg)
    else:
        text_img.paste(bg, ((text_img.width - bg.width) // 2, (text_img.height - bg.height) // 2))
        text_img.paste(image, (1 + (text_img.width - image.width) // 2, -1 + (text_img.height - image.height) // 7),
                       image)

    img_byte_arr = io.BytesIO()
    text_img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


async def beemovie_task(self, ctx):
    guild_id = ctx.guild.id
    state = self.bot.state.get_guild_state_by_id(guild_id)

    while True:
        if state.bee_active and state.bee_page < len(self.beescript):
            await ctx.send(self.beescript[state.bee_page])
            state.bee_page += 1
            if state.bee_page == len(self.beescript):
                state.bee_active = False
                state.bee_page = 0
                await asyncio.sleep(5)
                await ctx.send("na csak ennyit akartam")
        await asyncio.sleep(random.randrange(5, 10))


async def reset_alert_states(bot):
    module_logger.info("resetting ghost_state for all guilds")
    for guild_state in bot.state.guilds:
        guild_state.ghost_alerted_today = False


async def announce_friday_mfs(bot):
    for guild_state in bot.state.guilds:
        guild = discord.utils.get(bot.guilds, id=guild_state.id)
        channel = guild.system_channel
        embed = discord.Embed(title="PPPPÉNTEK ESTE! SOGOR", description="because the uncle can do it edition")
        embed.set_author(name="Kovács Tibor József", url="https://www.facebook.com/tibikevok.jelolj/",
                         icon_url="https://cdn.discordapp.com/attachments/248727639127359490/913774079423684618/422971_115646341961102_1718197155_n.jpg")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/745209915299069952/913788274575835136/friday.png")

        embed.add_field(name="\u200b", value="\n".join(
            ["MIT:", ">JÁCCASZ", ">NÉZEL", ">HALGATOL", ">KAJOLSZ", ">ISZOL", ">SZIVOL", ">REJSZOL"]))

        await channel.send(embed=embed)


async def set_daily_tension(bot, tension=None):
    from cogs.rng import roll
    # TODO: option to only set it for 1 guild
    for guild_state in bot.state.guilds:
        module_logger.debug(f'setting tension for guild : {guild_state.id}')

        guild_state.tension = tension if tension is not None else roll("100")
        guild = discord.utils.get(bot.guilds, id=guild_state.id)
        channel = guild.system_channel

        plus90 = [
            "https://www.youtube.com/watch?v=CDJhBTUg9Zw",  # rero zone
            "Grandmasta Pete - Mérés",
            "x̰̫̘̮́͠ḑ̨̟̝͎͓̮̬͎̜͍̬̬͍͉͕̹̘͞",
            "nem bántás nap",
            "https://www.youtube.com/watch?v=Xf6Geh82vXg"
        ]

        plus50 = [
            "régi kazetá pejáco javitás",
            "xanox44 homemade vape video"
        ]

        sub50 = [
            "https://www.youtube.com/watch?v=A_6wm8HVaVY",
            "Aleksandr Pistoletov - Gladiator",
            "Kibaszott Stryker",
            "lecsalos live"
        ]

        t_str = f'{guild_state.tension}%'
        if guild_state.tension > 90:
            tension = random.choice([t_str] + plus90)
        elif guild_state.tension in [69, 420]:
            tension = t_str
        elif guild_state.tension > 50:
            tension = random.choice([t_str] + plus50)
        else:
            tension = random.choice([t_str] + sub50)

        t_msg = f'mai vilag tenszion: **{tension}**'

        #  IDEA: roll for random skulls, tbd what they do

        skulls = []

        if guild_state.tension < 50:
            skulls.append("cement: off")

        if guild_state.tension == 69:
            skulls.append("NICE 😏")

        if len(skulls) > 0:
            t_msg += f'\n **skulls:** {", ".join(skulls)}'
        await roll_status(bot)
        await channel.send(t_msg)
