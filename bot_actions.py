import discord
import time
from discord import CategoryChannel, Colour,Interaction,Guild,Member,InteractionType,ButtonStyle,Embed, Message, PermissionOverwrite, Role, TextChannel, VoiceChannel
from discord.ui import Modal, TextInput, View, Button, ChannelSelect, RoleSelect
from discord.ext import tasks
from tinydb import Query
from random import choice
from tinydb.table import Document
import bot_globals
from bot_conditions import *
from bot_exceptions import *
from bot_models import Jam, JamParticipant, JamTeam, UnogMember,ApproveRecord
from bot_views import ApprovalApplyButtonView, ApprovalFormView,ApprovalModal,DenyVerificationModal, JamSubmissionPendingView

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
        await interaction.response.send_modal(DenyVerificationModal(interaction,approvalDenyModal_on_submit))

async def approvalForm_approveButton_interaction(interaction : Interaction):
    if check_is_approver(interaction):
        
        await interaction.message.add_reaction('✅')
        await disable_approval_form(interaction)

        memberID = int(interaction.message.embeds[0].description.split()[0].removeprefix("<@").removesuffix(">"))
        member = interaction.guild.get_member(memberID)
        
        await approve_user(approver=interaction.user,
                           target_user=member,
                           newName=interaction.message.embeds[0].fields[0].value,
                           eMail=interaction.message.embeds[0].fields[1].value,
                           birthday=interaction.message.embeds[0].fields[2].value,
                           info1=interaction.message.embeds[0].fields[3].value,
                           info2=interaction.message.embeds[0].fields[4].value)
        await add_approvalForm_end_status(interaction.message,interaction.user,True)
    else:
        raise YouMustBeApproverException()

async def approvalDenyModal_on_submit(interaction : Interaction, deniedMember : Member, reason : str):

    await interaction.message.add_reaction('❌')
    embed = Embed(title="Reddedildi ❌", description="Kullanıcıya mesaj gönderildi!", color=choice(bot_globals.COLORS_UNOG))
    embed.add_field(name="\u200b", value=f"<@{deniedMember.id}>", inline=False)
    embed.add_field(name="Reddetme Sebebi 🤨", value=reason, inline=False)
    embed.add_field(name="Reddeden", value=f"<@{interaction.user.id}>", inline=False)
    embed.set_thumbnail(url=deniedMember.avatar)
    await disable_approval_form(interaction)
    panelChannel = bot_globals.Server_Unog.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION_PANEL)
    await panelChannel.send("", embed=embed)
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
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)

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

    await interaction.response.edit_message(view=view)

async def disable_submission_form(interaction: Interaction):
    view = View() 
    buton1 = Button(style=discord.ButtonStyle.green, label="Geçerli", disabled=True)
    buton2 = Button(style=discord.ButtonStyle.red, label="Geçersiz", disabled=True)
    view.add_item(buton1)
    view.add_item(buton2)
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

    if len(newName) < 1:
        raise UserNewNameCouldNotBeEmpty()
    elif str.isalnum(newName):
        raise UserNewNameMustBeAlphanumeric()

    update = UnogMember(id=target_user.id,
                        name=newName,
                        email=eMail,
                        birthday=birthday,
                        info1=info1,
                        info2=info2)
    approveRecord = ApproveRecord(approvedID=target_user.id,
                                approverID=approver.id)
    
    bot_globals.TABLE_MEMBERS.upsert(update,Query().id == target_user.id)
    bot_globals.TABLE_APPROVES.upsert(approveRecord,Query().approvedID == target_user.id)

    await target_user.add_roles(memberRole)
    await target_user.edit(nick=newName)
    

    if bot_globals.LOG_APPROVES:
        await msg_approvalForm_decision(target_user,approver)
    if bot_globals.WELCOME_NEWCOMERS:
         await welcome_member_message(target_user)

    

