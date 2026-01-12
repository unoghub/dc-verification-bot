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
from bot_views import ApproverRoleSelect, MemberRoleSelect, VerificationChannelSelect, VerificationPanelChannelSelect, WelcomeChannelSelect, ApprovalApplyButtonView
from discord.app_commands.checks import has_any_role,has_role
from discord import app_commands
from bot_actions import approvalForm_applyButton_interaction,approve_user
from bot_exceptions import reply_no_permission,UserIsNull,JamAlreadyPresent,JamAlreadyParticipating,JamTeamAlreadyPresent,JamNotPresent,JamNotParticipating,UserNotApprover,UserAlreadyVerified
from bot_conditions import check_can_user_create_jam_team, check_can_user_join_jam, check_is_approver,check_is_jam_mod,check_is_botdev, check_is_jam_present,check_is_member,check_has_top_access, check_is_no_jam_present, is_user_member,is_jam_present,is_user_in_jam,is_user_in_jam_team
from bot_events import actives
from bot_models import Jam, JamParticipant, JamTeam
from importer_ggj26 import ImporterGGJ26

def setup_commands(bot_instance: Bot):
#region verification_commands
    @bot_instance.tree.command(name="indir_veritabanı",guild=bot_globals.GUILD_UNOG,description="ÜNOG Veritabanını JSON olarak indirir ve günceller.")
    @app_commands.check(check_has_top_access)
    async def dbjson(interaction: Interaction):
        file = File("unog.json")
        await interaction.response.send_message("ÜNOG veritabanı oluşturuldu/güncellendi.",file=file,ephemeral=True)

    @bot_instance.tree.command(name="ayarlar",description="Bot ayarları panelini aç.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_has_top_access)
    async def botSettings(interaction: Interaction):

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
        

        await interaction.response.send_message("", view=view, embed=embed, ephemeral=True, delete_after=180)

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

    @bot_instance.tree.command(name="onayla", description="Kullanıcıyı manuel onaylar.", guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(target_user="Onaylanan kullanıcı",usernick="Yeni İsmi")
    @app_commands.check(check_is_approver)
    async def approve_manually(interaction: Interaction, target_user: Member,usernick : str):

        if target_user is None:
            raise UserIsNull()
        if not is_user_member(target_user):
            await approve_user(interaction.user,target_user,usernick)
        else:
            raise UserAlreadyVerified()

    @bot_instance.tree.command(name="onay_kayıt_butonu_yarat", description="Girilen kanalda onay kayıt butonu oluşturur.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_has_top_access)
    async def create_verification_application_button(interaction: Interaction):
        
        verificationChannel = bot_globals.UnogBot.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION)
        
        if not verificationChannel:
            await interaction.response.send_message('Önce kayıt kanalını ayarlamalısınız.', ephemeral=True, delete_after=15)
            return

        view = ApprovalApplyButtonView()
        view.children[0].callback = approvalForm_applyButton_interaction

        await interaction.channel.send("", view=view)
#endregion

#region jam_commands
    @bot_instance.tree.command(name="jam-yarat", description="Yeni bir jam oluştur.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(jam_kısa_adı="Jam'in kısa adı (örn: GGJ26)",jam_tam_adı="Jam'in uzun yazımı (örn: Global Game Jam 2026)",baslangic_timestamp="Başlangıç tarihinin Unix kodu",bitis_timestamp="Bitiş tarihinin Unix kodu",jam_url="Jam sayfasının url adresi",aciklama="Jam'in kısa açıklaması.")
    @app_commands.check(check_is_jam_mod)
    @app_commands.check(check_is_no_jam_present)
    async def jam_create(interaction: Interaction, jam_kısa_adı: str,jam_tam_adı : str,baslangic_timestamp : int,bitis_timestamp: int,jam_url : str,aciklama : str = None):
        
        guild: Guild = interaction.guild
        jam_kısa_adı = jam_kısa_adı.upper().strip()
        jam_tam_adı = jam_tam_adı.strip().title()

        category: CategoryChannel = await guild.create_category(jam_tam_adı)
        voiceChannel = await guild.create_voice_channel(name=f"{jam_kısa_adı} Sohbet", category=category)
        textChannel = await guild.create_text_channel(str.lower(f"{jam_kısa_adı}-genel"), category=category)
        
        participantRole : Role = await guild.create_role(name=jam_kısa_adı + " Katılımcısı")
        jammerRole : Role = await guild.create_role(name=jam_kısa_adı + " Jammer")

        jam : Jam = Jam(jam_kısa_adı,
                        jam_tam_adı,
                        startUnix=baslangic_timestamp,
                        endUnix=bitis_timestamp,
                        categoryID=category.id,
                        generalVoiceChannelID=voiceChannel.id,
                        generalTextChannelID=textChannel.id,
                        participantRoleID=participantRole.id,
                        jammerRoleID=jammerRole.id,
                        description=aciklama)

        bot_globals.TABLE_JAM_CURRENT.insert(jam)

        await interaction.response.send_message(
            "Jam: **" + jam_tam_adı + "** başarıyla yaratıldı.",
            ephemeral=True)

    @bot_instance.tree.command(name="jam-bilgi", description="Mevcut jamle ilgili tüm bilgileri gösterir.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_member)
    async def jam_info(interaction : Interaction):
        jamRawData = is_jam_present()
        embed : Embed = None
        if jamRawData:
            jamData : Jam = Jam(data=jamRawData)
            embed = Embed(title=jamData.longName + " 🕹",
                          color=choice(bot_globals.COLORS_UNOG),
                          description=jamData.description)
            embed.add_field(name="Başlangıç Zamanı:",value=f"<t:{jamData.startUnix}:d>")
            embed.add_field(name='Bitiş Zamanı:',value=f"<t:{jamData.endUnix}:d>")
            embed.add_field(name='Katılımcı Rolü:',value=f"<@&{jamData.participantRoleID}>")
            embed.add_field(name='Web Adresi:',value=jamData.url)
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            raise JamNotPresent()

    @bot_instance.tree.command(name="jam-yardım", description="Mevcut jame katılırsınız.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_member)
    async def jam_help(interaction : Interaction):
        embed : Embed = Embed(title="Jam Komutları",description="Aşağıda Jamle ilgili bütün komutların açıklamaları bulunmaktadır.",color=choice(bot_globals.COLORS_UNOG))
        embed.add_field(name="/jam-bilgi",value="Mevcut jamle ilgili tüm bilgileri gösterir.")
        embed.add_field(name="/jam-yarat",value=f"**Kullanabilen Roller:**<@&{bot_globals.ROLEID_DIRECTOR}>, <@&{bot_globals.ROLEID_JAM_MOD}>\nYeni bir jam oluşturur.\nHerhangi bir anda sadece bir tane jam bulunabilir.")
        embed.add_field(name="/jam-ekipleri-ekle",value=f"**Kullanabilen Roller:**<@&{bot_globals.ROLEID_DIRECTOR}>, <@&{bot_globals.ROLEID_JAM_MOD}>\nMevcut jame dışarıdan ekip bilgilerini ekler.\nEklenilen dosyanın .csv formatında olması gerekir.")
        embed.add_field(name="/jam-ekip-kur",value=f"**Jam'e katılan her üye kullanabilir**\nKatıldığınız jamde bir ekip oluşturur.\nBir jamde her katılımcının bir ekipte bulunması gerekir")
        embed.add_field(name="/jam-bitir",value=f"Kullanabilen Roller:<@&{bot_globals.ROLEID_DIRECTOR}>, <@&{bot_globals.ROLEID_JAM_MOD}>\nMevcut jami bitirir ve tüm verileri silinir.\nYeni bir jam başlatılması için ilk önce jamin bitirilmesi gerekir.")
        embed.add_field(name="/jam-bitir",value=f"Kullanabilen Roller:<@&{bot_globals.ROLEID_DIRECTOR}>, <@&{bot_globals.ROLEID_JAM_MOD}>\nMevcut jamde submission yapan ekip üyelerini terfi ederek kalıcı rol ataması yapar.\nJam'in herhangi bir esnasında kullanılabilir.")
        await interaction.response.send_message(embed=embed,ephemeral=True)
    
    @bot_instance.tree.command(name="jam-bitir", description="Mevcut jam'i bitirir, Dikkat: bütün jam verisi silinir.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_jam_mod)
    @app_commands.check(check_is_jam_present)
    async def jam_end(interaction : Interaction):
        jamData = bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")
        categoryID : int = jamData.get('categoryID')
        for i in interaction.guild.categories:
            if i.id == categoryID:
                for j in i.channels:
                    await j.delete()
                await i.delete()
                break
        
        bot_globals.TABLE_JAM_CURRENT.truncate()
        bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.truncate()
        bot_globals.TABLE_JAM_CURRENT_TEAMS.truncate()

        await interaction.response.send_message("Jam başarıyla bitirildi.",ephemeral=True)

    @bot_instance.tree.command(name="jam-katıl", description="Mevcut jame katılırsınız.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_member)
    @app_commands.check(check_can_user_join_jam)
    async def jam_join(interaction : Interaction):

        currentJam : Jam = Jam(data=bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta"))
        jamParticipantRoleID : int = currentJam.participantRoleID
        jamParticipantRole : Role = interaction.guild.get_role(jamParticipantRoleID)



        bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.insert(JamParticipant(discordID=interaction.user.id))
        await interaction.user.add_roles(jamParticipantRole)
        embed = Embed(title="Başarılı! ✅",color=choice(bot_globals.COLORS_UNOG),description=f"{currentJam.longName} jamine katıldınız. \n\n Şimdi `/jam-ekip-kur <ekipAdı>` veya,\n `/jam-ekibe-katıl <ekipAdı>`komutuyla solo/ekip fark etmeksizin bir ekip oluşturup etkinliğe hazırlanabilirsiniz.\n\n Sıkıştığınız durumlarda `/jam-yardım` komutuyla her komutun detaylı açıklamasına ulaşabilirsiniz.")
        await interaction.response.send_message("",embed=embed,ephemeral=True)

    @bot_instance.tree.command(name="jam-ekip-kur", description="Katıldığınız jamde ekip kurarsınız.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(ekip_adi="Lideri olacağınız ekibinizin adı")
    @app_commands.check(check_is_member)
    @app_commands.check(check_can_user_create_jam_team)
    async def jam_create_team(interaction : Interaction, ekip_adi : str ):

        ekip_adi = ekip_adi.strip().lower()
        currentJamRawData = bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")
        participantRawData = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.contains(Query().discordID == interaction.user.id)
        teamRawData = bot_globals.TABLE_JAM_CURRENT_TEAMS.contains(Query().teamName == ekip_adi)

        if not currentJamRawData:
            raise JamNotPresent()
        elif not participantRawData:
            raise JamNotParticipating()
        elif teamRawData:
            raise JamTeamAlreadyPresent()
        
        newJamTeam = JamTeam(ekip_adi,leader=interaction.user.id)

        bot_globals.TABLE_JAM_CURRENT_TEAMS.insert(newJamTeam)

        await interaction.response.send_message(f"Ek: {ekip_adi} başarıyla oluşturuldu. ✅",ephemeral=True)

    @bot_instance.tree.command(name="jam-ekipleri-ekle", description="Jam takımlarını içe aktarır.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(teams=".csv formatında takımların dosyası")
    @app_commands.check(check_is_jam_mod)
    @app_commands.check(check_is_jam_present)
    async def jam_set_teams(interaction: Interaction, teams: Attachment):
        await ImporterGGJ26.run(interaction,teams)

    @bot_instance.tree.command(name="jam-terfi", description="Oyun sayfası eklenmiş olan ekipleri terfi eder ve Jammer rolünü ekler.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_jam_mod)
    @app_commands.check(check_is_jam_present)
    async def jam_rank_teams(interaction: Interaction):
        pass
#endregion

        

