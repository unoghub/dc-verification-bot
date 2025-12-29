import discord
from discord import Interaction,Guild,Member,InteractionType,ButtonStyle,Embed
from discord.ui import Modal, TextInput, View, Button, ChannelSelect, RoleSelect
from tinydb import Query
from random import choice
from bot_conditions import is_user_approver,is_user_admin
from bot_modals import DenyVerificationModal
from bot_exceptions import reply_no_permission
import bot_globals



async def welcome_member_message(guild : Guild, member : Member):
    welcome_channel = await guild.fetch_channel(globals.TEXTCHANNELID_WELCOME)
    if welcome_channel:

        message = str(globals.WELCOME_MESSAGES)
        if "%split%" in message:
            listelen = message.split("%split%")
            message = choice(listelen)
        if "%user%" in message:
            message = message.replace("%user%", f"{member.nick}")
        if "\>" in message:
            message = message.replace("\<", f"<")

        embed = Embed(title="ÜNOG'a Hoş Geldin!", description=message, color=choice(globals.COLORS_UNOG))
        embed.set_thumbnail(url=member.avatar)
        msg = await welcome_channel.send("", embed=embed)
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

async def approve_verification(interaction : Interaction):

    if not is_user_approver(interaction.user):
        await reply_no_permission(interaction.context)
        return
    
    user = interaction.message.embeds[0].description
    user = user.split(">")[0]
    user = int(user.split("@")[1])
    user = interaction.guild.get_member(user)
    username = interaction.message.embeds[0].fields[0].value

    try:
        await user.edit(nick=username.title())
    except:
        print(f"User {user} could not be edited")
    
    try:
        await user.add_roles(globals.ROLEID_MEMBER)
    except:
        print(f"Member role could not be added to {user}")

    bot_globals.TABLE_MEMBERS.update({'verified': True}, Query().id == user.id)

    embed = Embed(title=f"Onaylandı! ✅", color=choice(globals.COLORS_UNOG))
    embed.add_field(name="\u200b", value=f"<@{user.id}>", inline=False)
    embed.add_field(name="Onaylayan", value=interaction.user.mention, inline=False)
    embed.set_thumbnail(url=user.avatar)

    await interaction.response.send_message(f"", embed=embed)

    if interaction.type == InteractionType.component:
        await interaction.message.add_reaction("✅")
        buton1 = Button(style=ButtonStyle.green, label="Onayla", custom_id="onayla", disabled=True)
        buton2 = Button(style=ButtonStyle.red, label="Reddet", custom_id="reddet", disabled=True)
        view = View()
        view.add_item(buton1)
        view.add_item(buton2)
        await interaction.message.edit(view=view)

    await welcome_member_message(interaction.guild, user) 

async def deny_verification(interaction : Interaction):
    if not is_user_admin(interaction.user):
        await reply_no_permission()
        return
    await interaction.response.send_modal(DenyVerificationModal(interaction))