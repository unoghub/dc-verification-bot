from discord.ext.commands import Context
from discord import Interaction
from discord.ext.commands import Bot
from discord.app_commands import AppCommandError
import bot_globals

async def reply_no_permission(context: Context | Interaction):

    if type(context) is Context:
        await context.reply('Bu komutu kullanmaya yetkiniz yok.', ephemeral=True, delete_after=30)
    elif type(context) is Interaction:
        await context.response.send_message('Bu komutu kullanmaya yetkiniz yok.', ephemeral=True, delete_after=30)

class UserNotApproved(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_MEMBER}> rolüne sahip olmanız, bunun için de onaylanmış olmanız gerekmektedir."):
        super().__init__(message)
    pass

class UserNotApprover(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_APPROVER}> rolüne sahip olmanız gerekmektedir."):
        super().__init__(message)
    pass

class UserNotHasTopAccess(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için:\n <@&{bot_globals.ROLEID_DIRECTOR}> veya,\n <@&{bot_globals.ROLEID_BOTDEV}>\n rollerinden birine sahip olmanız gerekmektedir."):
        super().__init__(message)
    pass


class UserNotBotDev(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_BOTDEV}> rolüne sahip olmanız gerekmektedir."):
        super().__init__(message)
    pass

class UserAlreadyInATeam(AppCommandError):
    def __init__(self, message=f"Halihazırda bir jam ekibine kayıtlısınız."):
        super().__init__(message)
    pass

class UserNotJamMod(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_JAM_MOD}> rolüne sahip olmanız gerekmektedir."):
        super().__init__(message)
    pass

class JamAlreadyPresent(AppCommandError):
    def __init__(self, message="Şuanda devam etmekte olan bir jam olduğundan ötürü jam yaratılamıyor. Bitirme komutunu kullanmanız gerekmektedir."):
        super().__init__(message)
    pass

class JamNotParticipating(AppCommandError):
    def __init__(self, message="Bu komutu kullanabilmek için mevcut jame katılmış olmanız gerekiyor."):
        super().__init__(message)
    pass

class JamAlreadyParticipating(AppCommandError):
    def __init__(self, message="Mevcut jame zaten kayıtlısınız."):
        super().__init__(message)
    pass

class JamTeamAlreadyPresent(AppCommandError):
    def __init__(self, message="Bu ekip adı kullanılıyor."):
        super().__init__(message)
    pass

class NoJamPresent(AppCommandError):
    def __init__(self, message="Mevcut bir jam bulunmamaktadır."):
        super().__init__(message)
    pass