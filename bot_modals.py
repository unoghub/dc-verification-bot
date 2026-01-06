from discord import Interaction,TextStyle,Embed,InteractionType,ButtonStyle,TextChannel,ChannelType,Member
from discord.ui import Modal, TextInput, View, Button, ChannelSelect, RoleSelect
from tinydb import Query
from random import choice
from typing import Callable
import bot_globals

class DenyVerificationModal(Modal):
    def __init__(self, interaction: Interaction):
        super().__init__()
        self.maininte = interaction
    title = "Reddetme Formu"
    info1 = TextInput(label="Reddetme sebebi", custom_id="redinfo", placeholder="Reddetme sebebini giriniz.", style=TextStyle.paragraph, max_length=1500)

    async def on_submit(self, interaction: Interaction):

        user : Member = interaction.guild.get_member(int(interaction.message.embeds[0].description.split(">")[0].split("@")[1]))

        bot_globals.TABLE_DENIES.insert({'reason': self.info1.value, 'refuser': interaction.user.name,'id':user.id})

        embed = Embed(title="Reddedildi ❌", description="Kullanıcıya mesaj gönderildi!", color=choice(bot_globals.COLORS_UNOG))
        embed.add_field(name="\u200b", value=f"<@{user.id}>", inline=False)
        embed.add_field(name="Reddetme Sebebi 🤨", value=self.info1.value, inline=False)
        embed.add_field(name="Reddeden", value=interaction.user.mention, inline=False)
        embed.set_thumbnail(url=user.avatar)

        await interaction.response.send_message(f"", embed=embed)
        if self.maininte.type == InteractionType.component:
            await self.maininte.message.add_reaction("❌")
            buton1 = Button(style=ButtonStyle.green, label="Onayla", custom_id="onayla", disabled=True)
            buton2 = Button(style=ButtonStyle.red, label="Reddet", custom_id="reddet", disabled=True)
            view = View()
            view.add_item(buton1)
            view.add_item(buton2)
            await self.maininte.message.edit(view=view)
        await user.send(f"Merhaba, {user.mention}!\nUmarız iyisindir ve her şey yolundadır. Başvurunu inceledik fakat maalesef aşağıdaki nedenden dolayı kabul edemiyoruz.\n```{self.info1.value}```\nEğer formu buna dikkat ederek yeniden doldurursan en kısa sürede başvurunu tekrar inceleyip seni onaylayabiliriz.\nAyrıca eğer bir problemle karşılaşırsan direktörler ile iletişime geçebilirsin. <:A_logo_unog:945028420977455157> 💙")

class ApprovalModal(Modal):
    _approveCallback : Callable[[Interaction],None] = None
    _denyCallback : Callable[[Interaction],None] = None

    def __init__(self, *, title = ..., timeout = None, custom_id = ...,approveCallback : Callable[[Interaction],None],denyCallback : Callable[[Interaction],None]):
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        _approveCallback = approveCallback
        _denyCallback = denyCallback

    title = "📝 Onaylanma Formu"

    name = TextInput(label="İsim Ve Soyisim", custom_id="name")
    email = TextInput(label="E-mail Adresi", custom_id="email")
    birthday = TextInput(label="Doğum Tarihi", custom_id="birthday", placeholder="GG.AA.YYYY")
    info1 = TextInput(label="Bulunduğunuz Kurum Veya Ekip", custom_id="info1")
    info2 = TextInput(label="ÜNOG'u Nasıl Keşfettiniz?", custom_id="info2", required=False)

    async def on_submit(self, interaction: Interaction):

        approvalChannel : TextChannel = bot_globals.Server_Unog.get_channel(bot_globals.TEXTCHANNELID_VERIFICATION_PANEL)
        nameFormat : str = self.name.value.title()
        
        bot_globals.TABLE_APPROVES.upsert({'name': nameFormat ,'email': self.email.value, 'birthday': self.birthday.value, 'info1': self.info1.value, 'info2': self.info2.value, 'inserver': 'no', 'memberinfo': 'no', 'id': interaction.user.id}, Query().id == interaction.user.id)

        embed = Embed(title="Talebiniz Alındı!", description="Yetkili tarafından onaylandığında rol ataması yapacağım!", color=choice(bot_globals.COLORS_UNOG))

        await interaction.response.send_message(f"", ephemeral=True, delete_after=30, embed=embed)


        embed = Embed(title="Yeni Üye", description=f"{interaction.user.mention} sunucuya katıldı!", color=choice(bot_globals.COLORS_UNOG))
        embed.add_field(name="İsim", value=self.name.value, inline=False)
        embed.add_field(name="E-mail", value=self.email.value, inline=False)
        embed.add_field(name="Doğum Tarihi", value=self.birthday.value, inline=False)
        embed.add_field(name="Bulunduğunuz Kurum Veya Ekip", value=self.info1.value, inline=False)
        embed.add_field(name="ÜNOG'u Nasıl Keşfettiniz?", value=self.info2.value, inline=False)
        embed.set_thumbnail(url=interaction.user.avatar)


        buton1 =   Button(style=ButtonStyle.green, label="Onayla", custom_id="onayla")
        buton2 =   Button(style=ButtonStyle.red, label="Reddet", custom_id="reddet")
        view = View(timeout=None)
        buton1.callback = self._approveCallback
        buton2.callback = self._denyCallback
        view.add_item(buton1)
        view.add_item(buton2)
        await approvalChannel.send(embed=embed, view=view)