async def msg_approvalForm_decision (approved : Member,decisionMaker : Member ,decision : bool = True,additionalInfo : str = ""):
    verificationPanel = bot_globals.Server_Unog.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION_PANEL)
    if verificationPanel:
        embed : Embed = None
        if decision:
            embed = Embed(title=f"Onaylandı! ✅",description=f"<@{approved.id}>", color=choice(bot_globals.COLORS_UNOG))
            embed.add_field(name="Onaylayan", value=f"<@{decisionMaker.id}>", inline=False)
            if approved.avatar:
                embed.set_thumbnail(url=approved.avatar.url)
            await verificationPanel.send(embed=embed)
        else:
            embed = Embed(title="Reddedildi ❌", description="Kullanıcıya mesaj gönderildi!", color=choice(bot_globals.COLORS_UNOG))
            embed.add_field(name="\u200b", value=f"<@{approved.id}>", inline=False)
            embed.add_field(name="Reddetme Sebebi 🤨", value=additionalInfo, inline=False)
            embed.add_field(name="Reddeden", value=f"<@{decisionMaker.id}>", inline=False)
            if approved.avatar:
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

    view = JamSubmissionPendingView()
    view.children[0].callback = on_jam_submit_approve
    view.children[1].callback = on_jam_submit_deny
    bot_globals.UnogBot.add_view(view=view)

    print("Actives refreshed")

#region jam

async def submit_jam_project(team_doc : Document, submissionURL : str):

    duplicate_checker = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(Query().gameURL == submissionURL)
    if duplicate_checker and duplicate_checker.doc_id != team_doc.doc_id:
        raise YourJamTeamSubmissionIsNotUniqueException()
    
    
    team : JamTeam = JamTeam(mapping=team_doc)
    if team.gameURL != "":
        raise YourJamTeamAlreadySubmittedException()
    

    team.gameURL = submissionURL.strip()
    jam = Jam(mapping=is_jam_present())
    bot_globals.TABLE_JAM_CURRENT_TEAMS.update(team,doc_ids=[team_doc.doc_id])
    panelChannel = bot_globals.Server_Unog.get_channel(jam.modPanelChannelID)
    embed = Embed(title=f"'{team.teamName}' takımı oyununu gönderdi!",description=f"🕒 Gönderim vakti: <t:{int(time.time())}:F>\n🌐 URL: {team.gameURL}\nBu oyunun geçerli/geçersiz olarak onaylanmasını yapın.")
    view = JamSubmissionPendingView()
    view.children[0].callback = on_jam_submit_approve
    view.children[1].callback = on_jam_submit_deny
    await panelChannel.send("",embed=embed,view=view)

async def on_jam_submit_approve(interaction : Interaction):
    approver = is_user_approver(interaction.user)
    if not approver:
        raise YouMustBeApproverException()
    teamName = interaction.message.embeds[0].title.split(" ")[0].removeprefix("'").removesuffix("'")
    team_doc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(Query().teamName == teamName)
    bot_globals.TABLE_JAM_CURRENT_TEAMS.update({'passed':True},doc_ids=[team_doc.doc_id])
    await disable_submission_form(interaction=interaction)
    await interaction.message.add_reaction("✅")

async def on_jam_submit_deny(interaction: Interaction):
    approver = is_user_approver(interaction.user)
    if not approver:
        raise YouMustBeApproverException()
    teamName = interaction.message.embeds[0].title.split(" ")[0].removeprefix("'").removesuffix("'")
    team_doc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(Query().teamName == teamName)
    bot_globals.TABLE_JAM_CURRENT_TEAMS.update({'passed':False},doc_ids=[team_doc.doc_id])
    await disable_submission_form(interaction=interaction)
    await interaction.message.add_reaction("❌")

async def create_jam(shortName :str,fullName:str,unix_start:int,unix_end:int,url:str,description:str =""):

    guild: Guild = bot_globals.Server_Unog
    shortName = shortName.strip().upper().replace(" ","")
    fullName = fullName.strip().title()
    url = url.strip().replace(" ","")

    jamModRole = guild.get_role(bot_globals.ROLEID_JAM_MOD)
    verifiedRole = guild.get_role(bot_globals.ROLEID_MEMBER)
    directorRole = guild.get_role(bot_globals.ROLEID_DIRECTOR)
    botDevRole = guild.get_role(bot_globals.ROLEID_BOTDEV)

    visibilityOverrideForChannels = {
        guild.default_role:bot_globals.PERMISSION_OVERWRITE_DEFAULT_ROLE,
        verifiedRole:PermissionOverwrite(view_channel=True),
        directorRole:PermissionOverwrite(view_channel=True),
        botDevRole:PermissionOverwrite(view_channel=True)
    }
    #visibility overrideları yapıyordun!
    category: CategoryChannel = await guild.create_category(fullName,overwrites=visibilityOverrideForChannels)
    voiceChannel = await guild.create_voice_channel(name=f"{shortName} Sohbet", category=category)
    textChannel = await guild.create_text_channel(str.lower(f"{shortName}-genel"), category=category)
    panelChannel = await guild.create_text_channel(f"{shortName}-moderatör-paneli",category=category,overwrites={
        guild.default_role:bot_globals.PERMISSION_OVERWRITE_DEFAULT_ROLE,
        jamModRole:PermissionOverwrite(view_channel=True),
        directorRole:PermissionOverwrite(view_channel=True),
        botDevRole:PermissionOverwrite(view_channel=True)
    })

    participantRole : Role = await guild.create_role(name=shortName + " Katılımcısı",colour=Colour.random())
    jammerRole : Role = await guild.create_role(name=shortName + " Jammer",colour= Colour.random())

    jam : Jam = Jam(shortName,
                    fullName,
                    startUnix=unix_start,
                    endUnix=unix_end,
                    categoryID=category.id,
                    generalVoiceChannelID=voiceChannel.id,
                    generalTextChannelID=textChannel.id,
                    participantRoleID=participantRole.id,
                    modPanelChannelID=panelChannel.id,
                    jammerRoleID=jammerRole.id,
                    description=description,
                    url=url)

    bot_globals.TABLE_JAM_CURRENT.insert(jam)

