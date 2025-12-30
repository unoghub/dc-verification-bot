import discord
import json
from random import choice
from discord.ui import View,Button
from discord import Embed,File,Attachment,ButtonStyle,Interaction,Member,Role,Guild,CategoryChannel,Object
from discord.ext.commands import Context,Bot
from openpyxl import Workbook
from tinydb import Query
import bot_globals
from bot_modals import ApprovalModal,ApprovalChannelSelect,MemberRoleSelect,ApproverRoleSelect,NewUserChannelSelect
from bot_conditions import is_user_admin,is_user_approver
from discord.app_commands.checks import has_any_role
from bot_actions import welcome_member_message
from bot_exceptions import reply_no_permission
from bot_conditions import is_user_admin
from bot_events import actives

def setup_commands(bot_instance: Bot):

    @bot_instance.tree.command(name="indir_veritabanı",guild=bot_globals.GUILD_UNOG,description="ÜNOG Veritabanını JSON olarak indirir ve günceller.")
    async def dbjson(ctx: Context):
        if not is_user_admin(ctx.author):
            await reply_no_permission(ctx)
            return
        file = File("unog.json")
        await ctx.send(file=file)




    @bot_instance.tree.command(name="ayarlar",description="Bot ayarları panelini aç.",guild=bot_globals.GUILD_UNOG)
    async def botSettings(interctn: Interaction):

        if not is_user_admin(interctn.user):
            await reply_no_permission(interctn.context)
            return

        embed = Embed(title="Bot Ayarları", description="Onaylama kanalı seçin.", color=choice(bot_globals.COLORS_UNOG))

        verificationChannel = bot_globals.Server_Unog.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION)
        verifiedRole = bot_globals.Server_Unog.get_role(bot_globals.ROLEID_MEMBER)
        approverRole = bot_globals.Server_Unog.get_role(bot_globals.ROLEID_APPROVER)

        if not verificationChannel:
            embed.add_field(name="Onay Kanalı", value="Ayarlanmamış")
        else:
            embed.add_field(name="Onay Kanalı",value="<#" + str(verificationChannel.id) + ">")

        if not verifiedRole:
            embed.add_field(name="Onaylı Üye Rolü", value="Ayarlanmamış")
        else:
            embed.add_field(name="Onaylı Üye Rolü", value="<@&" + str(verifiedRole.id) + ">")
        
        if not approverRole:
            embed.add_field(name="Alım Sorumlusu Rolü", value="Ayarlanmamış")
        else:
            embed.add_field(name="Alım Sorumlusu Rolü", value="<@&" + str(approverRole.id) + ">")

        async def select_approval_channel(interaction : Interaction):
            await interaction.response.send_message("Onay Paneli kanalını seçin:", ephemeral=True, delete_after=180,view=View().add_item(ApprovalChannelSelect()))

        async def set_member_role(interaction : Interaction):
            await interaction.response.send_message("Üye rolünü seçin.", ephemeral=True, delete_after=180,view=View().add_item(MemberRoleSelect()))

        async def reset_member_role(interaction : Interaction ):
            bot_globals.ROLEID_MEMBER = 1330931358628974642
            await interaction.response.send_message("Üye rolü sıfırlandı.", ephemeral=True, delete_after=30)

        async def set_approver_role(interaction : Interaction):
            await interaction.response.send_message("Alım Sorumlusu rolünü seçin.", ephemeral=True, delete_after=180,view=View().add_item(ApproverRoleSelect()))



        """async def newuser(interaction: Interaction):
            if not is_user_admin(interaction.user):
                await reply_no_permission(interaction.context)
                return
            
            embed = Embed(title="Yeni Kullanıcı Ayarları",description="Yeni kullanıcı geldiğinde yapılacak işlemleri ayarlayın.",color=choice(constants.COLORS_UNOG))
            db = TinyDB(UNOG_DATABASE)
            newuser = db.table('newuser')
            newuser = newuser.search(Query().guild == interaction.guild.id)
            if newuser:
                roleList = ""
                for role in newuser:
                    roleList += "<@&" + str(role['role']) + ">\n"
                embed.add_field(name="Yeni Kullanıcı Rolü", value=roleList)
            else:
                embed.add_field(name="Yeni Kullanıcı Rolü", value="Ayarlanmamış")
            channel = db.table('newuserchannel')
            channel = channel.search(Query().guild == interaction.guild.id)
            if channel:
                embed.add_field(name="Yeni Kullanıcı Kanalı", value="<#" + str(channel[0]['channel']) + ">")
            else:
                embed.add_field(name="Yeni Kullanıcı Kanalı", value="Ayarlanmamış")
            message = db.table('newusermessage')
            message = message.search(Query().guild == interaction.guild.id)
            if message:
                embed.add_field(name="Yeni Kullanıcı Mesajı", value=message[0]['message'], inline=False)
            else:
                embed.add_field(name="Yeni Kullanıcı Mesajı", value="Ayarlanmamış", inline=False)

            buton = Button(style=ButtonStyle.primary, label="Yeni Kullanıcı Rolleri Seç", custom_id="newuserrole")
            butonsil = Button(style=ButtonStyle.grey, label="Yeni Kullanıcı Rolünü Sıfırla",custom_id="newuserrolesil", row=1)
            butonkanal = Button(style=ButtonStyle.primary, label="Kanal Seç", custom_id="channel")
            butonkanalsil = Button(style=ButtonStyle.grey, label="Kanalı Sıfırla", custom_id="channeldel", row=1)
            butonmesaj = Button(style=ButtonStyle.green, label="Mesaj ayarla", custom_id="message")
            butonmesajsil = Button(style=ButtonStyle.grey, label="Mesajı Sıfırla", custom_id="messagedel", row=1)
            buttonmesajiyazdir = Button(style=ButtonStyle.red, label="Mesajı Yazdır", custom_id="mesajiyazdir")

            async def newuserchannel(interaction : Interaction):
                await interaction.response.send_message("Kanal seçin.", ephemeral=True, delete_after=180,view=View().add_item(NewUserChannelSelect()))

            async def newuserrole(interaction : Interaction):
                await interaction.response.send_message("Birden fazla seçebilirsin!", ephemeral=True, delete_after=180,view=View().add_item(NewUserSelect()))

            async def newuserrolesil(interaction : Interaction):
                db = TinyDB(UNOG_DATABASE)
                roles = db.table('newuser')
                roles.remove(Query().guild == interaction.guild.id)
                await interaction.response.send_message("Yeni kullanıcı rolü sıfırlandı.", ephemeral=True, delete_after=30)

            async def newuserchannelsil(interaction : Interaction):
                db = TinyDB(UNOG_DATABASE)
                channel = db.table('newuserchannel')
                channel.remove(Query().guild == interaction.guild.id)
                await interaction.response.send_message("Kanal sıfırlandı.", ephemeral=True, delete_after=30)

            async def newusermesaj(interaction : Interaction):
                await interaction.response.send_modal(NewUserMessageSelect())

            async def newusermesajsil(interaction : Interaction):
                db = TinyDB(UNOG_DATABASE)
                message = db.table('newusermessage')
                message.remove(Query().guild == interaction.guild.id)
                await interaction.response.send_message("Mesaj sıfırlandı.", ephemeral=True, delete_after=30)

            async def mesajiyazdir(interaction : Interaction):
                db = TinyDB(UNOG_DATABASE)
                message = db.table('newusermessage')
                message = message.search(Query().guild == interaction.guild.id)
                if message:
                    message = message[0]['message']
                    message = message.replace("<", f"\<")
                    await interaction.response.send_message(message, ephemeral=True, delete_after=30)
                else:
                    await interaction.response.send_message("Mesaj ayarlanmamış.", ephemeral=True, delete_after=30)

            butonsil.callback = newuserrolesil
            buton.callback = newuserrole
            butonkanal.callback = newuserchannel
            butonkanalsil.callback = newuserchannelsil
            butonmesaj.callback = newusermesaj
            butonmesajsil.callback = newusermesajsil
            buttonmesajiyazdir.callback = mesajiyazdir

            view = View()
            view.add_item(buton)
            view.add_item(butonsil)
            view.add_item(butonkanal)
            view.add_item(butonkanalsil)
            view.add_item(butonmesaj)
            view.add_item(butonmesajsil)
            view.add_item(buttonmesajiyazdir)

            await interaction.response.send_message("", ephemeral=True, delete_after=180, embed=embed, view=view)
"""
        
        view = View()
        button1 = Button(style=ButtonStyle.primary, label="Onay Başvurusu Kanalını Düzenle", custom_id="channel")
        button8 = Button(style=ButtonStyle.primary, label="Alım Sorumlusu Rolünü Düzenle", custom_id="approveRole")
        button3 = Button(style=ButtonStyle.green, label="Onaylı Rolünü Düzenle", custom_id="give",row=1)
        button6 = Button(style=ButtonStyle.grey, label="Onaylı Rolünü Sıfırla", custom_id="givedel", row=1)
        #button4 = Button(style=ButtonStyle.grey, label="Kanalı Sıfırla", custom_id="channeldel", row=1)
        #button7 = Button(style=ButtonStyle.primary, label="Yeni Kullanıcı Ayarları", custom_id="excell", row=2)

        button1.callback = select_approval_channel
        button3.callback = set_member_role
        button6.callback = reset_member_role
        button8.callback = set_approver_role
        #button7.callback = newuser

        view.add_item(button1)
        view.add_item(button3)
        #view.add_item(button4)
        #view.add_item(button5)
        view.add_item(button6)
        #view.add_item(button7)
        view.add_item(button8)

        await interctn.response.send_message("", view=view, embed=embed, ephemeral=True, delete_after=180)


    @bot_instance.tree.command(name="butonları_yenile", description="Aktif butonları yeniler.",guild=bot_globals.GUILD_UNOG)
    async def refresh_active_buttons(ctx: Context):
        if not is_user_admin(ctx.author):
            await reply_no_permission(ctx)
            return

        await actives()
        await ctx.reply('Butonlar yenilendi.', ephemeral=True, delete_after=30)


    @bot_instance.tree.command(name="excell", description="ÜNOG veritabanını excel dosyası olarak çıkarır ve günceller.",guild=bot_globals.GUILD_UNOG)
    async def excell(ctx: Context):

        if not is_user_admin(ctx.author):
            await reply_no_permission(ctx)
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

        await ctx.reply('Excell dosyası oluşturuldu/güncellendi.', ephemeral=True, delete_after=180, file=attach)


    @bot_instance.tree.command(name="jamyarat", description="Yeni bir jam oluştur.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(jam_adı="Her yerde bu yazıcaktır.")
    async def jam_create(interaction: Context, jam_adı: str):
        guild: Guild = interaction.guild
        category: CategoryChannel = await guild.create_category(jam_adı)
        await guild.create_voice_channel(name="Genel Sohbet", category=category)
        await guild.create_text_channel(str.lower(jam_adı).replace(" ", "-"), category=category)
        await guild.create_role(name=jam_adı + " Katılımcısı")
        await interaction.reply(
            "Jam: **" + jam_adı + "** başarıyla yaratıldı.\n Bilgi: Otomatik oluşturulan rolü sonradan ayarlayabilirsiniz ancak id numarası değişeceği için rolü komple değiştirmemelisiniz. (silip yenisini oluşturmak)",
            ephemeral=True, delete_after=30)


    @bot_instance.tree.command(name="jam_takımları_kur", description="Jam takımlarını oluştur.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(category="Jam'in bulunduğu Kategori Kanalı", teams=".csv formatında takımların dosyası")
    async def jam_set_teams(ctx: Context, category: CategoryChannel, teams: Attachment):
        file_bytes = await teams.read()
        data = json.loads(file_bytes.decode("utf-8"))
        if isinstance(data, dict):
            for key, item in data.items():
                await ctx.guild.create_voice_channel(name=key, category=category)

        await ctx.reply("Takımlar başarıyla oluşturuldu.", ephemeral=True, delete_after=30)


    @bot_instance.tree.command(name="onayla", description="Kullanıcıyı manuel onaylar.", guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(user="Onaylanan kullanıcı",usernick="Yeni İsmi")
    async def approve_manually(ctx: Context, user: Member,usernick : str):

        if not is_user_approver(ctx.author):
            await reply_no_permission(ctx)
            return
        
        IsUserMember : bool = False
        for i in user.roles:
            if i.id == bot_globals.ROLEID_MEMBER:
                IsUserMember = True

        if not IsUserMember:
            await user.add_roles(bot_globals.ROLEID_MEMBER)
            if usernick:
                await user.edit(nick=usernick)
        else:
            ctx.reply("Kullanıcı zaten onaylı",ephemeral=True,delete_after=30)
            return

        bot_globals.TABLE_MEMBERS.update({'inserver': 'yes'}, Query().id == user.id)

        embed = Embed(title=f"Onaylandı!", color=choice(bot_globals.COLORS_UNOG))
        embed.add_field(name="\u200b", value=f"<@{user.id}>", inline=False)
        embed.set_thumbnail(url=user.avatar)

        await ctx.reply(embed=embed)

        await welcome_member_message(ctx.guild, user)


    @bot_instance.tree.command(name="onay_kayıt_butonu_yarat", description="Girilen kanalda onay kayıt butonu oluşturur.",guild=bot_globals.GUILD_UNOG)
    @discord.app_commands.describe(description="Mesaj için metin girin.")
    async def create_verification_application_button(ctx: Context, description: str = None):
        
        if not is_user_admin(ctx.author):
            await reply_no_permission(ctx)
            return
        
        verificationChannel = bot_globals.UnogBot.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION)
        
        if not verificationChannel:
            await ctx.reply('Önce kayıt kanalını ayarlamalısınız.', ephemeral=True, delete_after=30)
            return

        view = View(timeout=None)

        async def send_modal(interaction : Interaction):

            if bot_globals.Server_Unog.get_role(bot_globals.ROLEID_MEMBER) in interaction.user.roles:
                await interaction.response.send_message("Sistemimizde onaylı gözüküyorsunuz, bir hata durumunda Direktörlerimize ulaşabilirsiniz.", ephemeral=True, delete_after=10)
                return
            await interaction.response.send_modal(ApprovalModal())

        button1 = Button(style=ButtonStyle.primary, label="Onay Talebi İçin Tıkla!", custom_id="modal")
        button1.callback = send_modal
        view.add_item(button1)

        message = await ctx.channel.send(description, view=view)

        

