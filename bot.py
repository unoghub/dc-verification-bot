import os
from dotenv import load_dotenv
import discord 
from discord.ui import Modal, TextInput, View, Button, ChannelSelect, RoleSelect
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext import tasks
from tinydb import TinyDB, Query
from random import choice
from openpyxl import Workbook

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_NAME = 'members.json'
MEMBER_TABLE = 'members'
ACTIVE_TABLE = 'active'
CHANNEL_TABLE = 'channels'
GIVE_TABLE = 'GIVE'
TAKE_TABLE = 'TAKE'
APPROVER_TABLE = 'APPROVER'
JAMS_TABLE = 'JAMS'
SERVER_ID = 811409264534224947

colors = 0x7ac943, 0x563795, 0x2193c7
KHANO_USERID = 222094201356025857
AKDENIZ_USERID = 385887296555319296

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# region ACTIONS

async def reply_no_permission(context: Context):
    await context.reply('Bu komutu kullanmaya yetkiniz yok.', ephemeral=True, delete_after=30)

async def welcome_user(guild, member):
    db = TinyDB(DB_NAME)
    newuserchannel = db.table('newuserchannel')
    newuserchannel = newuserchannel.search(Query().guild == guild.id)
    if newuserchannel:
        channel = guild.get_channel(newuserchannel[0]['channel'])
        if not channel:
            return
        message = db.table('newusermessage')
        message = message.search(Query().guild == guild.id)
        if message:
            message = message[0]['message']
            if "%split%" in message:
                listelen = message.split("%split%")
                message = choice(listelen)
            if "%user%" in message:
                message = message.replace("%user%", f"{member.nick}")
            if "\>" in message:
                message = message.replace("\<", f"<")
            embed = discord.Embed(title="ÜNOG'a Hoş Geldin!", description=message, color=choice(colors))
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

async def approve_verification(interaction):
    if not is_user_approver(interaction.user):
        await interaction.response.send_message("Bu işlemi yapmaya yetkiniz yok.", ephemeral=True, delete_after=30)
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

    db = TinyDB(DB_NAME)
    role = db.table(GIVE_TABLE)
    role = role.search(Query().guild == interaction.guild.id)
    for r in role:
        try:
            await user.add_roles(interaction.guild.get_role(r['role']))
        except:
            print(f"Role {r['role']} could not be added to {user}")
    role = db.table(TAKE_TABLE)
    role = role.search(Query().guild == interaction.guild.id)
    for r in role:
        try:
            await user.remove_roles(interaction.guild.get_role(r['role']))
        except:
            print(f"Role {r['role']} could not be removed from {user}")
    db = TinyDB(DB_NAME)
    members = db.table(MEMBER_TABLE)
    members.update({'inserver': 'yes'}, Query().id == user.id)

    embed = discord.Embed(title=f"Onaylandı! ✅", color=choice(colors))
    embed.add_field(name="\u200b", value=f"<@{user.id}>", inline=False)
    embed.add_field(name="Onaylayan", value=interaction.user.mention, inline=False)
    embed.set_thumbnail(url=user.avatar)

    await interaction.response.send_message(f"", embed=embed)
    if interaction.type == discord.InteractionType.component:
        await interaction.message.add_reaction("✅")
        buton1 =   Button(style=discord.ButtonStyle.green, label="Onayla", custom_id="onayla", disabled=True)
        buton2 =   Button(style=discord.ButtonStyle.red, label="Reddet", custom_id="reddet", disabled=True)
        view = View()
        view.add_item(buton1)
        view.add_item(buton2)
        await interaction.message.edit(view=view)

    await welcome_user(interaction.guild, user)

async def deny_verification(interaction):
    if not is_user_admin(interaction.user):
        await interaction.response.send_message("Bu işlemi yapmaya yetkiniz yok.", ephemeral=True, delete_after=30)
        return 
    await interaction.response.send_modal(ReddetModal(interaction))

# endregion

# region MODALS