async def delete_jam():
    jam_doc : Document = bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")
    jam : Jam = Jam(mapping=jam_doc)
    categoryID : int = jam_doc.get('categoryID')
    for i in bot_globals.Server_Unog.categories:
        if i.id == categoryID:
            for j in i.channels:
                await j.delete()
            await i.delete()
            break
    
    all_participants = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.all()
    participantRole = bot_globals.Server_Unog.get_role(jam.participantRoleID)
    jammerRole = bot_globals.Server_Unog.get_role(jam.jammerRoleID)
    for participant in all_participants:
        member = bot_globals.Server_Unog.get_member(participant.get('discordID'))
        await member.remove_roles(participantRole)
        teamid = participant.get('teamID')
        if teamid != -1:
            team = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(doc_id=teamid)
            if team.get('passed'):
                await member.add_roles(jammerRole)
                await member.send(f"Tebrikler! {jam.longName} Sonucunda gönderdiğiniz oyun moderatörlerimizce kabul edildi ve {jammerRole.mention} kalıcı rolünü kazandınız.")

    bot_globals.TABLE_JAM_CURRENT.truncate()
    bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.truncate()
    bot_globals.TABLE_JAM_CURRENT_TEAMS.truncate()
    bot_globals.TABLE_JAM_FORMS.truncate()
    role_participant : Role = bot_globals.Server_Unog.get_role(jam.participantRoleID)
    await role_participant.delete(reason="Jam bitti.")

async def create_jam_participant(user : Member):
    jamRaw = bot_globals.TABLE_JAM_CURRENT.get(Query()._type=="meta")
    if jamRaw is None:
        return
    jam : Jam = Jam(mapping=jamRaw)
    bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.upsert(JamParticipant(discordID=user.id,teamID=-1),Query().discordID == user.id)
    participantMember : Member = bot_globals.Server_Unog.get_member(user.id)
    participantRole : Role = bot_globals.Server_Unog.get_role(jam.participantRoleID)
    await participantMember.add_roles(participantRole)

async def delete_jam_participant(participant_doc_id: int):
    jam_doc = bot_globals.TABLE_JAM_CURRENT.get(Query()._type=="meta")
    if not jam_doc:
        return
    participant_doc = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == participant_doc_id)
    if not participant_doc:
        return
    jam : Jam = Jam(mapping=jam_doc)
    participant : JamParticipant = JamParticipant(mapping=participant_doc)
    if participant.teamID != -1:
        teamDoc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(doc_id=participant.teamID)
        if teamDoc:
            jamTeam = JamTeam(mapping=teamDoc)

            jamTeam.remove_participant(participant_doc_id)
            if jamTeam.isEmpty:
                delete_jam_team(teamDoc.doc_id)

    bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.remove(Query().discordID == participant_doc_id)
    participantMember : Member = bot_globals.Server_Unog.get_member(participant_doc_id)
    participantRole : Role = bot_globals.Server_Unog.get_role(jam.participantRoleID)
    await participantMember.remove_roles(participantRole)

