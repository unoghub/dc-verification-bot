import discord
import json
import os
from random import choice
from discord.ui import View,Button
from discord import Embed,File,Attachment,ButtonStyle,Interaction,Member,Role,Guild,CategoryChannel,Object
from discord.ext.commands import Context,Bot,check
from openpyxl import Workbook
from tinydb import Query
import bot_globals
from bot_modals import ApprovalModal,VerificationPanelChannelSelect,MemberRoleSelect,ApproverRoleSelect,VerificationChannelSelect,WelcomeChannelSelect
from discord.app_commands.checks import has_any_role,has_role
from discord import app_commands
from bot_actions import welcome_member_message
from bot_exceptions import reply_no_permission,JamAlreadyPresent,JamAlreadyParticipating,JamTeamAlreadyPresent,NoJamPresent,JamNotParticipating
from bot_conditions import check_is_approver,check_is_jam_mod,check_is_botdev,check_is_member,check_has_top_access,check_can_create_jam_team
from bot_events import actives

def setup_commands(bot_instance: Bot):

    @bot_instance.tree.command(name="indir_veritabanı",guild=bot_globals.GUILD_UNOG,description="ÜNOG Veritabanını JSON olarak indirir ve günceller.")
    @app_commands.check(check_has_top_access)
    async def dbjson(interaction: Interaction):
        file = File("unog.json")
        await interaction.response.send_message("ÜNOG veritabanı oluşturuldu/güncellendi.",file=file,ephemeral=True)

    @bot_instance.tree.command(name="ayarlar",description="Bot ayarları panelini aç.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_has_top_access)
    async def botSettings(interctn: Interaction):

        embed = Embed(title="Bot Ayarları", description="Onaylama kanalı seçin.", color=choice(bot_globals.COLORS_UNOG))

        verificationChannel = bot_globals.Server_Unog.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION)
        welcomeChannel = bot_globals.Server_Unog.get_channel(bot_globals.TEXTCHANNELID_WELCOME)
        verificationPanelChannel = bot_globals.Server_Unog.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION_PANEL)

        memberRole = bot_globals.Server_Unog.get_role(bot_globals.ROLEID_MEMBER)
        approverRole = bot_globals.Server_Unog.get_role(bot_globals.ROLEID_APPROVER)

        if not verificationPanelChannel:
            embed.add_field(name="Onay Paneli Kanalı", value="Ayarlanmamış")
        else:
            embed.add_field(name="Onay Paneli Kanalı",value="<#" + str(verificationPanelChannel.id) + ">")
        
        if not welcomeChannel:
            embed.add_field(name="Hoşgeldin Kanalı", value="Ayarlanmamış")
        else:
            embed.add_field(name="Hoşgeldin Kanalı",value="<#" + str(welcomeChannel.id) + ">")

        if not verificationChannel:
            embed.add_field(name="Onay Kanalı", value="Ayarlanmamış")
        else:
            embed.add_field(name="Onay Kanalı",value="<#" + str(verificationChannel.id) + ">")

        if not approverRole:
            embed.add_field(name="Alım Sorumlusu Rolü", value="Ayarlanmamış")
        else:
            embed.add_field(name="Alım Sorumlusu Rolü", value="<@&" + str(approverRole.id) + ">")
        
        if not memberRole:
            embed.add_field(name="Onaylı Üye Rolü", value="Ayarlanmamış")
        else:
            embed.add_field(name="Onaylı Üye Rolü", value="<@&" + str(memberRole.id) + ">")
        

        
        
        
        async def set_verification_panel_channel(interaction : Interaction):
            await interaction.response.send_message("Onay Paneli kanalını seçin:", ephemeral=True, delete_after=180,view=View().add_item(VerificationPanelChannelSelect()))

        async def reset_verification_panel_channel(interaction : Interaction):
            bot_globals.TEXTCHANNELID_VERIFICATION_PANEL = int(os.getenv('TEXTCHANNELID_VERIFICATION_PANEL'))
            await interaction.response.send_message(f"Onay Paneli kanalı sıfırlandı => <#{bot_globals.TEXTCHANNELID_VERIFICATION_PANEL}>", ephemeral=True, delete_after=10)

        async def set_verification_channel(interaction : Interaction):
            await interaction.response.send_message("Onay kanalını seçin:", ephemeral=True, delete_after=180,view=View().add_item(VerificationChannelSelect()))
        
        async def reset_verification_channel(interaction : Interaction):
            bot_globals.TEXTCHANNELID_VERIFICATION = int(os.getenv('TEXTCHANNELID_VERIFICATION'))
            await interaction.response.send_message(f"Onay kanalı sıfırlandı => <#{bot_globals.TEXTCHANNELID_VERIFICATION_PANEL}>", ephemeral=True, delete_after=10)

        async def set_welcome_channel(interaction : Interaction):
            await interaction.response.send_message("Hoşgeldin kanalını seçin:", ephemeral=True, delete_after=180,view=View().add_item(WelcomeChannelSelect()))
        
        async def reset_welcome_channel(interaction : Interaction):
            bot_globals.TEXTCHANNELID_WELCOME = int(os.getenv("TEXTCHANNELID_WELCOME"))
            await interaction.response.send_message(f"Hoşgeldin kanalı sıfırlandı => <#{bot_globals.TEXTCHANNELID_VERIFICATION_PANEL}>", ephemeral=True, delete_after=10)



        async def set_member_role(interaction : Interaction):
            await interaction.response.send_message("Üye rolünü seçin.", ephemeral=True, delete_after=180,view=View().add_item(MemberRoleSelect()))

        async def reset_member_role(interaction : Interaction ):
            bot_globals.ROLEID_MEMBER = int(os.getenv("ROLEID_MEMBER"))
            await interaction.response.send_message("Üye rolü sıfırlandı.", ephemeral=True, delete_after=30)

        async def set_approver_role(interaction : Interaction):
            await interaction.response.send_message("Alım Sorumlusu rolünü seçin.", ephemeral=True, delete_after=180,view=View().add_item(ApproverRoleSelect()))

        async def reset_approver_role(interaction : Interaction ):
            bot_globals.ROLEID_APPROVER = os.getenv("ROLEID_APPROVER")
            await interaction.response.send_message(f"Alım Sorumlusu rolü sıfırlandı => <@&{bot_globals.ROLEID_APPROVER}>", ephemeral=True, delete_after=30)
        
        view = View()
        button1 = Button(style=ButtonStyle.green, label="Onay Paneli Kanalını Seç", custom_id="setVerificationPanelChannel",row=0)
        button2 = Button(style=ButtonStyle.gray, label="Onay Paneli Kanalını Sıfırla", custom_id="resetVerificationPanelChannel",row=0)

        button3 = Button(style=ButtonStyle.green, label="Onay Başvuru Kanalını Seç", custom_id="setVerificationChannel",row=1)
        button4 = Button(style=ButtonStyle.gray, label="Onay Başvuru Kanalını Sıfırla", custom_id="resetVerificationChannel",row=1)

        button5 = Button(style=ButtonStyle.green, label="Hoşgeldin Kanalını Seç", custom_id="setWelcomeChannel",row=2)
        button6 = Button(style=ButtonStyle.gray, label="Hoşgeldin Kanalını Sıfırla", custom_id="resetWelcomeChannel",row=2)


        button7 = Button(style=ButtonStyle.green, label="Alım Sorumlusu Rolünü Seç", custom_id="setApproverRole",row=3)
        button8 = Button(style=ButtonStyle.gray,label="Alım Sorumlusu Rolünü Sıfırla", custom_id="resetApproverRole",row=3)

        button9 = Button(style=ButtonStyle.green, label="Onaylı Rolünü Seç", custom_id="give",row=4)
        button10 = Button(style=ButtonStyle.gray, label="Onaylı Rolünü Sıfırla", custom_id="givedel", row=4)

        button1.callback = set_verification_panel_channel
        button2.callback = reset_verification_panel_channel

        button3.callback = set_verification_channel
        button4.callback = reset_verification_channel

        button5.callback = set_welcome_channel
        button6.callback = reset_welcome_channel

        button7.callback = set_approver_role
        button8.callback = reset_approver_role

        button9.callback = set_member_role
        button10.callback = reset_member_role

        view.add_item(button1)
        view.add_item(button2)
        view.add_item(button3)
        view.add_item(button4)
        view.add_item(button5)
        view.add_item(button6)
        view.add_item(button7)
        view.add_item(button8)
        view.add_item(button9)
        view.add_item(button10)
        

        await interctn.response.send_message("", view=view, embed=embed, ephemeral=True, delete_after=180)

    @bot_instance.tree.command(name="butonları_yenile", description="Aktif butonları yeniler.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_has_top_access)
    async def refresh_active_buttons(interaction: Interaction):
        if not check_is_botdev(interaction):
            await reply_no_permission(interaction)
            return

        await actives()
        await interaction.response.send_message('Butonlar yenilendi.', ephemeral=True, delete_after=30)

    @bot_instance.tree.command(name="excell", description="ÜNOG veritabanını excel dosyası olarak çıkarır ve günceller.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_has_top_access)
    async def excell(interaction: Interaction):

        if not check_is_botdev(interaction):
            await reply_no_permission(interaction)
            return
        
        members = bot_globals.TABLE_MEMBERS.all()
        wb = Workbook()
        ws = wb.active
        ws.append(['İsim', 'E-mail', 'Doğum Tarihi', 'info1', "info2", 'Kayıtlı mı?', 'Üye Bilgisi', 'ID', "Ret Sebebi",
                   "Reddeden"])
        for member in members:
            if "ret sebebi" in str(member):
                ws.append([member['name'], member['email'], member['birthday'], member['info1'], member['info2'],
                           member['inserver'], member['memberinfo'], member['id'], member["ret sebebi"],
                           member["reddeden"]])
            else:
                ws.append([member['name'], member['email'], member['birthday'], member['info1'], member['info2'],
                           member['inserver'], member['memberinfo'], member['id']])
        wb.save('members.xlsx')

        attach = File('members.xlsx')

        await interaction.response.send_message('Excell dosyası oluşturuldu/güncellendi.', ephemeral=True, delete_after=180, file=attach)

    @bot_instance.tree.command(name="jam-yarat", description="Yeni bir jam oluştur.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(jam_kısa_adı="Jam'in kısa adı (örn: GGJ26)",jam_tam_adı="Jam'in uzun yazımı (örn: Global Game Jam 2026)",baslangic_timestamp="Başlangıç tarihinin Unix kodu",bitis_timestamp="Bitiş tarihinin Unix kodu",jam_url="Jam sayfasının url adresi")
    @app_commands.check(check_is_jam_mod)
    async def jam_create(interaction: Interaction, jam_kısa_adı: str,jam_tam_adı : str,baslangic_timestamp : int,bitis_timestamp: int,jam_url : str):
        
        guild: Guild = interaction.guild

        jam_kısa_adı = jam_kısa_adı.upper().strip()
        jam_tam_adı = jam_tam_adı.strip().title()

        jamData = bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")

        if jamData:
            raise JamAlreadyPresent()
        
        bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.truncate()
        bot_globals.TABLE_JAM_CURRENT_TEAMS.truncate()

        category: CategoryChannel = await guild.create_category(jam_kısa_adı)
        voiceChannel = await guild.create_voice_channel(name=f"{jam_kısa_adı} Sohbet", category=category)
        textChannel = await guild.create_text_channel(str.lower(f"{jam_kısa_adı} genel").replace(" ", "-"), category=category)
        
        participantRole : Role = await guild.create_role(name=jam_kısa_adı + " Katılımcısı")
        jammerRole : Role = await guild.create_role(name=jam_kısa_adı + " Jammer")

        bot_globals.TABLE_JAM_CURRENT.insert({
        '_type':"meta",
        'shortName': jam_kısa_adı,
        'longName': jam_tam_adı,
        'categoryID': category.id,
        'generalTextChannelID': textChannel.id,
        'generalVoiceChannelID': voiceChannel.id,
        'participantRoleID': participantRole.id,
        'jammerRoleID': jammerRole.id,
        'startUnix': baslangic_timestamp,
        'endUnix': bitis_timestamp,
        'url': jam_url
    })

        await interaction.response.send_message(
            "Jam: **" + jam_tam_adı + "** başarıyla yaratıldı.",
            ephemeral=True, delete_after=30)

    @bot_instance.tree.command(name="jam-bitir", description="Mevcut jam'i bitirir.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_jam_mod)
    async def jam_end(interaction : Interaction):
        jamData = bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")

        if not jamData:
            raise NoJamPresent()

        for i in interaction.guild.categories:
            if i.id == jamData.categoryID:
                for j in i.channels:
                    await interaction.guild._remove_channel(j)
                interaction.guild._remove_channel(i)
                break
        
        bot_globals.TABLE_JAM_CURRENT.truncate()
        bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.truncate()
        bot_globals.TABLE_JAM_CURRENT_TEAMS.truncate()

        await interaction.response.send_message("Jam başarıyla bitirildi.",ephemeral=True, delete_after=30)

    @bot_instance.tree.command(name="jam-katıl", description="Mevcut jame katılırsınız.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_member)
    async def jam_join(interaction : Interaction):

        currentJam = bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")
        participantData = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.contains(Query().discordID == interaction.user.id)
        jamParticipantRoleID : int = currentJam.participantRoleID

        if not currentJam:
            raise NoJamPresent()

        elif participantData:
            raise JamAlreadyParticipating()
        
        bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.insert({'discordID':interaction.user.id,'teamID':-1})
        await interaction.user.add_roles(jamParticipantRoleID)

    @bot_instance.tree.command(name="jam-takım-kur", description="Katıldığınız jamde ekip kurarsınız.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(ekip_adi="Lideri olacağınız ekibinizin adı")
    @app_commands.check(check_can_create_jam_team)
    async def jam_create_team(interaction : Interaction, ekip_adi : str ):

        ekip_adi = ekip_adi.strip().lower()
        currentJam = bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")
        participantData = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.contains(Query().discordID == interaction.user.id)
        teamData = bot_globals.TABLE_JAM_CURRENT_TEAMS.contains(Query().teamName == ekip_adi)

        if not currentJam:
            raise NoJamPresent()

        elif not participantData:
            raise JamNotParticipating()

        elif teamData:
            raise JamTeamAlreadyPresent()
        
        bot_globals.TABLE_JAM_CURRENT_TEAMS.insert({
        'teamName': ekip_adi,
        'gameURL': "",
        'submitted': False,
        'leader': interaction.user.id,
        'members': []
        })

    @bot_instance.tree.command(name="jam-takımları-kur", description="Jam takımlarını oluştur.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(teams=".csv formatında takımların dosyası")
    @app_commands.check(check_is_jam_mod)
    async def jam_set_teams(interaction: Interaction, teams: Attachment):
        jamData = bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")

        if not jamData:
            raise NoJamPresent()
         
        file_bytes = await teams.read()
        data = json.loads(file_bytes.decode("utf-8"))
        category : CategoryChannel = interaction.guild.get_channel(jamData.categoryID)
        if isinstance(data, dict):
            for key, item in data.items():
                await interaction.guild.create_voice_channel(name=key, category=category)

        await interaction.response.send_message("Takımlar başarıyla oluşturuldu.", ephemeral=True, delete_after=30)

    @bot_instance.tree.command(name="jam-terfi", description="Oyun sayfası eklenmiş olan ekiplerin/soloları terfi eder.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(category="Jam'in bulunduğu Kategori Kanalı", teams=".csv formatında takımların dosyası")
    @app_commands.check(check_is_jam_mod)
    async def jam_set_teams(interaction: Interaction, category: CategoryChannel, teams: Attachment):
        file_bytes = await teams.read()
        data = json.loads(file_bytes.decode("utf-8"))
        if isinstance(data, dict):
            for key, item in data.items():
                await interaction.guild.create_voice_channel(name=key, category=category)

        await interaction.response.send_message("Takımlar başarıyla oluşturuldu.", ephemeral=True, delete_after=30)

    @bot_instance.tree.command(name="onayla", description="Kullanıcıyı manuel onaylar.", guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(user="Onaylanan kullanıcı",usernick="Yeni İsmi")
    @app_commands.check(check_is_approver)
    async def approve_manually(interaction: Interaction, user: Member,usernick : str):
        
        IsUserMember : bool = False
        for i in user.roles:
            if i.id == bot_globals.ROLEID_MEMBER:
                IsUserMember = True

        if not IsUserMember:
            await user.add_roles(bot_globals.ROLEID_MEMBER)
            if usernick:
                await user.edit(nick=usernick)
        else:
            interaction.response.send_message("Kullanıcı zaten onaylı",ephemeral=True,delete_after=30)
            return

        bot_globals.TABLE_MEMBERS.update({'inserver': 'yes'}, Query().id == user.id)

        embed = Embed(title=f"Onaylandı!", color=choice(bot_globals.COLORS_UNOG))
        embed.add_field(name="\u200b", value=f"<@{user.id}>", inline=False)
        embed.set_thumbnail(url=user.avatar)

        await interaction.response.send_message(embed=embed)

        await welcome_member_message(interaction.guild, user)

    @bot_instance.tree.command(name="onay_kayıt_butonu_yarat", description="Girilen kanalda onay kayıt butonu oluşturur.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(description="Mesaj için metin girin.")
    @app_commands.check(check_has_top_access)
    async def create_verification_application_button(interaction: Interaction, description: str = None):
        
        verificationChannel = bot_globals.UnogBot.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION)
        
        if not verificationChannel:
            await interaction.response.send_message('Önce kayıt kanalını ayarlamalısınız.', ephemeral=True, delete_after=30)
            return

        view = View(timeout=None)

        async def send_modal(interaction : Interaction):

            if bot_globals.Server_Unog.get_role(bot_globals.ROLEID_MEMBER) in interaction.user.roles:
                await interaction.response.send_message("Sistemimizde onaylı gözüküyorsunuz, bir hata durumunda Direktörlerimize ulaşabilirsiniz.", ephemeral=True, delete_after=10)
                return
            await interaction.response.send_modal(ApprovalModal(denyCallback=deny_by_application,approveCallback=approve_by_application))

        button1 = Button(style=ButtonStyle.primary, label="Onay Talebi İçin Tıkla!", custom_id="modal")
        button1.callback = send_modal
        view.add_item(button1)

        message = await interaction.channel.send(description, view=view)

async def approve_by_application(interaction : Interaction):
    if check_is_approver(interaction):
        print(interaction.message.embeds[0].fields[0].value) 
        #await interaction.message.add_reaction('') #:white_check_mark:
        view = interaction.message.view
        for item in view.children:
            item.disabled = True
        embed = Embed(title="Onaylandı! :white_check_mark:",description=f"{interaction.message.embeds[0].description.split()[0]}")
        embed.add_field(name="Onaylayan",value=f"<@{interaction.user.id}>")
        await interaction.response.send_message("",embed=embed)
    #    bot_globals.TABLE_APPROVES.upsert({'name': nameFormat ,'email': self.email.value, 'birthday': self.birthday.value, 'info1': self.info1.value, 'info2': self.info2.value, 'inserver': 'no', 'memberinfo': 'no', 'id': interaction.user.id}, Query().id == interaction.user.id)
def deny_by_application(interaction : Interaction):
    return
        