class ReddetModal(Modal):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.maininte = interaction
    title = "Reddetme Formu"
    info1 = TextInput(label="Reddetme sebebi", custom_id="redinfo", placeholder="Reddetme sebebini giriniz.", style=discord.TextStyle.paragraph, max_length=1500)

    async def on_submit(self, interaction: discord.Interaction):
        db = TinyDB(DB_NAME)
        members = db.table(MEMBER_TABLE)
        member = Query()


        # moderatör bildirimi
        user = interaction.message.embeds[0].description
        user = user.split(">")[0]
        user = int(user.split("@")[1])
        user = interaction.guild.get_member(user)

        members.upsert({'ret sebebi': self.info1.value, 'reddeden': interaction.user.name}, member.id == user.id)

        embed = discord.Embed(title="Reddedildi ❌", description="Kullanıcıya mesaj gönderildi!", color=choice(colors))
        embed.add_field(name="\u200b", value=f"<@{user.id}>", inline=False)
        embed.add_field(name="Reddetme Sebebi 🤨", value=self.info1.value, inline=False)
        embed.add_field(name="Reddeden", value=interaction.user.mention, inline=False)
        embed.set_thumbnail(url=user.avatar)

        await interaction.response.send_message(f"", embed=embed)
        if self.maininte.type == discord.InteractionType.component:
            await self.maininte.message.add_reaction("❌")
            buton1 =   Button(style=discord.ButtonStyle.green, label="Onayla", custom_id="onayla", disabled=True)
            buton2 =   Button(style=discord.ButtonStyle.red, label="Reddet", custom_id="reddet", disabled=True)
            view = View()
            view.add_item(buton1)
            view.add_item(buton2)
            await self.maininte.message.edit(view=view)
        await user.send(f"Merhaba, {user.mention}!\nUmarız iyisindir ve her şey yolundadır. Başvurunu inceledik fakat maalesef aşağıdaki nedenden dolayı kabul edemiyoruz.\n```{self.info1.value}```\nEğer formu buna dikkat ederek yeniden doldurursan en kısa sürede başvurunu tekrar inceleyip seni onaylayabiliriz.\nAyrıca eğer bir problemle karşılaşırsan direktörler ile iletişime geçebilirsin. <:A_logo_unog:945028420977455157> 💙")

