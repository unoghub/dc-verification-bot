from discord import Guild, Intents
from discord.ext.commands import Bot

from bot_events import setup_events
from bot_commands import setup_commands
import bot_globals 

bot_globals.UnogBot = Bot(command_prefix="!", intents=Intents.all())

setup_events()
setup_commands(bot_globals.UnogBot)

bot_globals.UnogBot.run(bot_globals.BOT_TOKEN)