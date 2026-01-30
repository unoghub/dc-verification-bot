import io
import discord
import json
import os
from random import choice
from discord.ui import View,Button
from discord import Color, Colour, Embed,File,Attachment,ButtonStyle,Interaction,Member,Role,Guild,CategoryChannel,Object,PermissionOverwrite
from discord.ext.commands import Context,Bot,check
from openpyxl import Workbook
from tinydb import Query
from tinydb.table import Document
import bot_globals
from bot_views import ApproverRoleSelect, MemberRoleSelect, VerificationChannelSelect, VerificationPanelChannelSelect, WelcomeChannelSelect, ApprovalApplyButtonView
from discord.app_commands.checks import has_any_role,has_role
from discord import app_commands
from discord.app_commands import Group
from discord.ext import commands

from bot_actions import *
from bot_exceptions import *
from bot_conditions import *
from bot_events import actives
from bot_models import Jam, JamParticipant, JamTeam
from importer_ggj26 import ImporterGGJ26

class DirectorCog(commands.Cog):

    director = app_commands.Group(
        name="bot",
        description="Direktör Komutları.",
        guild_ids=[bot_globals.SERVERID_UNOG])

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @director.command(name="indir_veritabanı", description="ÜNOG Veritabanını JSON olarak indirir ve günceller.")
    @app_commands.check(check_has_top_access)
    async def dbjson(self, interaction: Interaction):
        file = File("unog.json")
        await interaction.response.send_message("ÜNOG veritabanı oluşturuldu/güncellendi.",file=file,ephemeral=True)

    @director.command(name="butonları_yenile", description="Aktif butonları yeniler.")
    @app_commands.check(check_has_top_access)
    async def refresh_active_buttons(self,interaction: Interaction):
        await actives()
        await interaction.response.send_message('Butonlar yenilendi.', ephemeral=True, delete_after=30)

    @director.command(name="indir_excell", description="ÜNOG veritabanını günceller ve excel dosyası olarak çıkarır.")
    @app_commands.check(check_has_top_access)
    async def excell(self,interaction: Interaction):
        members = bot_globals.TABLE_MEMBERS.all()
        wb = Workbook()
        ws = wb.active
        ws.append(['İsim', 'E-mail', 'Doğum Tarihi', 'info1', "info2", 'Discord ID'])
        for member in members:
            ws.append([member['name'], member['email'], member['birthday'], member['info1'], member['info2'],member['id']])
        wb.save('members.xlsx')

        attach = File('members.xlsx')

        await interaction.response.send_message("", ephemeral=True, file=attach)