class OnayFormuModal(Modal):
    title = "📝 Onaylanma Formu"

    name = TextInput(label="İsim Ve Soyisim", custom_id="name")
    email = TextInput(label="E-mail Adresi", custom_id="email")
    birthday = TextInput(label="Doğum Tarihi", custom_id="birthday", placeholder="GG.AA.YYYY")
    info1 = TextInput(label="Bulunduğunuz Kurum Veya Ekip", custom_id="info1")
    info2 = TextInput(label="ÜNOG'u Nasıl Keşfettiniz?", custom_id="info2", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        db = TinyDB(DB_NAME)
        members = db.table(MEMBER_TABLE)
        member = Query()
        nameFormat = self.name.value.title()
        members.upsert({'name': nameFormat,'email': self.email.value, 'birthday': self.birthday.value, 'info1': self.info1.value, 'info2': self.info2.value, 'inserver': 'no', 'memberinfo': 'no', 'id': interaction.user.id}, member.id == interaction.user.id)

        embed = discord.Embed(title="Talebiniz Alındı!", description="Yetkili tarafından onaylandığında rol ataması yapacağım!", color=choice(colors))

        await interaction.response.send_message(f"", ephemeral=True, delete_after=30, embed=embed)

        db = TinyDB(DB_NAME)
        channel = db.table(CHANNEL_TABLE)

        channel = client.get_guild(interaction.guild_id).get_channel(channel.get(Query().guild == interaction.guild.id)['channel'])

        embed = discord.Embed(title="Yeni Üye", description=f"{interaction.user.mention} sunucuya katıldı!", color=choice(colors))
        embed.add_field(name="İsim", value=self.name.value, inline=False)
        embed.add_field(name="E-mail", value=self.email.value, inline=False)
        embed.add_field(name="Doğum Tarihi", value=self.birthday.value, inline=False)
        embed.add_field(name="Bulunduğunuz Kurum Veya Ekip", value=self.info1.value, inline=False)
        embed.add_field(name="ÜNOG'u Nasıl Keşfettiniz?", value=self.info2.value, inline=False)
        embed.set_thumbnail(url=interaction.user.avatar)
            

        buton1 =   Button(style=discord.ButtonStyle.green, label="Onayla", custom_id="onayla")
        buton2 =   Button(style=discord.ButtonStyle.red, label="Reddet", custom_id="reddet")
        view = View(timeout=None)
        buton1.callback = approve_verification
        buton2.callback = deny_verification
        view.add_item(buton1)
        view.add_item(buton2)
        await channel.send(embed=embed, view=view)

class ChannelSelect(ChannelSelect):
    def __init__(self):
        options = [discord.ChannelType.text]
        super().__init__(channel_types=options)

    async def callback(self, interaction: discord.Interaction):
        db = TinyDB(DB_NAME)
        channel = db.table(CHANNEL_TABLE)
        channel.upsert({'guild': interaction.guild.id, 'channel': self.values[0].id, 'channel_name': self.values[0].name}, Query().guild == interaction.guild.id)
        await interaction.response.send_message(f"Kanal seçildi. <#{self.values[0].id}>", ephemeral=True, delete_after=10)

class GiveSelect(RoleSelect):
    async def callback(self, interaction: discord.Interaction):
        db = TinyDB(DB_NAME)
        roles = db.table(GIVE_TABLE)
        role = client.get_guild(interaction.guild.id).get_role(self.values[0].id)
        if role.is_bot_managed():
            await interaction.response.send_message(f"Bu rol bir botun rolü!\nBot rolleri verilemez.", ephemeral=True, delete_after=10)
            return
        roles.upsert({'guild': interaction.guild.id, 'role': self.values[0].id, 'role_name': self.values[0].name}, Query().role == self.values[0].id)
        await interaction.response.send_message(f"Rol Eklendi: <@&{self.values[0].id}>", ephemeral=True, delete_after=10)
        
class TakeSelect(RoleSelect):
    async def callback(self, interaction: discord.Interaction):
        db = TinyDB(DB_NAME)
        roles = db.table(TAKE_TABLE)
        role = client.get_guild(interaction.guild.id).get_role(self.values[0].id)
        if role.is_bot_managed():
            await interaction.response.send_message(f"Bu rol bir botun rolü!\nBot rolleri verilemez.", ephemeral=True, delete_after=10)
            return
        roles.upsert({'guild': interaction.guild.id, 'role': self.values[0].id, 'role_name': self.values[0].name}, Query().role == self.values[0].id)
        await interaction.response.send_message(f"Rol Eklendi: <@&{self.values[0].id}>", ephemeral=True, delete_after=10)

class NewUserSelect(RoleSelect):
    async def callback(self, interaction: discord.Interaction):
        db = TinyDB(DB_NAME)
        roles = db.table('newuser')
        role = client.get_guild(interaction.guild.id).get_role(self.values[0].id)
        if role.is_bot_managed():
            await interaction.response.send_message(f"Bu rol bir botun rolü!\nBot rolleri verilemez.", ephemeral=True, delete_after=10)
            return
        roles.upsert({'guild': interaction.guild.id, 'role': self.values[0].id, 'role_name': self.values[0].name}, Query().role == self.values[0].id)
        await interaction.response.send_message(f"Rol Eklendi: <@&{self.values[0].id}>", ephemeral=True, delete_after=10)

class ApproverRoleSelect(RoleSelect):
    async def callback(self, interaction: discord.Interaction):
        db = TinyDB(DB_NAME)
        roles = db.table(APPROVER_TABLE)
        role = client.get_guild(interaction.guild.id).get_role(self.values[0].id)
        if role.is_bot_managed():
            await interaction.response.send_message(f"Bu rol bir botun rolü!\nBot rolleri verilemez.", ephemeral=True, delete_after=10)
            return
        roles.upsert({'guild': interaction.guild.id, 'role': self.values[0].id, 'role_name': self.values[0].name}, Query().guild == interaction.guild.id)
        await interaction.response.send_message(f"Rol Eklendi: <@&{self.values[0].id}>", ephemeral=True, delete_after=10)

class NewUserChannelSelect(ChannelSelect):
    async def callback(self, interaction: discord.Interaction):
        db = TinyDB(DB_NAME)
        channel = db.table('newuserchannel')
        channel.upsert({'guild': interaction.guild.id, 'channel': self.values[0].id, 'channel_name': self.values[0].name}, Query().guild == interaction.guild.id)
        await interaction.response.send_message(f"Kanal seçildi. <#{self.values[0].id}>", ephemeral=True, delete_after=10)

class NewUserMessageSelect(Modal):
    title = "Yeni Kullanıcı Mesajı"
    message = TextInput(label="Mesaj", custom_id="mesaj", required=True, style=discord.TextStyle.paragraph ,placeholder=f"%user% kullanarak kullanıcıyı etiketleyebilir,\n%split% ile birden fazla mesaj gönderebilirsiniz.")

    async def on_submit(self, interaction: discord.Interaction):
        db = TinyDB(DB_NAME)
        message = db.table('newusermessage')
        message.upsert({'guild': interaction.guild.id, 'message': self.message.value}, Query().guild == interaction.guild.id)
        await interaction.response.send_message(f"Mesaj ayarlandı.\n\n{self.message.value}", ephemeral=True, delete_after=180)

# endregion

async def newuser(interaction : discord.Interaction):
    if not is_user_admin(interaction.user):
        await interaction.response.send_message("Bu işlemi yapmaya yetkiniz yok.", ephemeral=True, delete_after=30)
        return
    embed = discord.Embed(title="Yeni Kullanıcı Ayarları", description="Yeni kullanıcı geldiğinde yapılacak işlemleri ayarlayın.", color=choice(colors))
    db = TinyDB(DB_NAME)
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
    buton = Button(style=discord.ButtonStyle.primary, label="Yeni Kullanıcı Rolleri Seç", custom_id="newuserrole")
    butonsil = Button(style=discord.ButtonStyle.grey, label="Yeni Kullanıcı Rolünü Sıfırla", custom_id="newuserrolesil", row=1)
    butonkanal = Button(style=discord.ButtonStyle.primary, label="Kanal Seç", custom_id="channel")
    butonkanalsil = Button(style=discord.ButtonStyle.grey, label="Kanalı Sıfırla", custom_id="channeldel", row=1)
    butonmesaj = Button(style=discord.ButtonStyle.green, label="Mesaj ayarla", custom_id="message")
    butonmesajsil = Button(style=discord.ButtonStyle.grey, label="Mesajı Sıfırla", custom_id="messagedel", row=1)
    buttonmesajiyazdir = Button(style=discord.ButtonStyle.red, label="Mesajı Yazdır", custom_id="mesajiyazdir")

    async def newuserchannel(interaction):
        await interaction.response.send_message("Kanal seçin.", ephemeral=True, delete_after=180, view=View().add_item(NewUserChannelSelect()))

    async def newuserrole(interaction):
        await interaction.response.send_message("Birden fazla seçebilirsin!", ephemeral=True, delete_after=180, view=View().add_item(NewUserSelect()))

    async def newuserrolesil(interaction):
        db = TinyDB(DB_NAME)
        roles = db.table('newuser')
        roles.remove(Query().guild == interaction.guild.id)
        await interaction.response.send_message("Yeni kullanıcı rolü sıfırlandı.", ephemeral=True, delete_after=30)
    
    async def newuserchannelsil(interaction):
        db = TinyDB(DB_NAME)
        channel = db.table('newuserchannel')
        channel.remove(Query().guild == interaction.guild.id)
        await interaction.response.send_message("Kanal sıfırlandı.", ephemeral=True, delete_after=30)
    
    async def newusermesaj(interaction):
        await interaction.response.send_modal(NewUserMessageSelect())

    async def newusermesajsil(interaction):
        db = TinyDB(DB_NAME)
        message = db.table('newusermessage')
        message.remove(Query().guild == interaction.guild.id)
        await interaction.response.send_message("Mesaj sıfırlandı.", ephemeral=True, delete_after=30)

    async def mesajiyazdir(interaction):
        db = TinyDB(DB_NAME)
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

    await interaction.response.send_message("", ephemeral=True, delete_after=180, embed=embed,  view=view)

#region CONDITIONCHECKS

def is_user_admin(user: discord.Member):
    if user.id == AKDENIZ_USERID or user.id == KHANO_USERID:
        return True
    return user.guild_permissions.administrator

def is_user_approver(user: discord.Member):
    if user.id == AKDENIZ_USERID or user.id == KHANO_USERID:
        return True
    db = TinyDB(DB_NAME)
    approvers = db.table(APPROVER_TABLE)
    role = approvers.get(Query().guild == user.guild.id)
    if role and discord.utils.get(user.roles, id=role['role']):
        return True
    return False

# endregion

# region COMMANDS

@client.command(name="rf")
async def tree(ctx: Context):
    if(is_user_admin(ctx.author)):
        print("tree command has run")
        guild = discord.Object(id=SERVER_ID)
        await client.tree.sync(guild=guild)
    else:
        await reply_no_permission(ctx)

@client.command()
async def dbjson(ctx : Context):
    if not is_user_admin(ctx.author):
        await reply_no_permission(ctx)
        return
    file = discord.File("members.json")
    await ctx.send(file=file)

@client.hybrid_command(name="settings", with_app_command=True, description="Bot ayarları.")
async def settings(ctx : Context):
    if not is_user_admin(ctx.author):
        await ctx.reply('Bu komutu kullanmaya yetkiniz yok.', ephemeral=True, delete_after=30)
        return
    db = TinyDB(DB_NAME)
    channel = db.table(CHANNEL_TABLE)

    embed = discord.Embed(title="Bot Ayarları",description="Onaylama kanalı seçin.", color=choice(colors))
    if not channel.get(Query().guild == ctx.guild.id):
        embed.add_field(name="Kayıt Kanalı", value="Ayarlanmamış")
    else:
        embed.add_field(name="Kayıt Kanalı", value="<#" + str(channel.get(Query().guild == ctx.guild.id)['channel']) + ">")
    roles = db.table(TAKE_TABLE)
    if not roles.search(Query().guild == ctx.guild.id):
        embed.add_field(name="Alınacak Rol", value="Ayarlanmamış")
    else:
        roleList = ""
        for role in roles.search(Query().guild == ctx.guild.id):
            roleList += "<@&" + str(role['role']) + ">\n"
        embed.add_field(name="Alınacak Rol", value=roleList)
    roles = db.table(GIVE_TABLE)
    if not roles.search(Query().guild == ctx.guild.id):
        embed.add_field(name="Verilecek Rol", value="Ayarlanmamış")
    else:
        roleList = ""
        for role in roles.search(Query().guild == ctx.guild.id):
            roleList += "<@&" + str(role['role']) + ">\n"
        embed.add_field(name="Verilecek Rol", value=roleList)
    approverTable = db.table(APPROVER_TABLE)
    approverRole = approverTable.get(Query().guild == ctx.guild.id)
    if not approverRole:
        embed.add_field(name="Onaylayıcı Rol", value= "Ayarlanmamış")
    else:
        if (isinstance(approverRole, list)):
            approverRole = approverRole[0]
        embed.add_field(name="Onaylayıcı Rol", value="<@&" + str(approverRole['role']) + ">")



    async def kanal_sec(interaction):
        await interaction.response.send_message("Kanal seçin.", ephemeral=True, delete_after=180, view=View().add_item(ChannelSelect()))

    async def take(interaction):
        await interaction.response.send_message("Alınacak rolleri seçin.", ephemeral=True, delete_after=180, view=View().add_item(TakeSelect()))
    
    async def give(interaction):
        await interaction.response.send_message("Verilecek rolleri seçin.", ephemeral=True, delete_after=180, view=View().add_item(GiveSelect()))

    async def approveRole(interaction):
        await interaction.response.send_message("Onaylayıcı rolünü seçin.", ephemeral=True, delete_after=180, view=View().add_item(ApproverRoleSelect()))

    async def kanal_sil(interaction):
        db = TinyDB(DB_NAME)
        channel = db.table(CHANNEL_TABLE)
        channel.remove(Query().guild == interaction.guild.id)
        await interaction.response.send_message("Kanal sıfırlandı.", ephemeral=True, delete_after=30)

        db = TinyDB(DB_NAME)
        active = db.table(ACTIVE_TABLE)

        active.remove(Query().guild == interaction.guild.id)

    
    async def take_sil(interaction):
        db = TinyDB(DB_NAME)
        roles = db.table(TAKE_TABLE)
        roles.remove(Query().guild == interaction.guild.id)
        await interaction.response.send_message("Alınacak roller sıfırlandı.", ephemeral=True, delete_after=30)
    async def give_sil(interaction):
        db = TinyDB(DB_NAME)
        roles = db.table(GIVE_TABLE)
        roles.remove(Query().guild == interaction.guild.id)
        await interaction.response.send_message("Verilecek roller sıfırlandı.", ephemeral=True, delete_after=30)

    view = View()
    button1 =  Button(style=discord.ButtonStyle.primary, label="Kanal seç", custom_id="channel")
    button2 =  Button(style=discord.ButtonStyle.red, label="Alınacak rolleri seç", custom_id="take")
    button3 =  Button(style=discord.ButtonStyle.green, label="Verilecek rolleri seç", custom_id="give")
    button4 = Button(style=discord.ButtonStyle.grey, label="Kanalı Sıfırla", custom_id="channeldel", row=1)
    button5 = Button(style=discord.ButtonStyle.grey, label="Alınacak rolleri Sıfırla", custom_id="takedel", row=1)
    button6 = Button(style=discord.ButtonStyle.grey, label="Verilecek rolleri Sıfırla", custom_id="givedel", row=1)
    button7 = Button(style=discord.ButtonStyle.primary, label="Yeni Kullanıcı Ayarları", custom_id="excell", row=2)
    button8 = Button(style=discord.ButtonStyle.primary, label="Onaylayıcı Rolünü Ayarla", custom_id="approveRole", row=3)

    button1.callback = kanal_sec
    button2.callback = take
    button3.callback = give
    button4.callback = kanal_sil
    button5.callback = take_sil
    button6.callback = give_sil
    button7.callback = newuser
    button8.callback = approveRole
    

    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)
    view.add_item(button4)
    view.add_item(button5)
    view.add_item(button6)
    view.add_item(button7)
    view.add_item(button8)
    
    await ctx.reply("", view=view, embed=embed, ephemeral=True, delete_after=180)

