from discord import Member,Interaction,Object
from tinydb import  Query
from bot_actions import actives,approve_user,create_jam_participant
import bot_globals
from bot_commands import setup_commands

def setup_events():

    @bot_globals.UnogBot.event
    async def setup_hook():
        # Load cogs here
        await setup_commands(bot_globals.UnogBot)
        commands = await bot_globals.UnogBot.tree.sync(guild=Object(id=bot_globals.SERVERID_UNOG))

        print("=== SYNC RESULT ===")
        for cmd in commands:
            print(f"Synced: {cmd.name} ({cmd.id})")
        print(f"Total synced: {len(commands)}")

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
            await bot_globals.UnogBot.tree.sync(guild=Object(id=bot_globals.SERVERID_UNOG))
            print('command sync success')
        except Exception as e:
            print(f'command sync fail:{e}')

    @bot_globals.UnogBot.tree.error
    async def on_app_command_error(interaction : Interaction, error):
        # print(f"ErrorType:{type(error)}\n Message:{error}")
        # await interaction.response.send_message(f"❌ **Hata:**\n {error}",ephemeral=True,delete_after=30)
        if interaction.response.is_done():
            # Already responded or deferred → use followup
            await interaction.followup.send(
                f"❌ **Hata:**\n{error}",
                ephemeral=True,
                delete_after=30
            )
        else:
            # Not responded yet → normal response
            await interaction.response.send_message(
                f"❌ **Hata:**\n{error}",
                ephemeral=True,
                delete_after=30
            )
        
    @bot_globals.UnogBot.event
    async def on_member_join(member : Member):
        
        form_doc = bot_globals.TABLE_JAM_FORMS.get(Query().username == member.name)
        if form_doc:
            await approve_user(None,member,form_doc.get('name'),form_doc.get('email'),form_doc.get('birthday'),"Jam formundan katıldım")
            await create_jam_participant(member.id)
        else:
            user = bot_globals.TABLE_MEMBERS.get(Query().id == member.id)
            if user: #member is in db
                memberRole = bot_globals.Server_Unog.get_role(bot_globals.ROLEID_MEMBER)
                await member.add_roles(memberRole)
                await member.edit(nick=user.get('name'))
