import discord
from discord import Interaction,Guild,Member,InteractionType,ButtonStyle,Embed
from discord.ui import Modal, TextInput, View, Button, ChannelSelect, RoleSelect
from tinydb import Query
from random import choice
from bot_modals import DenyVerificationModal,ApprovalModal
import bot_globals
from bot_conditions import check_is_approver
from bot_exceptions import UserNotApprover


async def welcome_member_message(guild : Guild, member : Member):
    welcome_channel = await guild.fetch_channel(bot_globals.TEXTCHANNELID_WELCOME)
    if welcome_channel:
        message = bot_globals.WELCOME_MESSAGES
        if "%split%" in message:
            listelen = message.split("%split%")
            message = choice(listelen)
        if "%user%" in message:
            message = message.replace("%user%", f"{member.nick}")
        if "\>" in message:
            message = message.replace("\<", f"<")

        embed = Embed(title="ÜNOG'a Hoş Geldin!", description=message, color=choice(bot_globals.COLORS_UNOG))
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
        await msg.add_reaction(choice(emojilist))

async def on_verification_apply_button_clicked(interaction : Interaction):

            if bot_globals.Server_Unog.get_role(bot_globals.ROLEID_MEMBER) in interaction.user.roles:
                await interaction.response.send_message("Sistemimizde onaylı gözüküyorsunuz, bir hata durumunda Direktörlerimize ulaşabilirsiniz.", ephemeral=True, delete_after=10)
                return
            await interaction.response.send_modal(ApprovalModal(denyCallback=deny_by_application,approveCallback=approve_by_application))

async def deny_by_application(interaction : Interaction):
    print("denylogic")
    if check_is_approver(interaction):
        await interaction.response.send_modal(DenyVerificationModal(interaction))
    else:
        raise UserNotApprover()

async def approve_by_application(interaction : Interaction):
    if check_is_approver(interaction):
        view = View() 
        buton1 = Button(style=discord.ButtonStyle.green, label="Onayla", disabled=True)
        buton2 = Button(style=discord.ButtonStyle.red, label="Reddet", disabled=True)
        view.add_item(buton1)
        view.add_item(buton2)
        memberID = int(interaction.message.embeds[0].description.split()[0].removeprefix("<@").removesuffix(">"))

        await interaction.message.add_reaction('✅')
        await interaction.response.edit_message(view=view)

        embed = Embed(title="Onaylandı! :white_check_mark:",description=f"{interaction.message.embeds[0].description.split()[0]}")
        embed.add_field(name="Onaylayan",value=f"<@{interaction.user.id}>")
        await interaction.followup.send("",embed=embed)
        memberRole = interaction.guild.get_role(bot_globals.ROLEID_MEMBER)
        member = interaction.guild.get_member(memberID)
        await member.add_roles(memberRole)
        await member.edit(nick=interaction.message.embeds[0].fields[0].value)
        await welcome_member_message(interaction.guild,member)
        bot_globals.TABLE_MEMBERS.upsert({'name': interaction.message.embeds[0].fields[0].value ,'email': interaction.message.embeds[0].fields[1].value, 'birthday': interaction.message.embeds[0].fields[2].value, 'info1': interaction.message.embeds[0].fields[3].value, 'info2': interaction.message.embeds[0].fields[4].value, 'id': memberID}, Query().id == memberID)
        bot_globals.TABLE_APPROVES.upsert({'approvedID':memberID,'approverID':interaction.user.id},Query().approverID == interaction.user.id)
    else:
        raise UserNotApprover()


# async def approve_verification(interaction : Interaction):

#     if not is_user_approver(interaction.user):
#         await reply_no_permission(interaction.context)
#         return
    
#     user = interaction.message.embeds[0].description
#     user = user.split(">")[0]
#     user = int(user.split("@")[1])
#     user = interaction.guild.get_member(user)
#     username = interaction.message.embeds[0].fields[0].value

#     try:
#         await user.edit(nick=username.title())
#     except:
#         print(f"User {user} could not be edited")
    
#     try:
#         await user.add_roles(bot_globals.ROLEID_MEMBER)
#     except:
#         print(f"Member role could not be added to {user}")

#     bot_globals.TABLE_MEMBERS.update({'verified': True}, Query().id == user.id)

#     embed = Embed(title=f"Onaylandı! ✅", color=choice(bot_globals.COLORS_UNOG))
#     embed.add_field(name="\u200b", value=f"<@{user.id}>", inline=False)
#     embed.add_field(name="Onaylayan", value=interaction.user.mention, inline=False)
#     embed.set_thumbnail(url=user.avatar)

#     await interaction.response.send_message(f"", embed=embed)

#     if interaction.type == InteractionType.component:
#         await interaction.message.add_reaction("✅")
#         buton1 = Button(style=ButtonStyle.green, label="Onayla", custom_id="onayla", disabled=True)
#         buton2 = Button(style=ButtonStyle.red, label="Reddet", custom_id="reddet", disabled=True)
#         view = View()
#         view.add_item(buton1)
#         view.add_item(buton2)
#         await interaction.message.edit(view=view)

#     await welcome_member_message(interaction.guild, user) 