@client.hybrid_command(name="refresh", with_app_command=True, description="Bütün butonları yeniler.")
async def refresh(ctx : Context):
    if not is_user_admin(ctx.author):
        await ctx.reply('Bu komutu kullanmaya yetkiniz yok.', ephemeral=True, delete_after=30)
        return
    print("refresh by used -" + ctx.author.name + "- in -" + ctx.guild.name + "- at " + ctx.channel.name)

    await actives()
    await ctx.reply('Butonlar yenilendi.', ephemeral=True, delete_after=30)

@client.hybrid_command(name="excell", with_app_command=True, description="Üyeleri excele döker.")
async def excell(ctx : Context):
    if not is_user_admin(ctx.author):
        await ctx.reply('Bu komutu kullanmaya yetkiniz yok.', ephemeral=True, delete_after=30)
        return
    db = TinyDB(DB_NAME)
    members = db.table(MEMBER_TABLE)
    members = members.all()
    wb = Workbook()
    ws = wb.active
    ws.append(['İsim', 'E-mail', 'Doğum Tarihi', 'info1', "info2", 'Kayıtlı mı?', 'Üye Bilgisi', 'ID', "Ret Sebebi", "Reddeden"])
    for member in members:
        if "ret sebebi" in str(member):
            ws.append([member['name'], member['email'], member['birthday'], member['info1'], member['info2'], member['inserver'], member['memberinfo'], member['id'], member["ret sebebi"], member["reddeden"]])
        else:
            ws.append([member['name'], member['email'], member['birthday'], member['info1'], member['info2'], member['inserver'], member['memberinfo'], member['id']])
    wb.save('members.xlsx')

    attach = discord.File('members.xlsx')

    await ctx.reply('Excell dosyası oluşturuldu.', ephemeral=True, delete_after=180, file=attach)

