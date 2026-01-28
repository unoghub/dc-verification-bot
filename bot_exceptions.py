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

class YoureNotVerifiedException(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_MEMBER}> rolüne sahip olmanız, bunun için de onaylanmış olmanız gerekmektedir."):
        super().__init__(message)

class TargetUserIsNullException(AppCommandError):
    def __init__(self, message=f"Kullanıcı verisi null/girilmemiş."):
        super().__init__(message)

class ThisUserIsAlreadyVerifiedException(AppCommandError):
    def __init__(self, message=f"Bu kullanıcı zaten onaylı.(<@&{bot_globals.ROLEID_MEMBER}>)"):
        super().__init__(message)

class YoureAlreadyInJamException(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanabilmek için bir jame katılmamış olmanız gerekiyor."):
        super().__init__(message)

class YouMustJoinJamException(AppCommandError):
    def __init__(self, message=f"Bu komutu yapabilmek için önce bir jame katılmalısınız."):
        super().__init__(message)

class YouMustBeApproverException(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_APPROVER}> rolüne sahip olmanız gerekmektedir."):
        super().__init__(message)

class YouMustHaveTopAccessException(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için:\n <@&{bot_globals.ROLEID_DIRECTOR}> veya,\n <@&{bot_globals.ROLEID_BOTDEV}>\n rollerinden birine sahip olmanız gerekmektedir."):
        super().__init__(message)

class YouMustBeBotDevException(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_BOTDEV}> rolüne sahip olmanız gerekmektedir."):
        super().__init__(message)

class YouMustNotBeInJamTeamException(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanabilmek için bir jam ekibinde olmamanız gerekiyor."):
        super().__init__(message)

class YouMustBeInJamTeamException(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanabilmek için bir jam ekibinde olmanız gerekiyor."):
        super().__init__(message)

class YouMustBeJamModException(AppCommandError):
    def __init__(self, message=f"Bu komutu kullanmak için <@&{bot_globals.ROLEID_JAM_MOD}> rolüne sahip olmanız gerekmektedir."):
        super().__init__(message)

class JamAlreadyPresentException(AppCommandError):
    def __init__(self, message="Şuanda devam etmekte olan bir jam mevcut olduğu için işlem gerçekleştirilemiyor.\n `/jam-bitir` komutuyla mevcut jami bitirmeniz gerekmektedir."):
        super().__init__(message)

class JamNotPresentException(AppCommandError):
    def __init__(self, message="Mevcut bir jam bulunmamaktadır."):
        super().__init__(message)

class YouMustJoinJamException(AppCommandError):
    def __init__(self, message="Bu komutu kullanabilmek için mevcut jame katılmış olmanız gerekiyor."):
        super().__init__(message)

class YouAlreadyInJamException(AppCommandError):
    def __init__(self, message="Mevcut jame zaten kayıtlısınız."):
        super().__init__(message)

class JamTeamNameAlreadyPresentException(AppCommandError):
    def __init__(self, message="Bu ekip adı kullanılıyor."):
        super().__init__(message)

class JamTeamNotExistsException(AppCommandError):
    def __init__(self, message="Böyle bir ekip bulunmamakta."):
        super().__init__(message)

class JamCategoryNotPresentException(AppCommandError):
    def __init__(self, message="Bu jamin kategorisi bulunamıyor."):
        super().__init__(message)

class JamTeamJoinRequestAlreadySentException(AppCommandError):
    def __init__(self, message="Bu jame katılım isteği zaten gönderilmiştir."):
        super().__init__(message)

class YouAlreadyInRequestedJamTeamException(AppCommandError):
    def __init__(self, message="Katılım isteği göndermeye çalıştığınız ekipte zaten bulunuyorsunuz."):
        super().__init__(message)

class YourJamTeamSubmissionIsNotUniqueException(AppCommandError):
    def __init__(self, message="Ekibinizin submission URL'si bir başka takım tarafından yapılmıştır. Bir aksilik olduğunu düşünüyorsanız moderatörlere bilirebilirsiniz."):
        super().__init__(message)

class YourJamTeamAlreadySubmittedException(AppCommandError):
    def __init__(self, message="Ekibiniz oyununu öncesinden göndermiştir. Her ekip sadece bir kere jamini gönderebilir."):
        super().__init__(message)

class YouAreNotJamTeamLeaderException(AppCommandError):
    def __init__(self, message="Bir ekip lideri değilsiniz."):
        super().__init__(message)

class TargetUserIsNotInJam(AppCommandError):
    def __init__(self, message="Hedef kullanıcı bir jam katılımcısı değildir."):
        super().__init__(message)

class TargetUserIsNotVerified(AppCommandError):
    def __init__(self, message="Hedef kullanıcı bir onaylı üye değil."):
        super().__init__(message)

class TargetUserIsAlreadyInYourJamTeam(AppCommandError):
    def __init__(self, message="Hedef kullanıcı zaten ekibinizde."):
        super().__init__(message)

class TargetUserIsAlreadyVerified(AppCommandError):
    def __init__(self, message="Hedef kullanıcı zaten onaylı."):
        super().__init__(message)

class TargetUserIsNotVerified(AppCommandError):
    def __init__(self, message="Hedef kullanıcı onaylı üye değildir."):
        super().__init__(message)

class TargetUserIsNotInJamTeam(AppCommandError):
    def __init__(self, message="Hedef kullanıcı bir jam ekibinde değil."):
        super().__init__(message)

class ThisJamParticipantDataIsCorruptException(AppCommandError):
    def __init__(self, message="Bu katılımcının veritabanı kaydı hatalı."):
        super().__init__(message)

class ThisParticipantNotInServerException(AppCommandError):
    def __init__(self, message="Bu katılımcı sunucuda değil."):
        super().__init__(message)

class ThisJamTeamsVoiceChannelNotPresentException(AppCommandError):
    def __init__(self, message="Bu jam ekibinin ses kanalı silinmiş."):
        super().__init__(message)

class TargetUserIsNotJoinRequestingYourJamTeam(AppCommandError):
    def __init__(self, message="Hedef kullanıcının bulunduğunuz ekibe göndermiş olduğu bir katılım isteği yoktur."):
        super().__init__(message)

class ThisGivenJamTeamNameDoesNotExistException(AppCommandError):
    def __init__(self, message="Girilen isimde bir jam ekibi bulunmamaktadır."):
        super().__init__(message)

class UserNewNameCouldNotBeEmpty(AppCommandError):
    def __init__(self, message="Yeni isim boş olmamalı."):
        super().__init__(message)

class UserNewNameMustBeAlphanumeric(AppCommandError):
    def __init__(self, message="Yeni isim boş olmamalı."):
        super().__init__(message)

class AttachedFileIsNotCsvException(AppCommandError):
    def __init__(self, message="Eklenen dosya .csv formatında olmalıdır."):
        super().__init__(message)