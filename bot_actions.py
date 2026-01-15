import discord
from discord import Interaction,Guild,Member,InteractionType,ButtonStyle,Embed, Message, PermissionOverwrite, Role, TextChannel, VoiceChannel
from discord.ui import Modal, TextInput, View, Button, ChannelSelect, RoleSelect
from discord.ext import tasks
from tinydb import Query
from random import choice
from tinydb.table import Document
import bot_globals
from bot_conditions import check_is_approver, is_jam_present,is_user_member
from bot_exceptions import JamCategoryNotPresent, JamNotPresent, JamTeamAlreadyPresent, JamTeamNotPresent, UserNotApprover, UserAlreadyVerified, UserNotInJam
from bot_models import Jam, JamParticipant, JamTeam, UnogMember,ApproveRecord
from bot_views import ApprovalApplyButtonView, ApprovalFormView,ApprovalModal,DenyVerificationModal

async def welcome_member_message(member : Member):
    welcome_channel = await bot_globals.Server_Unog.fetch_channel(bot_globals.TEXTCHANNELID_WELCOME)
    if welcome_channel:
        message = bot_globals.WELCOME_MESSAGES
        if "%split%" in message:
            listelen = message.split("%split%")
            message = choice(listelen)
        if "%user%" in message:
            message = message.replace("%user%", f"{str(member)}")
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
        #emoji = discord.utils.get(bot_globals.Server_Unog.emojis, name=choice(emojiname))
        await msg.add_reaction(choice(emojilist))

async def approvalForm_applyButton_interaction(interaction : Interaction):
    if not is_user_member(interaction.user):
        await interaction.response.send_modal(ApprovalModal(approvalModal_on_submit))
    else: 
        await interaction.response.send_message(f"Zaten <@&{bot_globals.ROLEID_MEMBER}> rolüne sahipsiniz.",ephemeral=True,delete_after=15)

async def approvalForm_denyButton_interaction(interaction : Interaction):
    if check_is_approver(interaction):
        await interaction.response.send_modal(DenyVerificationModal(interaction,denyForm_on_submit))

async def approvalForm_approveButton_interaction(interaction : Interaction):
    if check_is_approver(interaction):
        
        await interaction.message.add_reaction('✅')
        await disable_approval_form(interaction)

        memberID = int(interaction.message.embeds[0].description.split()[0].removeprefix("<@").removesuffix(">"))
        member = interaction.guild.get_member(memberID)
        
        await approve_user(interaction.user,member,
                           interaction.message.embeds[0].fields[0].value,
                           interaction.message.embeds[0].fields[1].value,
                           interaction.message.embeds[0].fields[2].value,
                           interaction.message.embeds[0].fields[3].value,
                           interaction.message.embeds[0].fields[4].value)
        await add_approvalForm_end_status(interaction.message,interaction.user,True)
    else:
        raise UserNotApprover()

async def denyForm_on_submit(interaction : Interaction, deniedMember : Member, reason : str):

    embed = Embed(title="Reddedildi ❌", description="Kullanıcıya mesaj gönderildi!", color=choice(bot_globals.COLORS_UNOG))
    embed.add_field(name="\u200b", value=f"<@{deniedMember.id}>", inline=False)
    embed.add_field(name="Reddetme Sebebi 🤨", value=reason, inline=False)
    embed.add_field(name="Reddeden", value=f"<@{interaction.user.id}>", inline=False)
    embed.set_thumbnail(url=deniedMember.avatar)

    await interaction.response.send_message("", embed=embed)
    await deniedMember.send(f"Merhaba, <@{deniedMember.id}>!\nUmarız iyisindir ve her şey yolundadır. Başvurunu inceledik fakat maalesef aşağıdaki nedenden dolayı kabul edemiyoruz.\n```{reason}```\nEğer formu buna dikkat ederek yeniden doldurursan en kısa sürede başvurunu tekrar inceleyip seni onaylayabiliriz.\nAyrıca eğer bir problemle karşılaşırsan direktörler ile iletişime geçebilirsin. 💙")

async def create_approval_form(unogMember : UnogMember):
    verificationPanelChannel = bot_globals.Server_Unog.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION_PANEL)
    
    member : Member = bot_globals.Server_Unog.get_member(unogMember.id)

    embed = Embed(title="Yeni Üye", description=f"<@{member.id}> sunucuya katıldı!", color=choice(bot_globals.COLORS_UNOG))
    embed.add_field(name="İsim", value=unogMember.name, inline=False)
    embed.add_field(name="E-mail", value=unogMember.email, inline=False)
    embed.add_field(name="Doğum Tarihi", value=unogMember.birthday, inline=False)
    embed.add_field(name="Bulunduğunuz Kurum Veya Ekip", value=unogMember.info1, inline=False)
    embed.add_field(name="ÜNOG'u Nasıl Keşfettiniz?", value=unogMember.info2, inline=False)
    embed.set_thumbnail(url=member.avatar)

    view = ApprovalFormView()
    view.children[0].callback = approvalForm_approveButton_interaction
    view.children[1].callback = approvalForm_denyButton_interaction
    await verificationPanelChannel.send("",embed=embed,view=view)