@client.hybrid_command(name="jamyarat", description="Yeni bir jam oluşturur.")
@discord.app_commands.describe(jam_adı= "Her yerde bu yazıcaktır.")
async def jam_create(interaction: Context, jam_adı:str):
    guild : discord.Guild = interaction.guild
    category : discord.CategoryChannel= await guild.create_category(jam_adı)
    await guild.create_voice_channel(name="Genel Sohbet",category=category)
    await guild.create_text_channel(str.lower(jam_adı).replace(" ","-"),category=category)
    await guild.create_role(name=jam_adı+ " Katılımcısı")
    await interaction.reply("Jam: **" + jam_adı + "** başarıyla yaratıldı.\n Bilgi: Otomatik oluşturulan rolü sonradan ayarlayabilirsiniz ancak id numarası değişeceği için rolü komple değiştirmemelisiniz. (silip yenisini oluşturmak)",ephemeral=True, delete_after=30)

@client.hybrid_command(name="onayla", with_app_command=True, description="Kullanıcıyı manuel onaylar.")
@discord.app_commands.describe(user = "id veya etiket", role = "id veya etiket")
async def onayla_m(ctx : Context, user: discord.Member, role: discord.Role = None, username: str = None):
    if not is_user_approver(ctx.author):
        await ctx.reply('Bu komutu kullanmaya yetkiniz yok.', ephemeral=True, delete_after=30)
        return
    if role:
        await user.add_roles(role)
    if username:
        await user.edit(nick=username)
    db = TinyDB(DB_NAME)
    members = db.table(MEMBER_TABLE)
    members.update({'inserver': 'yes'}, Query().id == user.id)

    embed = discord.Embed(title=f"Onaylandı!", color=choice(colors))
    embed.add_field(name="\u200b", value=f"<@{user.id}>", inline=False)
    embed.set_thumbnail(url=user.avatar)

    await ctx.reply(embed=embed)

    await welcome_user(ctx.guild, user)

