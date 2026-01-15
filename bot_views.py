from random import choice
from typing import Callable
from discord.ui import View,Modal, TextInput, View, Button, ChannelSelect, RoleSelect
from discord import ButtonStyle, Interaction,TextStyle,Embed,InteractionType,TextChannel,ChannelType,Member
import discord
from bot_models import UnogMember
import bot_globals
from bot_exceptions import UserAlreadyVerified
from bot_conditions import is_user_member


#region views

class ApprovalApplyButtonView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(style=ButtonStyle.primary, label="Onay Talebi İçin Tıkla!", custom_id="applyVerificationButton")
    async def approve(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        pass

class ApprovalFormView(View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(style=ButtonStyle.green, label="Onayla", custom_id="onayla", disabled=False))
        self.add_item(Button(style=ButtonStyle.red, label="Reddet", custom_id="reddet", disabled=False))


#endregion

#region modals

class DenyVerificationModal(Modal):
    _callback : Callable[[Interaction],None]

    def __init__(self, interaction: Interaction, callback : Callable[[Interaction],None]):
        super().__init__()
        self.maininte = interaction
        self._callback = callback

    title = "Reddetme Formu"
    info1 = TextInput(label="Reddetme sebebi", custom_id="redinfo", placeholder="Reddetme sebebini giriniz.", style=TextStyle.paragraph, max_length=1500)

    async def on_submit(self, interaction: Interaction):

        member : Member = interaction.guild.get_member(int(interaction.message.embeds[0].description.split()[0].removeprefix('<@').removesuffix('>')))
        
        await self._callback(interaction,member,self.info1.value)

        if self.maininte.type == InteractionType.component:
            await self.maininte.message.add_reaction("❌")
            buton1 = Button(style=ButtonStyle.green, label="Onayla", custom_id="onayla", disabled=True)
            buton2 = Button(style=ButtonStyle.red, label="Reddet", custom_id="reddet", disabled=True)
            view = View()
            view.add_item(buton1)
            view.add_item(buton2)
            await self.maininte.message.edit(view=view)

class ApprovalModal(Modal):

    _callback : Callable[[Interaction,UnogMember],None]

    def __init__(self,callback : Callable[[Interaction,UnogMember],None]):
        super().__init__(timeout=None)
        self._callback = callback

    title = "📝 Onaylanma Formu"

    name = TextInput(label="İsim Ve Soyisim", custom_id="name")
    email = TextInput(label="E-mail Adresi", custom_id="email")
    birthday = TextInput(label="Doğum Tarihi", custom_id="birthday", placeholder="GG.AA.YYYY")
    info1 = TextInput(label="Bulunduğunuz Kurum Veya Ekip", custom_id="info1")
    info2 = TextInput(label="ÜNOG'u Nasıl Keşfettiniz?", custom_id="info2", required=False)

    async def on_submit(self, interaction: Interaction):
        unogMember = UnogMember(id=interaction.user.id,
                                name=self.name.value,
                                email=self.email.value,
                                birthday=self.birthday.value,
                                info1=self.info1.value,
                                info2=self.info2.value)
        await self._callback(interaction,unogMember)
        

#endregion

#region channelSelects

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

#endregion