async def disable_approval_form(interaction : Interaction):
    view = View() 
    buton1 = Button(style=discord.ButtonStyle.green, label="Onayla", disabled=True)
    buton2 = Button(style=discord.ButtonStyle.red, label="Reddet", disabled=True)
    view.add_item(buton1)
    view.add_item(buton2)

    await interaction.message.add_reaction('✅')
    await interaction.response.edit_message(view=view)

async def approvalModal_on_submit(interaction : Interaction, unogMember : UnogMember):
    embed = Embed(title="Talebiniz Alındı!", description="Yetkili tarafından onaylandığında rol ataması yapacağım!", color=choice(bot_globals.COLORS_UNOG))

    await interaction.response.send_message(f"", ephemeral=True, delete_after=30, embed=embed)

    await create_approval_form(unogMember)

async def add_approvalForm_end_status(message : Message,approver : Member,approved : bool):
    embed = message.embeds[0]
    if approved:
        embed.add_field(name="Sonuç",value=f"<@{approver.id}> tarafından onaylandı.")
    else:
        embed.add_field(name="Sonuç",value=f"<@{approver.id}> tarafından reddedildi.")
    await message.edit(embed=embed)

async def approve_user(approver : Member,target_user: Member, newName : str = "", eMail : str = "",birthday : str = "",
                       info1 : str = "", info2 : str = ""):
     
    memberRole = bot_globals.Server_Unog.get_role(bot_globals.ROLEID_MEMBER)

    unogMember = UnogMember(id=target_user.id,
                            name=newName,
                            email=eMail,
                            birthday=birthday,
                            info1=info1,
                            info2=info2)
    approveRecord = ApproveRecord(approvedID=target_user.id,
                                  approverID=approver.id)

    await target_user.add_roles(memberRole)
    await target_user.edit(nick=newName)
    
    bot_globals.TABLE_MEMBERS.upsert(unogMember,Query().id == target_user.id)
    bot_globals.TABLE_APPROVES.insert(approveRecord)

    if bot_globals.WELCOME_NEWCOMERS:
         await welcome_member_message(target_user)

    if bot_globals.LOG_APPROVES:
        await msg_approvalForm_decision(target_user,approver)

async def msg_approvalForm_decision (approved : Member,decisionMaker : Member ,decision : bool = True,additionalInfo : str = ""):
    verificationPanel = bot_globals.Server_Unog.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION_PANEL)
    if verificationPanel:
        embed : Embed = None
        if decision:
            embed = Embed(title=f"Onaylandı! ✅",description=f"<@{approved.id}>", color=choice(bot_globals.COLORS_UNOG))
            embed.add_field(name="Onaylayan", value=f"<@{decisionMaker.id}>", inline=False)
            embed.set_thumbnail(url=approved.avatar.url)
            await verificationPanel.send(embed=embed)
        else:
            embed = Embed(title="Reddedildi ❌", description="Kullanıcıya mesaj gönderildi!", color=choice(bot_globals.COLORS_UNOG))
            embed.add_field(name="\u200b", value=f"<@{approved.id}>", inline=False)
            embed.add_field(name="Reddetme Sebebi 🤨", value=additionalInfo, inline=False)
            embed.add_field(name="Reddeden", value=f"<@{decisionMaker.id}>", inline=False)
            embed.set_thumbnail(url=approved.avatar.url)

@tasks.loop(hours=1)
async def actives():

    view = ApprovalApplyButtonView()
    view.children[0].callback = approvalForm_applyButton_interaction
    bot_globals.UnogBot.add_view(view=view)

    view = ApprovalFormView()
    view.children[0].callback = approvalForm_approveButton_interaction
    view.children[1].callback = approvalForm_denyButton_interaction
    bot_globals.UnogBot.add_view(view=view)

    

    print("Actives refreshed")

#region jam

async def create_jam_participant(discordID: int):
    jamRaw = bot_globals.TABLE_JAM_CURRENT.get(Query()._type=="meta")
    if jamRaw is None:
        return
    jam : Jam = Jam(mapping=jamRaw)
    bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.upsert(JamParticipant(discordID=discordID,teamID=-1),Query().discordID == discordID)
    participantMember : Member = bot_globals.Server_Unog.get_member(discordID)
    participantRole : Role = bot_globals.Server_Unog.get_role(jam.participantRoleID)
    await participantMember.add_roles(participantRole)

async def delete_jam_participant(discordID: int):
    
    jamRaw = bot_globals.TABLE_JAM_CURRENT.get(Query()._type=="meta")
    participantRaw = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == discordID)

    if jamRaw is None:
        return

    if not participantRaw:
        return
    
    jam : Jam = Jam(mapping=jamRaw)
    participant : JamParticipant = JamParticipant(mapping=participantRaw)
    
    if participant.teamID != -1:
        teamDoc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(doc_id=participant.teamID)
        if teamDoc:
            jamTeam = JamTeam(mapping=teamDoc)

            jamTeam.remove_participant(discordID)
            if jamTeam.isEmpty:
                delete_jam_team(teamDoc.doc_id)

    bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.remove(Query().discordID == discordID)
    participantMember : Member = bot_globals.Server_Unog.get_member(discordID)
    participantRole : Role = bot_globals.Server_Unog.get_role(jam.participantRoleID)
    await participantMember.remove_roles(participantRole)