@client.hybrid_command(name="buton_yarat", with_app_command=True, description="Girilen kanalda kayıt butonu oluşturur.")
@discord.app_commands.describe(description="Mesaj için metin girin.")
async def buton_yarat(ctx : Context, description: str = None):
    if not is_user_admin(ctx.author):
        await ctx.reply('Bu komutu kullanmaya yetkiniz yok.', ephemeral=True, delete_after=30)
        return
    db = TinyDB(DB_NAME)
    channel = db.table(CHANNEL_TABLE)
    if not channel.get(Query().guild == ctx.guild.id):
        await ctx.reply('Önce kayıt kanalını ayarlamalısınız. /settings', ephemeral=True, delete_after=30)
        return

    view = View(timeout=None)

    async def send_modal(interaction):
        roles = db.table(GIVE_TABLE)
        roles = roles.search(Query().guild == interaction.guild.id)
        for role in roles:
            print(role)
            if interaction.user.guild.get_role(role['role']) in interaction.user.roles:
                await interaction.response.send_message("Zaten Kayıtlısın.", ephemeral=True, delete_after=10)
                return
        await interaction.response.send_modal(OnayFormuModal())

    button1 = Button(style=discord.ButtonStyle.primary, label="Onay Talebi İçin Tıkla!", custom_id="modal")
    button1.callback = send_modal
    view.add_item(button1)

    message = await ctx.channel.send(description, view=view)
    db = TinyDB(DB_NAME)
    active = db.table(ACTIVE_TABLE)

    activeMessage = active.get(Query().guild == ctx.guild.id)
    if activeMessage:
        msg = await ctx.guild.get_channel(activeMessage['channel']).fetch_message(activeMessage['message'])
        await msg.delete()

    active.upsert({'message': message.id, 'channel': message.channel.id, 'guild': message.guild.id,
                   'description': message.content}, Query().guild == message.guild.id)

    await ctx.reply('Buton oluşturuldu.', ephemeral=True, delete_after=30)

