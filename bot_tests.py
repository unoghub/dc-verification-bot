from tinydb import TinyDB

from bot_globals import DATABASE_UNOG

from discord.ext import commands
from bot import *
from bot_modals import *
from bot_events import *
from bot_actions import *


async def send_welcome_message_test(guild, channel, member):
    db = TinyDB(UNOG_DATABASE)
    message = db.table('newusermessage')
    message = message.search(Query().guild == 287963427362832386)
    if message:
        message = message[0]['message']
        if "%split%" in message:
            listelen = message.split("%split%")
            message = choice(listelen)
        if "%user%" in message:
            message = message.replace("%user%", f"{member.nick}")
        if "\>" in message:
            message = message.replace("\<", f"<")
        embed = discord.Embed(title="ÜNOG'a Hoş Geldin!", description=message, color=choice(UNOG_COLORS))
        embed.set_thumbnail(url=member.avatar)
        msg = await channel.send("", embed=embed)
        emojilist = [
        "👋", "🎉", "✨", "🎊", "🌟", "🚀", "🎈", "✅", "🪄",
        "🌠", "🔥","💫", "💎",
        "🎶", "📣", "⚡", "🌅", "🥳","🎮","🕹️", "💻",
        "🖥️", "🏞️", "💾"
        ]
        emojiname = [
            "Welcome",
            "ZoeWelcome",
            "blushie",
            "bnhatodorokidab",
            "ere",
            "hello",
            "hellothere",
            "hellothere1",
            "sailor_mercury",
            "watamee",
            "welcomehat",
            "PepeWelcome",
            "EN_Pretty",
            "EN_neko_expect",
            "EN_cat_mustache46",
            "A_logo_unog",
            "E_VoHiYo",
            "YoureWelcome",
            "kanna_oh_welcome",
            "blue_welcome",
            "Iruma_wiggle_dizzy_dance",
            "cute2",
            "welcomea",
            "welcometohell",
            "kawaiiwave",
            "3GMAROC",
            "E_Excited",
            "E_CuteTakingNotes",
            "E_cuteDog"
        ]
        emoji = discord.utils.get(guild.emojis, name=choice(emojiname))
        await msg.add_reaction(choice((choice(emojilist), emoji)))