class VerificationPanelChannelSelect(ChannelSelect):
    def __init__(self):
        options = [ChannelType.text]
        super().__init__(channel_types=options)

    async def callback(self, interaction: Interaction):
        bot_globals.TEXTCHANNELID_VERIFICATION_PANEL = self.values[0].id
        await interaction.response.send_message(f"Kanal seçildi. <#{bot_globals.TEXTCHANNELID_VERIFICATION_PANEL}>", ephemeral=True, delete_after=10)

class VerificationChannelSelect(ChannelSelect):
    def __init__(self):
        options = [ChannelType.text]
        super().__init__(channel_types=options)
    async def callback(self, interaction: Interaction):
        bot_globals.TEXTCHANNELID_VERIFICATION = self.values[0].id
        await interaction.response.send_message(f"Kanal seçildi. <#{bot_globals.TEXTCHANNELID_VERIFICATION}>", ephemeral=True, delete_after=10)

class WelcomeChannelSelect(ChannelSelect):
    def __init__(self):
        options = [ChannelType.text]
        super().__init__(channel_types=options)
    async def callback(self, interaction: Interaction):
        bot_globals.TEXTCHANNELID_WELCOME = self.values[0].id
        await interaction.response.send_message(f"Kanal seçildi. <#{bot_globals.TEXTCHANNELID_WELCOME}>", ephemeral=True, delete_after=10)

class MemberRoleSelect(RoleSelect):
    async def callback(self, interaction: Interaction):
        role = bot_globals.Server_Unog.get_role(self.values[0].id)
        if role.is_bot_managed():
            await interaction.response.send_message(f"Bu rol bir botun rolü!\nBot rolleri verilemez.", ephemeral=True, delete_after=10)
            return
        bot_globals.ROLEID_MEMBER = self.values[0].id
        await interaction.response.send_message(f"Rol Seçildi: <@&{self.values[0].id}>", ephemeral=True, delete_after=10)

class ApproverRoleSelect(RoleSelect):
    async def callback(self, interaction: Interaction):
        role = bot_globals.Server_Unog.get_role(self.values[0].id)
        if not role:
            await interaction.response.send_message(f"Girilen rol sunucuda bulunamıyor.", ephemeral=True, delete_after=10)
            return
        if role.is_bot_managed():
            await interaction.response.send_message(f"Bu rol bir botun rolü!\nBot rolleri verilemez.", ephemeral=True, delete_after=10)
            return
        bot_globals.ROLEID_APPROVER = self.values[0].id
        await interaction.response.send_message(f"Rol Eklendi: <@&{self.values[0].id}>", ephemeral=True, delete_after=10)

class NewUserMessageSelect(Modal):
    title = "Yeni Kullanıcı Mesajı"
    message = TextInput(label="Mesaj", custom_id="mesaj", required=True, style=TextStyle.paragraph,placeholder=f"%user% kullanarak kullanıcıyı etiketleyebilir,\n%split% ile birden fazla mesaj gönderebilirsiniz.")

    async def on_submit(self, interaction: Interaction):
        bot_globals.WELCOME_MESSAGES = self.message.value
        await interaction.response.send_message(f"Mesaj ayarlandı.\n\n{self.message.value}", ephemeral=True,delete_after=180)