class ApproverCog(commands.Cog):

    approver = app_commands.Group(
        name="alım",
        description="Alım Sorumlusu Komutları.",
        guild_ids=[bot_globals.SERVERID_UNOG])

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @approver.command(name="ayarlar",description="Bot ayarları panelini aç.")
    @app_commands.check(check_is_approver)
    async def botSettings(self,interaction: Interaction):

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
        
        # if not memberRole:
        #     embed.add_field(name="Onaylı Üye Rolü", value="Ayarlanmamış")
        # else:
        #     embed.add_field(name="Onaylı Üye Rolü", value="<@&" + str(memberRole.id) + ">")
        
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

        # button9 = Button(style=ButtonStyle.green, label="Onaylı Rolünü Seç", custom_id="give",row=4)
        # button10 = Button(style=ButtonStyle.gray, label="Onaylı Rolünü Sıfırla", custom_id="givedel", row=4)

        button1.callback = set_verification_panel_channel
        button2.callback = reset_verification_panel_channel

        button3.callback = set_verification_channel
        button4.callback = reset_verification_channel

        button5.callback = set_welcome_channel
        button6.callback = reset_welcome_channel

        button7.callback = set_approver_role
        button8.callback = reset_approver_role

        # button9.callback = set_member_role
        # button10.callback = reset_member_role

        view.add_item(button1)
        view.add_item(button2)
        view.add_item(button3)
        view.add_item(button4)
        view.add_item(button5)
        view.add_item(button6)
        view.add_item(button7)
        view.add_item(button8)
        # view.add_item(button9)
        # view.add_item(button10)
        
        await interaction.response.send_message("", view=view, embed=embed, ephemeral=True, delete_after=30)

    @approver.command(name="onayla", description="Kullanıcıyı manuel onaylar.")
    @discord.app_commands.describe(target_user="Onaylanan kullanıcı",usernick="Kullanıcının yeni adı")
    @app_commands.check(check_is_approver)
    async def approve_manually(self,interaction: Interaction, target_user: Member,usernick : str):
        if target_user is None:
            raise TargetUserIsNullException()
        if is_user_member(target_user):
            raise TargetUserIsAlreadyVerified()
        await approve_user(interaction.user,target_user,usernick)
        await interaction.response.send_message("İşlem başarılı!",ephemeral=True,delete_after=10)

    @approver.command(name="onay_kayıt_butonu_yarat",description="Kayıt kanalında onay kayıt butonu oluşturur.")
    @app_commands.check(check_is_approver)
    async def create_verification_application_button(self,interaction: Interaction):
        
        verificationChannel = bot_globals.UnogBot.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION)
        
        if not verificationChannel:
            await interaction.response.send_message('Önce kayıt kanalını ayarlamalısınız.', ephemeral=True, delete_after=15)
            return

        view = ApprovalApplyButtonView()
        view.children[0].callback = approvalForm_applyButton_interaction

        await verificationChannel.send("", view=view)
        await interaction.response.send_message("İşlem başarılı!",ephemeral=True,delete_after=10)

class BotdevCog(commands.Cog):

    botdev = app_commands.Group(
        name="geliştirici",
        description="Bot Geliştirici Komutları.",
        guild_ids=[bot_globals.SERVERID_UNOG])

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @botdev.command(name="veritabanı-migrate", description="ÜNOG veritabanında gerekli olan migration'ları çağırır, veritabanını düzeltir.")
    @app_commands.check(check_is_botdev)
    async def migrate_database(self,interaction: Interaction): #DONE 

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
        ephemeral=True)

