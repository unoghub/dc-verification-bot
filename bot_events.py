from discord.ext.commands import Bot
from discord import Member,Interaction,ButtonStyle,Guild,Object
from discord.app_commands import AppCommandError,CheckFailure,MissingPermissions,MissingRole,MissingAnyRole
from discord.ext import  tasks
from discord.ui import View,Button
from tinydb import  Query

from bot_modals import ApprovalModal
from bot_actions import approve_verification,deny_verification
import bot_globals

def setup_events():

    @bot_globals.UnogBot.event
    async def on_ready():

        print(f'{bot_globals.UnogBot.user} is connected')

        try:
            bot_globals.Server_Unog = bot_globals.UnogBot.get_guild(bot_globals.SERVERID_UNOG)
        except Exception as e:
            print(f"Failed to fetch the server with SERVER_ID:{bot_globals.SERVERID_UNOG}\n Error:{e} \n Exiting...")
            await bot_globals.UnogBot.close()
            return

        actives.start()

        try:
            await bot_globals.UnogBot.tree.sync(guild=bot_globals.Server_Unog)
            print('command sync success')
        except Exception as e:
            print(f'command sync fail:{e}')

    @bot_globals.UnogBot.tree.error
    async def on_command_error(interaction : Interaction, error):
        await interaction.response.send_message(error,ephemeral=True,delete_after=30)
        
    @bot_globals.UnogBot.event
    async def on_member_join(member : Member):
        user = bot_globals.TABLE_MEMBERS.search(Query().id == member.id)
        if user: #member is in db
            if user['approved'] == True:
                await member.add_roles(bot_globals.ROLEID_MEMBER)
        else: #new member is not in db,add a record
            bot_globals.TABLE_MEMBERS.insert({'id':member.id})

@tasks.loop(hours=1)
async def actives():
    """Loop function for every hour"""

    async def send_approval_modal(interaction: Interaction):
        for role in interaction.user.roles:
            if role == bot_globals.ROLEID_MEMBER:
                await interaction.response.send_message("Hesabınız veritabanımızda zaten onaylı gözükmektedir.", ephemeral=True, delete_after=10)
                return
        await interaction.response.send_modal(ApprovalModal())

    view = View(timeout=None)

    button1 = Button(style=ButtonStyle.primary, label="Onay Talebi İçin Tıkla!", custom_id="modal")
    button1.callback = send_approval_modal

    view.add_item(button1)
    bot_globals.UnogBot.add_view(view=view)

    view = View(timeout=None)

    buton1 = Button(style=ButtonStyle.green, label="Onayla", custom_id="onayla")
    buton1.callback = approve_verification

    buton2 = Button(style=ButtonStyle.red, label="Reddet", custom_id="reddet")
    buton2.callback = deny_verification

    view.add_item(buton1)
    view.add_item(buton2)

    bot_globals.UnogBot.add_view(view=view)
    print("Actives refreshed")