# endregion

@tasks.loop(hours=1)
async def actives():
    view = View(timeout=None)
    button1 =   Button(style=discord.ButtonStyle.primary, label="Onay Talebi İçin Tıkla!", custom_id="modal")

    async def send_modal(interaction):
        db = TinyDB(DB_NAME)
        roles = db.table(GIVE_TABLE)
        roles = roles.search(Query().guild == interaction.guild.id)
        for role in roles:
            if interaction.user.guild.get_role(role['role']) in interaction.user.roles:
                await interaction.response.send_message("Zaten Kayıtlısın.", ephemeral=True, delete_after=10)
                return
        await interaction.response.send_modal(OnayFormuModal())
    
    button1.callback = send_modal
    view.add_item(button1)
    client.add_view(view=view)

    buton1 =   Button(style=discord.ButtonStyle.green, label="Onayla", custom_id="onayla")
    buton2 =   Button(style=discord.ButtonStyle.red, label="Reddet", custom_id="reddet")
    view = View(timeout=None)
    buton1.callback = approve_verification
    buton2.callback = deny_verification
    view.add_item(buton1)
    view.add_item(buton2)

    client.add_view(view=view)
    print("Actives added")

# region EVENTS
@client.event
async def on_ready(): 
    print(f'{client.user} is connected')

    actives.start()
    try:
        #guild = discord.Object(id=SERVER_ID)
        await client.tree.sync()
        print('command sync is complete')
    except Exception as e:
        print(e)
 