class JamModCog(commands.Cog):

    jam_mod = app_commands.Group(
        name="jam_moderasyon",
        description="Jam Moderasyon Komutları.",
        guild_ids=[bot_globals.SERVERID_UNOG])

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @jam_mod.command(name="jam-yarat", description="Yeni bir jam oluştur.")
    @discord.app_commands.describe(jam_kısa_adı="Jam'in kısa adı (örn: GGJ26)",jam_tam_adı="Jam'in uzun yazımı (örn: Global Game Jam 2026)",baslangic_timestamp="Başlangıç tarihinin Unix kodu",bitis_timestamp="Bitiş tarihinin Unix kodu",jam_url="Jam sayfasının url adresi",aciklama="Jam'in kısa açıklaması.")
    @app_commands.check(check_is_jam_mod)
    async def jam_create(self,interaction: Interaction, jam_kısa_adı: str,jam_tam_adı : str,baslangic_timestamp : int,bitis_timestamp: int,jam_url : str,aciklama : str = None):
        
        check_is_no_jam_present(interaction)
        if not aciklama:
            aciklama = ""
        await create_jam(jam_kısa_adı,jam_tam_adı,baslangic_timestamp,bitis_timestamp,jam_url,aciklama)

        await interaction.response.send_message(
            "Jam: **" + jam_tam_adı.strip().title() + "** başarıyla yaratıldı.",
            ephemeral=True,delete_after=10)



    @jam_mod.command(name="jami-bitir", description="Mevcut jam'i bitirir, kabul edilen gruplar jammer olarak terfi edilir.Bütün jam verisi silinir.")
    @app_commands.check(check_is_jam_mod)
    async def jam_end(self,interaction : Interaction):
        
        check_is_jam_present(interaction)
        await interaction.response.defer()
        await delete_jam()
        await interaction.followup.send("Jam başarıyla bitirildi.",ephemeral=True)



    @jam_mod.command(name="ekipleri-içe-aktar", description="Jam katılımcılarını içe aktarır ve hepsini onaylı üye yapar.")
    @discord.app_commands.describe(teams=".csv formatında takımların dosyası")
    @app_commands.check(check_is_jam_mod)
    async def jam_import_teams(self,interaction: Interaction, teams: Attachment):
        check_is_jam_present(interaction=interaction)
        if not teams.filename.lower().endswith(".csv") or (teams.content_type.split(";")[0] not in ("text/csv", "application/vnd.ms-excel")):
            print(teams.content_type)
            raise AttachedFileIsNotCsvException()
        
        await interaction.response.defer()
        bot_globals.TABLE_JAM_FORMS.truncate()
        await ImporterGGJ26.run(interaction,teams)
        all_forms = bot_globals.TABLE_JAM_FORMS.all()
        for item in all_forms:
            member = bot_globals.Server_Unog.get_member_named(item.get('username'))
            if not member:
                continue
            if not is_user_member(member):
                await approve_user(interaction.guild.me,
                                    member,
                                    newName=item.get('name'),
                                    eMail=item.get('email'),
                                    birthday=item.get('birthday'),
                                    info2="Jam formuyla eklendim.")
            await create_jam_participant(member)
        await interaction.followup.send(
            "İçe aktarım başarılı ✅ Formda ismi sunucuda bulunabilen herkes onaylı üye yapıldı.",
            ephemeral=True
        )

    @jam_mod.command(name="üyeyi-katılımcı-yap", description="Seçilen üyeyi jam katılımcısı yapar.")
    @discord.app_commands.describe(hedef_kullanici="katılımcı olucak üye")
    @app_commands.check(check_is_jam_mod)
    async def make_user_participant(self,interaction: Interaction,hedef_kullanici : Member):
        check_is_jam_present(interaction)
        participant = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == hedef_kullanici.id)
        if participant:
            raise TargetUserIsAlreadyJamParticipantException()
        await create_jam_participant(hedef_kullanici)
        await interaction.response.send_message("✅ Üye başarıyla katılımcı yapıldı.",ephemeral=True)

    @jam_mod.command(name="dosyadakileri-katılımcı-yap", description="Seçilen dosyadaki herkesi jam katılımcısı yapar.")
    @discord.app_commands.describe(dosya="kullanılacak dosya")
    @app_commands.check(check_is_jam_mod)
    async def make_users_from_folder_participant(self,interaction: Interaction,dosya : Attachment):
        check_is_jam_present(interaction)
        await interaction.response.defer()

        if not dosya:
            await interaction.followup.send("❌ Lütfen dosya ekleyin.", ephemeral=True)
            return

        file_bytes = await dosya.read()
        text = file_bytes.decode("utf-8", errors="ignore")

        lines = text.splitlines()

        memberRole : Role = bot_globals.Server_Unog.get_role(bot_globals.ROLEID_MEMBER)
        jam_doc = bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")
        jam_participant_id = jam_doc.get('participantRoleID')
        participantRole : Role = bot_globals.Server_Unog.get_role(jam_participant_id)

        if not participantRole:
            await interaction.followup.send("❌ Jam katılımcısı rolü bulunamıyor.",ephemeral=True)
            return

        end_msg : str = "✅ İşlem başarılı, bu işlemin yanında bulunamayan kullanıcılar aşağıdaki gibi listelenmiştir:"
        absences : str = ""

        for i, line in enumerate(lines, start=1):
            name = line.strip().split(",")[0].strip().title()
            username = line.strip().split(",")[1].strip().removeprefix("@")

            user = bot_globals.Server_Unog.get_member_named(username)
            if not user:
                absences += line + "\n"
            else:
                if not is_user_member(user=user):
                    await user.add_roles(memberRole)
                    await user.edit(nick=name)
                if not is_user_in_jam(user):
                    await create_jam_participant(user)
        
        
        file = discord.File(
            io.BytesIO(absences.encode("utf-8")),
            filename="output.txt"
        )

        await interaction.followup.send(end_msg,file=file,ephemeral=True)



    # @jam_mod.command(name="terfi", description="Oyun sayfası eklenmiş olan ekipleri terfi eder ve Jammer rolünü ekler.")
    # @app_commands.check(check_is_jam_mod)
    # async def jam_rank_teams(self,interaction: Interaction): #buraya manuel approvement ekleyeceğiz.
    #     check_is_jam_present(interaction)
    #     pass



    @jam_mod.command(name="üyeyi-ekibinden-çıkar", description="Yazılan ekipten üyeyi çıkartırsınız.")
    @app_commands.describe(hedef="Ekibinden çıkartılcak kişi.")
    @app_commands.check(check_is_jam_mod)
    async def jam_mod_remove_participant_from_team(self,interaction: Interaction, hedef : Member):

        check_is_jam_present(interaction)
        target_participant_doc = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == hedef.id)
        if not target_participant_doc:
            raise TargetUserIsNotInJam()
        team_doc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(doc_id=target_participant_doc.get('teamID'))
        if not team_doc:
            raise TargetUserIsNotInJamTeam()
        await remove_participant_from_jam_team(target_participant_doc,send_message_to_team=True,interaction=interaction)

