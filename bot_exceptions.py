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

class UserNotVerified(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_MEMBER}> rolüne sahip olmanız, bunun için de onaylanmış olmanız gerekmektedir."):
        super().__init__(message)

class UserIsNull(AppCommandError):
    def __init__(self, message=f"Kullanıcı verisi null/girilmemiş."):
        super().__init__(message)

class UserAlreadyVerified(AppCommandError):
    def __init__(self, message=f"Bu kullanıcı zaten onaylı.(<@&{bot_globals.ROLEID_MEMBER}>)"):
        super().__init__(message)

class UserAlreadyInJam(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanabilmek için bir jame katılmamış olmanız gerekiyor."):
        super().__init__(message)

class UserNotInJam(AppCommandError):
    def __init__(self, message=f"Bu komutu yapabilmek için önce bir jame katılmalısınız."):
        super().__init__(message)

class UserNotApprover(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_APPROVER}> rolüne sahip olmanız gerekmektedir."):
        super().__init__(message)

class UserNotHasTopAccess(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için:\n <@&{bot_globals.ROLEID_DIRECTOR}> veya,\n <@&{bot_globals.ROLEID_BOTDEV}>\n rollerinden birine sahip olmanız gerekmektedir."):
        super().__init__(message)

class UserNotBotDev(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_BOTDEV}> rolüne sahip olmanız gerekmektedir."):
        super().__init__(message)

class UserAlreadyInJamTeam(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanabilmek için bir jam ekibinde olmamanız gerekiyor."):
        super().__init__(message)

class UserNotInJamTeam(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanabilmek için bir jam ekibinde olmanız gerekiyor."):
        super().__init__(message)

class UserNotJamMod(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_JAM_MOD}> rolüne sahip olmanız gerekmektedir."):
        super().__init__(message)

class JamAlreadyPresent(AppCommandError):
    def __init__(self, message="Şuanda devam etmekte olan bir jam mevcut olduğu için işlem gerçekleştirilemiyor.\n `/jam-bitir` komutuyla mevcut jami bitirmeniz gerekmektedir."):
        super().__init__(message)

class JamNotPresent(AppCommandError):
    def __init__(self, message="Mevcut bir jam bulunmamaktadır."):
        super().__init__(message)

class JamNotParticipating(AppCommandError):
    def __init__(self, message="Bu komutu kullanabilmek için mevcut jame katılmış olmanız gerekiyor."):
        super().__init__(message)

class JamAlreadyParticipating(AppCommandError):
    def __init__(self, message="Mevcut jame zaten kayıtlısınız."):
        super().__init__(message)

class JamTeamAlreadyPresent(AppCommandError):
    def __init__(self, message="Bu ekip adı kullanılıyor."):
        super().__init__(message)

class JamTeamNotPresent(AppCommandError):
    def __init__(self, message="Bir ekibiniz yok."):
        super().__init__(message)

class JamCategoryNotPresent(AppCommandError):
    def __init__(self, message="Bu jamin kategorisi bulunamıyor."):
        super().__init__(message)