async def create_jam_team(teamName : str) -> int:
    teamName = teamName.strip().lower().replace(" ","-")
    dupe = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(Query().teamName == teamName)
    if not dupe:
        jam_doc = is_jam_present()
        if jam_doc:
            jamData = Jam(mapping=jam_doc)
            jamCategory = bot_globals.Server_Unog.get_channel(jamData.categoryID)
            if jamCategory:
                memberRole = bot_globals.Server_Unog.get_role(bot_globals.ROLEID_MEMBER)
                everyoneRole = bot_globals.Server_Unog.default_role
                voiceChannel : VoiceChannel = await jamCategory.create_voice_channel(
                    teamName,overwrites={everyoneRole:bot_globals.PERMISSION_OVERWRITE_DEFAULT_ROLE,
                                         memberRole:bot_globals.PERMISSION_OVERWRITE_JAM_VERIFIEDMEMBER_VC})
                # textChannel : TextChannel = await jamCategory.create_text_channel(
                #     teamName,overwrites={everyoneRole:bot_globals.PERMISSION_OVERWRITE_DEFAULT_ROLE})
                # await textChannel.set_permissions(memberRole,overwrite=bot_globals.PERMISSION_OVERWRITE_JAM_VERIFIEDMEMBER_VC)
                return bot_globals.TABLE_JAM_CURRENT_TEAMS.insert(JamTeam(teamName=teamName,
                                                                    submitted=False,
                                                                    gameURL="",
                                                                    leader=-1,
                                                                    members=[],
                                                                    textChannelID=-1,
                                                                    voiceChannelID=voiceChannel.id,
                                                                    joinRequests=[]))
            raise JamCategoryNotPresent()
        raise JamNotPresent()
    else:
        raise JamTeamAlreadyPresent()

async def delete_jam_team(team_id : int):
    team_doc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(doc_id=team_id)
    if team_doc:
        team = JamTeam(mapping=team_doc)
        voiceChannel : VoiceChannel = bot_globals.Server_Unog.get_channel(team.voiceChannelID)
        await voiceChannel.delete()
        if team.leader != -1:
            bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.update({"teamID":-1},doc_ids=[team.leader])
        bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.update({"teamID":-1},doc_ids=team.members)
        
        bot_globals.TABLE_JAM_CURRENT_TEAMS.remove(doc_ids=[team_id])
    pass

async def add_participant_to_jam_team(participant_id: int,team_id: int,send_message : bool = False):

    team_raw = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(doc_id=team_id)
    participant_raw = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(doc_id=participant_id)

    if participant_raw and team_raw:
        team = JamTeam(mapping=team_raw)
        participant_discordID = participant_raw.get('discordID')
        team.add_participant(participant_id)
        participant_member : Member = bot_globals.Server_Unog.get_member(participant_discordID)

        teamvc = bot_globals.Server_Unog.get_channel(team.voiceChannelID)
            
        new_overwrites = teamvc.overwrites
        new_overwrites[participant_member] = bot_globals.PERMISSION_OVERWRITE_JAM_TEAM_MEMBER_VC
        await teamvc.edit(overwrites=new_overwrites)

        bot_globals.TABLE_JAM_CURRENT_TEAMS.update(team,doc_ids=[team_id])
        participant_raw['teamID'] = team_id
        bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.update(participant_raw,doc_ids=[participant_id])
        if send_message:
            await teamvc.send(f"**Yeni ekip üyesi eklendi**: {participant_member.mention}")

async def remove_participant_from_jam_team(participant_id: int, send_message : bool = False, interaction : Interaction | None = None):
    participant_doc = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(doc_id=participant_id)
    if participant_doc:
        team_id = participant_doc.get('teamID')
        team_doc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(doc_id=team_id)
        if team_doc:
            team = JamTeam(mapping=team_doc)
            participant_discordID = participant_doc.get('discordID')
            participant_member : Member = bot_globals.Server_Unog.get_member(participant_discordID)
            participant_doc['teamID'] = -1
            team.remove_participant(participant_id)

            teamvc : VoiceChannel = bot_globals.Server_Unog.get_channel(team.voiceChannelID)
            
            new_overwrites = teamvc.overwrites
            new_overwrites.pop(participant_member,None)
            await teamvc.edit(overwrites=new_overwrites)
            if team.isEmpty:
                await delete_jam_team(team_doc.doc_id)
            else:
                bot_globals.TABLE_JAM_CURRENT_TEAMS.update(team,doc_ids=[team_doc.doc_id])
                bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.update(participant_doc,doc_ids=[participant_doc.doc_id])
                if send_message:
                    await teamvc.send(f"{participant_member.mention} ekibinizden ayrıldı.")
            if interaction:
                await interaction.response.send_message("Ekipten çıktınız.",ephemeral=True,delete_after=15)
        else:
            raise JamTeamNotPresent()
    else:
        raise UserNotInJam()
#endregion