class JamCog(commands.Cog):

    jammer = app_commands.Group(
        name="jam",
        description="Jammer Komutları",
        guild_ids=[bot_globals.SERVERID_UNOG])

    def __init__(self, bot: commands.Bot):
        self.bot = bot



    @jammer.command(name="bilgi", description="Mevcut jamle ilgili tüm bilgileri gösterir.")
    @app_commands.check(check_can_member_get_jam_info)
    async def jam_info(self,interaction : Interaction): #DONE
        jam_doc = is_jam_present()
        participant_doc = is_user_in_jam(interaction.user)
        string_teaminfo : str = ""
        if participant_doc:
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
        jamData : Jam = Jam(mapping=jam_doc)
        embed = Embed(title=jamData.longName + " 🕹",
                        color=choice(bot_globals.COLORS_UNOG),
                        description=jamData.description + f"\n\n{string_teaminfo}")
        embed.add_field(name="🏁 Başlangıç Zamanı:",value=f"<t:{jamData.startUnix}>")
        embed.add_field(name='🚩 Bitiş Zamanı:',value=f"<t:{jamData.endUnix}>")
        embed.add_field(name='👤 Katılımcı Rolü:',value=f"<@&{jamData.participantRoleID}>")
        embed.add_field(name='🌏 Web Adresi:',value=jamData.url)
        await interaction.response.send_message(embed=embed,ephemeral=True)
 


    @jammer.command(name="yardım", description="Jam komutlarının açıklamaları.")
    @app_commands.check(check_can_member_get_jam_help)
    async def jam_help(self,interaction : Interaction): #DONE, SADECE DEĞİŞTİRİLMESİ KALDI
        
        embed : Embed = Embed(title="Jam Komutları",description="Aşağıda Jamle ilgili bütün komutların açıklamaları bulunmaktadır.\n",color=choice(bot_globals.COLORS_UNOG))
        
        embed.add_field(name="`/jam bilgi`",value="*Mevcut jamle ilgili tüm bilgileri gösterir.*")
        embed.add_field(name="`/jam yardım`",value="*Kullanabileceğiniz Jam komutlarını listeler.*")
        embed.add_field(name="`/jam katıl`",value="*Mevcut jame katılırsınız.*")
        embed.add_field(name="`/jam ekip-kur`",value="*Katıldığınız jamde bir ekip oluşturur.Bir jamde her katılımcının bir ekipte bulunması gerekir.*")
        embed.add_field(name="`/jam ekipten-çık`",value="*Bulunduğunuz jam ekibinden çıkarsınız.*")
        embed.add_field(name="`/jam ekibe-katıl`",value="*Yazdığınız ekibe katılım isteği gönderir.*")
        embed.add_field(name="`/jam ekip-isteğini-kabul-et`",value="*Yazılan kullanıcının katılım isteğini kabul eder.*")
        embed.add_field(name="`/jam oyunu-gönder`",value="*Bulunduğunuz jam ekibinin projesini çıkartmış olursunuz.*")
        await interaction.response.send_message(embed=embed,ephemeral=True)



    @jammer.command(name="katıl", description="Mevcut jame katılırsınız.")
    @app_commands.check(check_can_user_join_jam)
    async def jam_join(self,interaction : Interaction): #DONE

        currentJam : Jam = Jam(mapping=bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta"))
        jamParticipantRole : Role = bot_globals.Server_Unog.get_role(currentJam.participantRoleID)

        bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.insert(JamParticipant(discordID=interaction.user.id))
        await interaction.user.add_roles(jamParticipantRole)
        embed = Embed(title="✅ Başarılı! ",color=choice(bot_globals.COLORS_UNOG),description=f"{currentJam.longName} jamine katıldınız. \n\n Şimdi aşağıdaki komutlarla devam edin:\n `/jam ekip-kur <ekibin ses kanalındaki adı>` veya,\n `/jam ekibe-katıl <ekibin ses kanalındaki adı>`\n Bu komutlarla solo/ekip fark etmeksizin bir ekip oluşturup/girip etkinliğe başlayabilirsiniz.\n\n Sıkıştığınız durumlarda `/jam-yardım` komutuyla her komutun detaylı açıklamasına ulaşabilirsiniz.")
        await interaction.response.send_message("",embed=embed,ephemeral=True)



    @jammer.command(name="ekip-kur", description="Katıldığınız jamde ekip kurarsınız.")
    @discord.app_commands.describe(ekip_adi="Lideri olacağınız ekibinizin adı")
    @app_commands.check(check_can_user_create_jam_team)
    async def jam_create_team(self,interaction : Interaction, ekip_adi : str ): #DONE

        ekip_adi = ekip_adi.strip().lower().replace(" ","-")
        team_doc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(Query().teamName == ekip_adi)
        if team_doc:
            raise JamTeamNameAlreadyPresentException()
        
        participant_doc = is_user_in_jam(interaction.user)
        jam_doc : Document = is_jam_present()
        jam : Jam = Jam(mapping=jam_doc)
        jamCategory :CategoryChannel = None

        for x in bot_globals.Server_Unog.categories:
            if x.id == jam.categoryID:
                jamCategory = x
        
        if not jamCategory:
            raise JamCategoryNotPresentException()

        teamid = await create_jam_team(ekip_adi,jamCategory)
        team_doc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(doc_id=teamid)
        await add_participant_to_jam_team(participant_doc,team_doc)

        await interaction.response.send_message(f"Ekip: **{ekip_adi}** başarıyla oluşturuldu. ✅\n Artık oluşturacağınız bu ekibe katılım isteklerini yollatabilirsiniz.\n**Not:** Ekibinizle ilgili komutları ekibinizin ses kanalında çağırmanız gerekir.",ephemeral=True)



    @jammer.command(name="ekipten-çık", description="Bulunduğunuz jam ekibinden çıkış yaparsınız.")
    @app_commands.check(check_can_user_leave_jam_team)
    async def jam_leave_team(self,interaction : Interaction): #DONE 

        participant_doc = is_user_in_jam(interaction.user)
        await remove_participant_from_jam_team(participant_doc,True)
        await interaction.response.send_message("🔙 Jam ekibinizden başarıyla çıktınız.",ephemeral=True,delete_after=20)


    @jammer.command(name="ekibe-katıl", description="Yazdığınız ekibe katılma isteği gönderir.")
    @discord.app_commands.describe(ekip_adi="Katılacağınız ekibinizin adı")
    @app_commands.check(check_can_user_send_jam_team_join_request)
    async def jam_send_join_request(self,interaction : Interaction, ekip_adi : str ): # DONE

        ekip_adi = ekip_adi.strip().lower().replace(" ","-")
        participant_doc = is_user_in_jam(interaction.user)
        target_team_doc = bot_globals.TABLE_JAM_CURRENT_TEAMS.get(Query().teamName == ekip_adi)
        if not target_team_doc:
            raise ThisGivenJamTeamNameDoesNotExistException()
        await add_jam_join_request_to_jam_team(participant_doc,target_team_doc)
        await interaction.response.send_message(f"**{target_team_doc.get('teamName')}** ekibine davetiyeniz başarıyla gönderildi!",ephemeral=True,delete_after=20)



    @jammer.command(name="ekip-isteğini-kabul-et", description="Yazdığınız ekibe katılma isteği gönderir.")
    @discord.app_commands.describe(kullanici_adi="İstek yollayan kullanıcının discord adı (örn:.krenel)")
    @app_commands.check(check_can_user_accept_jam_join_request)
    async def jam_accept_invitation(self,interaction : Interaction, kullanici_adi : str ): # DONE
        kullanici_adi = kullanici_adi.strip()
        target_user = bot_globals.Server_Unog.get_member_named(kullanici_adi)
        if not target_user:
            raise ThisParticipantNotInServerException()
        target_member = is_user_member(target_user)
        target_participant_doc = is_user_in_jam(target_user)
        team_doc : Document = is_user_in_jam_team(interaction.user)
        team = JamTeam(mapping=team_doc)
        
        if not target_member:
            raise TargetUserIsNotVerified()
        elif not target_participant_doc:
            raise TargetUserIsNotInJam()
        elif target_participant_doc.doc_id in team.members or target_participant_doc.doc_id == team.leader:
            raise TargetUserIsAlreadyInYourJamTeam()
        elif not target_participant_doc.doc_id in team.joinRequests:
            raise TargetUserIsNotJoinRequestingYourJamTeam()
        
        team.joinRequests.remove(target_participant_doc.doc_id)
        bot_globals.TABLE_JAM_CURRENT_TEAMS.update({'joinRequests':team.joinRequests},doc_ids=[team_doc.doc_id])
        await interaction.response.send_message("✅ Katılım isteği başarıyla kabul edildi.",ephemeral=True,delete_after=10)
        await add_participant_to_jam_team(target_participant_doc,team_doc,True)



    @jammer.command(name="oyunu-gönder", description="⚠ Dikkat!: Sadece bir kere kullanılır. Ekibinizle bitmiş jam oyununuzu yollarsınız.")
    @discord.app_commands.describe(oyun_url="Bitmiş oyununuzun URL'si.")
    @app_commands.check(check_can_user_jam_submit)
    async def jam_team_submit(self,interaction : Interaction,oyun_url : str): #DONE

        team_doc = is_user_jam_team_leader(interaction.user)
        await submit_jam_project(team_doc,oyun_url)
        await interaction.response.send_message("✅ Jam Oyununuzun Gönderimi Başarılı!\n Artık bir şey yapmanıza gerek yok, moderatörler tüm oyunları inceleyecektir.",ephemeral=True,delete_after=15)


async def setup_commands(bot_instance: Bot):
    await bot_instance.add_cog(DirectorCog(bot_instance))
    await bot_instance.add_cog(ApproverCog(bot_instance))
    await bot_instance.add_cog(BotdevCog(bot_instance))
    await bot_instance.add_cog(JamModCog(bot_instance))
    await bot_instance.add_cog(JamCog(bot_instance))