@client.event
async def on_message(msg):
    if msg.guild is None:
        return
    if msg.content.startswith('!developermod'):
        if not is_user_admin(msg.author):
            return
        if msg.author.id != AKDENIZ_USERID or msg.author.id != KHANO_USERID: 
            return
        role = msg.guild.get_role(603961647127592980) 
        if role in msg.author.roles:
            await msg.author.remove_roles(role)
            await msg.channel.send("Developer modu kapatıldı.")
        else:
            await msg.author.add_roles(role)
            await msg.channel.send("Developer modu açıldı.")


    if msg.content.startswith('!komuttest3'):
        if not is_user_admin(msg.author):
            return
        user = msg.guild.get_member(AKDENIZ_USERID)
        await welcome_user(msg.guild, user)

    if msg.content.startswith('!testwelcome'):
        if not is_user_admin(msg.author):
            return
        await send_welcome_message_test(msg.guild, msg.channel, msg.author)


    if msg.content.startswith('!komuttest1'):
        if not is_user_admin(msg.author):
            return
        user = msg.guild.get_member(AKDENIZ_USERID)
        await user.remove_roles(msg.guild.get_role(1330931358628974642))
        await msg.channel.send("Rol alındı.")

    if msg.content.startswith('!komuttestriskli'):
        if not is_user_admin(msg.author):
            return
        # veritabanindaki kullancilarin hepsine rol ata
        db = TinyDB(DB_NAME)
        members = db.table(MEMBER_TABLE)
        members = members.all()
        role = msg.guild.get_role(1330931358628974642) #onayli uye rolu
        i = 0
        for member in members:
            i+=1
            if i < 1500:
                print("continue " + str(i))
                continue
            memberdb = member
            member = msg.guild.get_member(memberdb['id'])
            if member:
                try:
                    await member.edit(nick=memberdb['name'].title())
                    await member.add_roles(role)
                    print(f"{member} isimli kullanıcıya {role} rolü verildi.")
                except Exception as e:
                    print(f"{member} isimli kullanıcıya rol verilemedi.")
                    print(e)
            else:
                print(f"{member} isimli kullanıcı bulunamadı.")
    
    await client.process_commands(msg)
    return

@client.event
async def on_member_join(member):
    db = TinyDB(DB_NAME)
    newuser = db.table('newuser')
    newuser = newuser.search(Query().guild == member.guild.id)
    if newuser:
        for role in newuser:
            await member.add_roles(member.guild.get_role(role['role']))

@client.event
async def on_member_remove(member):
    db = TinyDB(DB_NAME)
    members = db.table(MEMBER_TABLE)
    members.update({'inserver': 'no'}, Query().id == member.id)

@client.event
async def on_raw_reaction_add(payload):
    if payload.message_id == 1336052031122575532:
        guild = client.get_guild(payload.guild_id)
        if str(payload.emoji) == "👾":
            role = guild.get_role(1330930413992149103)
            await guild.get_member(payload.user_id).add_roles(role)
        if str(payload.emoji) == "🦇":
            role = guild.get_role(1330930595127234580)
            await guild.get_member(payload.user_id).add_roles(role)
        if str(payload.emoji) == "🔶":
            role = guild.get_role(1330930551032512534)
            await guild.get_member(payload.user_id).add_roles(role)
        if str(payload.emoji) == "🔔":
            role = guild.get_role(1332676715104833596)
            await guild.get_member(payload.user_id).add_roles(role)

@client.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == 1336052031122575532:
        guild = client.get_guild(payload.guild_id)
        if str(payload.emoji) == "👾":
            role = guild.get_role(1330930413992149103)
            await guild.get_member(payload.user_id).remove_roles(role)
        if str(payload.emoji) == "🦇":
            role = guild.get_role(1330930595127234580)
            await guild.get_member(payload.user_id).remove_roles(role)
        if str(payload.emoji) == "🔶":
            role = guild.get_role(1330930551032512534)
            await guild.get_member(payload.user_id).remove_roles(role)
        if str(payload.emoji) == "🔔":
            role = guild.get_role(1332676715104833596)
            await guild.get_member(payload.user_id).remove_roles(role)

# endregion 

# region TESTS

async def send_welcome_message_test(guild, channel, member):
    db = TinyDB(DB_NAME)
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
        embed = discord.Embed(title="ÜNOG'a Hoş Geldin!", description=message, color=choice(colors))
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

# endregion

client.run(BOT_TOKEN)
