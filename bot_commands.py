import discord
import json
import os
from random import choice
from discord.ui import View,Button
from discord import Embed,File,Attachment,ButtonStyle,Interaction,Member,Role,Guild,CategoryChannel,Object,PermissionOverwrite
from discord.ext.commands import Context,Bot,check
from openpyxl import Workbook
from tinydb import Query
from tinydb.table import Document
import bot_globals
from bot_views import ApproverRoleSelect, MemberRoleSelect, VerificationChannelSelect, VerificationPanelChannelSelect, WelcomeChannelSelect, ApprovalApplyButtonView
from discord.app_commands.checks import has_any_role,has_role
from discord import app_commands
from bot_actions import add_participant_to_jam_team, approvalForm_applyButton_interaction,approve_user, create_jam_team, remove_participant_from_jam_team,submit_jam_project
from bot_exceptions import reply_no_permission,UserIsNull,JamAlreadyPresent,JamAlreadyParticipating,JamTeamAlreadyPresent,JamNotPresent,JamNotParticipating,UserNotApprover,UserAlreadyVerified,UserNotJamTeamLeader
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

    @bot_instance.tree.command(name="veritabanı-guncelle", description="ÜNOG veritabanında gerekli olan migration'ları çağırır, veritabanını düzeltir.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_botdev)
    async def migrate_database(interaction: Interaction):

        await interaction.response.defer(ephemeral=True)

        for doc in bot_globals.TABLE_MEMBERS:
            if "memberinfo" in doc:
                bot_globals.TABLE_MEMBERS.update(
                    lambda d: d.pop("memberinfo", None),
                    doc_ids=[doc.doc_id]
                )
            if "ret sebebi" in doc:
                bot_globals.TABLE_MEMBERS.update(lambda d: d.pop("ret sebebi", None),doc_ids=[doc.doc_id])
            if "reddeden" in doc:
                bot_globals.TABLE_MEMBERS.update(lambda d: d.pop("reddeden", None),doc_ids=[doc.doc_id])
            if "inserver" in doc:
                if doc.get('inserver') == "no":
                    bot_globals.TABLE_MEMBERS.remove(doc_ids=[doc.doc_id])
                else:
                    bot_globals.TABLE_MEMBERS.update(lambda d: d.pop("inserver", None),doc_ids=[doc.doc_id])
        await interaction.followup.send(
        "Veritabanı migrasyonu başarıyla yapıldı. ✅",
        ephemeral=True
        )

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
                        description=aciklama,
                        url=jam_url)

        bot_globals.TABLE_JAM_CURRENT.insert(jam)

        await interaction.response.send_message(
            "Jam: **" + jam_tam_adı + "** başarıyla yaratıldı.",
            ephemeral=True)

    @bot_instance.tree.command(name="jam-bilgi", description="Mevcut jamle ilgili tüm bilgileri gösterir.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_member)
    async def jam_info(interaction : Interaction):
        jamRawData = is_jam_present()
        participant = is_user_in_jam(interaction.user)
        string_teaminfo : str = ""
        if participant:
            jam_team_doc = is_user_in_jam_team(interaction.user)
            string_teaminfo = "**Bu jam'de bulunuyorsunuz.** ✅ \n\n **Ekibiniz:** "
            if jam_team_doc:
                jam_team : JamTeam = JamTeam(mapping=jam_team_doc)
                string_teaminfo += f"<#{jam_team.voiceChannelID}>\n"
                participant_leader = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(doc_id=jam_team.leader)
                string_teaminfo += f"**Ekip Lideri:** <@{participant_leader.get('discordID')}>\n"
                string_teaminfo += "**Ekip Üyeleri:**\n"
                for item in jam_team.members:
                    string_teaminfo += f"<@{bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(doc_id=item).get('discordID')}>\n"
            else:
                string_teaminfo += "Yok ❌"
                    
        else:
            string_teaminfo = "Bu jam'de bulunmuyorsunuz. ❌"

        embed : Embed = None
        if jamRawData:
            jamData : Jam = Jam(mapping=jamRawData)
            embed = Embed(title=jamData.longName + " 🕹",
                          color=choice(bot_globals.COLORS_UNOG),
                          description=jamData.description + f"\n\n{string_teaminfo}")
            embed.add_field(name="🏁 Başlangıç Zamanı:",value=f"<t:{jamData.startUnix}>")
            embed.add_field(name='🚩 Bitiş Zamanı:',value=f"<t:{jamData.endUnix}>")
            embed.add_field(name='👤 Katılımcı Rolü:',value=f"<@&{jamData.participantRoleID}>")
            embed.add_field(name='🌏 Web Adresi:',value=jamData.url)
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            raise JamNotPresent()

    @bot_instance.tree.command(name="jam-yardım", description="Mevcut jame katılırsınız.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_member)
    async def jam_help(interaction : Interaction):
        embed : Embed = Embed(title="Jam Komutları",description="Aşağıda Jamle ilgili bütün komutların açıklamaları bulunmaktadır.",color=choice(bot_globals.COLORS_UNOG))
        embed.add_field(name="/jam-bilgi",value="Mevcut jamle ilgili tüm bilgileri gösterir.")
        embed.add_field(name="/jam-katıl",value="Mevcut jame katılırsınız.")
        #embed.add_field(name="/jam-yarat",value=f"**Kullanabilen Roller:**<@&{bot_globals.ROLEID_DIRECTOR}>, <@&{bot_globals.ROLEID_JAM_MOD}>\nYeni bir jam oluşturur.\nHerhangi bir anda sadece bir tane jam bulunabilir.")
        #embed.add_field(name="/jam-ekipleri-ekle",value=f"**Kullanabilen Roller:**<@&{bot_globals.ROLEID_DIRECTOR}>, <@&{bot_globals.ROLEID_JAM_MOD}>\nMevcut jame dışarıdan ekip bilgilerini ekler.\nEklenilen dosyanın .csv formatında olması gerekir.")
        embed.add_field(name="/jam-ekip-kur",value=f"**Jam'e katılan her üye kullanabilir**\nKatıldığınız jamde bir ekip oluşturur.\nBir jamde her katılımcının bir ekipte bulunması gerekir")
        #embed.add_field(name="/jam-bitir",value=f"Kullanabilen Roller:<@&{bot_globals.ROLEID_DIRECTOR}>, <@&{bot_globals.ROLEID_JAM_MOD}>\nMevcut jami bitirir ve tüm verileri silinir.\nYeni bir jam başlatılması için ilk önce jamin bitirilmesi gerekir.")
        #embed.add_field(name="/jam-terfi",value=f"Kullanabilen Roller:<@&{bot_globals.ROLEID_DIRECTOR}>, <@&{bot_globals.ROLEID_JAM_MOD}>\nMevcut jamde submission yapan ekip üyelerini terfi ederek kalıcı rol ataması yapar.\nJam'in herhangi bir esnasında kullanılabilir.")
        await interaction.response.send_message(embed=embed,ephemeral=True)
    
    @bot_instance.tree.command(name="jam-bitir", description="Mevcut jam'i bitirir, Dikkat: bütün jam verisi silinir.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_jam_mod)
    @app_commands.check(check_is_jam_present)
    async def jam_end(interaction : Interaction):
        jam_doc : Document = bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")
        jam : Jam = Jam(mapping=jam_doc)
        categoryID : int = jam_doc.get('categoryID')
        for i in interaction.guild.categories:
            if i.id == categoryID:
                for j in i.channels:
                    await j.delete()
                await i.delete()
                break
        
        bot_globals.TABLE_JAM_CURRENT.truncate()
        bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.truncate()
        bot_globals.TABLE_JAM_CURRENT_TEAMS.truncate()
        bot_globals.TABLE_JAM_FORMS.truncate()
        role_participant : Role = await interaction.guild.get_role(jam.participantRoleID)
        await role_participant.delete()
        await interaction.response.send_message("Jam başarıyla bitirildi.",ephemeral=True)

    @bot_instance.tree.command(name="jam-katıl", description="Mevcut jame katılırsınız.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_member)
    @app_commands.check(check_can_user_join_jam)
    async def jam_join(interaction : Interaction):

        currentJam : Jam = Jam(mapping=bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta"))
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

        participant = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == interaction.user.id)
        
        team_id : int = await create_jam_team(ekip_adi)
        await add_participant_to_jam_team(participant_id=participant.doc_id,team_id=team_id)

        await interaction.response.send_message(f"Ekip: {ekip_adi} başarıyla oluşturuldu. ✅\n Artık oluşturacağınız bu ekibe katılım isteklerini yollatabilirsiniz.\n**Not:** Ekibinizle ilgili komutları ekibinizin ses kanalında çağırmanız gerekir.",ephemeral=True)

    @bot_instance.tree.command(name="jam-ekipten-çık", description="Bulunduğunuz jam ekibinden çıkış yaparsınız.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_member)
    async def jam_leave_team(interaction : Interaction):
        participant_doc = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == interaction.user.id)
        if participant_doc:
            await remove_participant_from_jam_team(participant_doc.doc_id,True,interaction=interaction)

    @bot_instance.tree.command(name="jam-ekibe-katıl", description="Yazdığınız ekibe katılma isteği gönderir.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(ekip_adi="Katılacağınız ekibinizin adı")
    @app_commands.check(check_is_member)
    @app_commands.check(check_can_user_create_jam_team)
    async def jam_join_team(interaction : Interaction, ekip_adi : str ):
        ekip_adi = ekip_adi.strip().lower().replace(" ","-")
        participant_doc = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == interaction.user.id)
        targetTeamDoc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(Query().teamName == ekip_adi)
        if targetTeamDoc is not None:
            targetTeam : JamTeam = JamTeam(mapping=targetTeamDoc)
            voiceChannel = interaction.guild.get_channel(targetTeam.voiceChannelID)
            if participant_doc.doc_id in targetTeam.joinRequests:
                await interaction.response.send_message("Bu ekibe bir istek zaten gönderdiniz, kabul edilmesi için ekip üyeleriyle iletişime geçebilirsiniz.",ephemeral=True)
                return
            else:
                await voiceChannel.send(f"Hey! {interaction.user.mention} isimli kullanıcı ekibinize katılmak istiyor.\n\n Kabul etmek için X komutunu kullanabilirsiniz.")
                targetTeam.joinRequests.append(participant_doc.doc_id)
                bot_globals.TABLE_JAM_CURRENT_TEAMS.update({'joinRequests':targetTeam.joinRequests},doc_ids=[targetTeamDoc.doc_id])
                await interaction.response.send_message(f"**{ekip_adi}** Ekibine davetiyeniz başarıyla gönderildi!",ephemeral=True)
        else:
            #raise JamTeamNotPresent(team_name)
            await interaction.response.send_message("Bu isimde bir ekip bulunmuyor, ekip adını doğru yazdığınızdan emin olun.",ephemeral=True,delete_after=20)

    @bot_instance.tree.command(name="jam-isteği-kabul-et", description="Yazdığınız ekibe katılma isteği gönderir.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(kullanici_adi="İstek yollayan kullanıcının discord adı (örn:.krenel)")
    @app_commands.check(check_is_member)
    async def jam_accept_invitation(interaction : Interaction, kullanici_adi : str ):
        kullanici_adi = kullanici_adi.strip()
        invoker_participant_doc = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == interaction.user.id)
        target_member = bot_globals.Server_Unog.get_member_named(kullanici_adi)
        target_participant_doc = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == target_member.id)
        team_doc : Document = is_user_in_jam_team(interaction.user)
        if team_doc:
            if invoker_participant_doc:
                if target_participant_doc:
                    if team_doc.get("leader") == invoker_participant_doc.doc_id:
                        team = JamTeam(mapping=team_doc)
                        if target_participant_doc.doc_id in team.joinRequests:
                            team.joinRequests.remove(target_participant_doc.doc_id)
                            bot_globals.TABLE_JAM_CURRENT_TEAMS.update({'joinRequests':team.joinRequests},doc_ids=[team_doc.doc_id])
                            await add_participant_to_jam_team(target_participant_doc.doc_id,team_doc.doc_id,True)
                            return
        raise NotImplementedError()

    @bot_instance.tree.command(name="jam-ekipleri-ekle", description="Jam takımlarını içe aktarır.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(teams=".csv formatında takımların dosyası")
    @app_commands.check(check_is_jam_mod)
    @app_commands.check(check_is_jam_present)
    async def jam_set_teams(interaction: Interaction, teams: Attachment):
        await ImporterGGJ26.run(interaction,teams)

    @bot_instance.tree.command(name="jam-ekip-submit", description="Ekibinizle bitmiş jam oyununuzu yollarsınız. (Sadece Ekip Lideri kullanabilir)",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(submission_url="Bitmiş oyununuzun URL'si.")
    @app_commands.check(check_is_member)
    async def jam_team_submit(interaction : Interaction,submission_url : str):
        participant_doc = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == interaction.user.id)
        if participant_doc:
            team_doc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(Query().leader == participant_doc.doc_id)
            if team_doc:
                submit_jam_project(team_doc.doc_id,submission_url)
                await interaction.response.send_message("Başarılı!",ephemeral=True,delete_after=15)
            else:
                raise UserNotJamTeamLeader()
        else:
            raise JamNotParticipating()

    @bot_instance.tree.command(name="jam-terfi", description="Oyun sayfası eklenmiş olan ekipleri terfi eder ve Jammer rolünü ekler.",guild=bot_globals.GUILD_UNOG)
    @app_commands.check(check_is_jam_mod)
    @app_commands.check(check_is_jam_present)
    async def jam_rank_teams(interaction: Interaction):
        pass
#endregion

        

