from discord.ext.commands import Context


async def reply_no_permission(context: Context):
    await context.reply('Bu komutu kullanmaya yetkiniz yok.', ephemeral=True, delete_after=30)