async def create_jam_team(teamName : str,categoryChannel : CategoryChannel) -> int: #DONE 
    teamName = teamName.strip().lower().replace(" ","-")
    memberRole = bot_globals.Server_Unog.get_role(bot_globals.ROLEID_MEMBER)
    everyoneRole = bot_globals.Server_Unog.default_role
    voiceChannel : VoiceChannel = await categoryChannel.create_voice_channel(
        teamName,overwrites={everyoneRole:bot_globals.PERMISSION_OVERWRITE_DEFAULT_ROLE,
                                memberRole:bot_globals.PERMISSION_OVERWRITE_JAM_VERIFIEDMEMBER_VC})
    return bot_globals.TABLE_JAM_CURRENT_TEAMS.insert(JamTeam(teamName=teamName,
                                                                passed=False,
                                                                gameURL="",
                                                                leader=-1,
                                                                members=[],
                                                                textChannelID=-1,
                                                                voiceChannelID=voiceChannel.id,
                                                                joinRequests=[]))

async def delete_jam_team(team_doc : Document): #DONE
    team = JamTeam(mapping=team_doc)
    voiceChannel : VoiceChannel = bot_globals.Server_Unog.get_channel(team.voiceChannelID)
    if voiceChannel:
        await voiceChannel.delete()
    if team.leader != -1:
        bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.update({"teamID":-1},doc_ids=[team.leader])
    bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.update({"teamID":-1},doc_ids=team.members)
    bot_globals.TABLE_JAM_CURRENT_TEAMS.remove(doc_ids=[team_doc.doc_id])

async def add_jam_join_request_to_jam_team(participant_doc : Document,team_doc: Document):#DONE
    team : JamTeam = JamTeam(mapping=team_doc)
    voiceChannel = bot_globals.Server_Unog.get_channel(team.voiceChannelID)

    if participant_doc.doc_id in team.joinRequests:
        raise JamTeamJoinRequestAlreadySentException()
    elif participant_doc.doc_id in team.members or participant_doc.doc_id == team.leader:
        raise YouAlreadyInRequestedJamTeamException()
    team.joinRequests.append(participant_doc.doc_id)
    bot_globals.TABLE_JAM_CURRENT_TEAMS.update({'joinRequests':team.joinRequests},doc_ids=[team_doc.doc_id])
    await voiceChannel.send(f"Hey! <@{participant_doc.get('discordID')}> isimli kullanıcı ekibinize katılmak istiyor.\n\n Kabul etmek için:\n `/jam ekip-isteğini-kabul-et <discord_username>`\n komutunu kullanabilirsiniz.")

async def add_participant_to_jam_team(participant_doc: Document,team_doc: Document,send_message_to_team : bool = False): #DONE
    team = JamTeam(mapping=team_doc)
    participant_member : Member = bot_globals.Server_Unog.get_member(participant_doc.get('discordID'))
    team.add_participant(participant_doc.doc_id)
    teamvc = bot_globals.Server_Unog.get_channel(team.voiceChannelID)
    new_overwrites = teamvc.overwrites
    new_overwrites[participant_member] = bot_globals.PERMISSION_OVERWRITE_JAM_TEAM_MEMBER_VC
    await teamvc.edit(overwrites=new_overwrites)

    bot_globals.TABLE_JAM_CURRENT_TEAMS.update(team,doc_ids=[team_doc.doc_id])
    bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.update({'teamID':team_doc.doc_id},doc_ids=[participant_doc.doc_id])
    if send_message_to_team:
        await teamvc.send(f"**Yeni ekip üyesi**: {participant_member.mention}")

async def remove_participant_from_jam_team(participant_doc: Document, send_message_to_team : bool = False):#DONE
    team_id = participant_doc.get('teamID')

    team_doc : Document = None
    if team_id != -1:
        team_doc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(doc_id=team_id)
    else:
        Deneme = Query()
        team_doc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get((Deneme.members.any(Query().value == participant_doc.doc_id)) |
        (Deneme.leader == participant_doc.doc_id))

    team = JamTeam(mapping=team_doc)
    participant_member : Member = bot_globals.Server_Unog.get_member(participant_doc.get("discordID"))
    bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.update({'teamID':-1},doc_ids=[participant_doc.doc_id])
    team.remove_participant(participant_doc.doc_id)
    teamvc : VoiceChannel = bot_globals.Server_Unog.get_channel(team.voiceChannelID)
    new_overwrites = teamvc.overwrites
    new_overwrites.pop(participant_member,None)
    await teamvc.edit(overwrites=new_overwrites)
    if team.isEmpty:
        await delete_jam_team(team_doc)
    else:
        bot_globals.TABLE_JAM_CURRENT_TEAMS.update(team,doc_ids=[team_doc.doc_id])
        if send_message_to_team:
            await teamvc.send(f"{participant_member.mention} ekibinizden ayrıldı.")
       
    
#endregion