from discord.ext.commands import Context
from discord import Interaction
from discord.ext.commands import Bot

async def reply_no_permission(context: Context | Interaction):

    if type(context) is Context:
        await context.reply('Bu komutu kullanmaya yetkiniz yok.', ephemeral=True, delete_after=30)
    elif type(context) is Interaction:
        await context.response.send_message('Bu komutu kullanmaya yetkiniz yok.', ephemeral=True, delete_after=30)

class JamAlreadyContains(Exception):
    def __init__(self, message="Bu kısa isimde başka bir jam mevcut olduğundan ötürü jam yaratılamıyor."):
        super().__init__(message)
    pass