import os
from discord import Guild,Object
from discord.ext.commands import Bot
from tinydb import TinyDB
from tinydb.table import Table
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN : str = os.getenv('BOT_TOKEN')
DATABASE_UNOG = TinyDB('unog.json')
DATABASE_JAMS = TinyDB('jams.json')
TABLE_DENIES : Table = DATABASE_UNOG.table("DENIES")
TABLE_APPROVES : Table = DATABASE_UNOG.table("APPROVES")
TABLE_MEMBERS : Table = DATABASE_UNOG.table("MEMBERS")
COLORS_UNOG = 0x7ac943, 0x2193c7,0x563795
USERID_AKDENIZ = 385887296555319296
USERID_KHANO = 222094201356025857
TEXTCHANNELID_VERIFICATION_PANEL =os.getenv('TEXTCHANNELID_VERIFICATION_PANEL') # Onay Paneli
TEXTCHANNELID_VERIFICATION = os.getenv('TEXTCHANNELID_VERIFICATION') # Onay-Kayıt kanalı
TEXTCHANNELID_WELCOME = os.getenv('TEXTCHANNELID_WELCOME') # Hoşgeldin kanalı
ROLEID_BOTDEV = os.getenv('ROLEID_BOTDEV')
ROLEID_MEMBER = os.getenv('ROLEID_MEMBER') # Üye
ROLEID_VOLUNTEER = os.getenv('ROLEID_VOLUNTEER') # Gönüllü
ROLEID_APPROVER = os.getenv('ROLEID_APPROVER') # Alım Sorumlusu
ROLEID_DIRECTOR = os.getenv('ROLEID_DIRECTOR') # Direktör 
SERVERID_UNOG = int(os.getenv('SERVERID_UNOG')) # Sunucu ID
GUILD_UNOG = Object(id=SERVERID_UNOG)
WELCOME_MESSAGES = "\ud83c\udf89 Ho\u015f geldin %user%! Aram\u0131za kat\u0131ld\u0131\u011f\u0131n i\u00e7in mutluyuz. \ud83c\udf89  \nHemen yerini al ve keyifli zaman ge\u00e7ir! \ud83d\ude80  \n%split%  \n\u2705 Tebrikler %user%! Onayland\u0131n ve art\u0131k tam anlam\u0131yla toplulu\u011fumuzun bir par\u00e7as\u0131s\u0131n!  \n\u0130yi e\u011flenceler! \u2728  \n%split%  \n\ud83d\udc4b Merhaba %user%! Toplulu\u011fumuza kat\u0131ld\u0131\u011f\u0131n i\u00e7in te\u015fekk\u00fcrler.  \nKendini evinde hissetmen i\u00e7in buraday\u0131z. \ud83c\udf88  \n%split%  \n\ud83c\udf8a %user%, ba\u015far\u0131yla onayland\u0131n! \ud83c\udf8a  \nArt\u0131k t\u00fcm i\u00e7eriklere eri\u015febilirsin. Tad\u0131n\u0131 \u00e7\u0131kar! \ud83c\udf1f  \n%split%  \n\ud83e\ude84 Hey %user%! Aram\u0131za kat\u0131ld\u0131\u011f\u0131n i\u00e7in \u00e7ok mutluyuz!  \nHer \u015fey senin i\u00e7in haz\u0131r, haydi ba\u015flayal\u0131m. \ud83c\udfde\ufe0f  \n%split%  \n\u2728 %user%, art\u0131k resmi olarak bizden birisin! \u2728  \nHarika vakit ge\u00e7irmen dile\u011fiyle. \ud83d\ude04  \n%split%  \n\ud83c\udf1f Ho\u015f geldin %user%! Burada harika an\u0131lar biriktirece\u011fiz.  \nKendini evinde hisset! \ud83c\udf89  \n%split%  \n\u2705 %user%, onayland\u0131n! Art\u0131k bizim bir par\u00e7am\u0131zs\u0131n.  \n\u015eimdi e\u011flence ba\u015flas\u0131n! \ud83d\udc83  \n%split%  \n\ud83c\udf89 Hey %user%! Buras\u0131 art\u0131k senin ikinci evin.  \nHemen ke\u015ffetmeye ba\u015fla! \ud83c\udfe1  \n%split%  \n\ud83d\ude80 %user%, onayland\u0131! \u015eimdi macera ba\u015fl\u0131yor.  \nHarika zaman ge\u00e7ir! \ud83c\udf20  \n%split%  \n\ud83c\udf88 Ho\u015f geldin %user%! Toplulu\u011fumuz seninle daha g\u00fc\u00e7l\u00fc.  \nHaydi ba\u015flayal\u0131m! \ud83d\udd25  \n%split%  \n\u2705 Harika haber %user%! Art\u0131k onayl\u0131 bir \u00fcyesin.  \nAram\u0131za ho\u015f geldin! \ud83d\ude0a  \n%split%  \n\ud83c\udf89 Selam %user%! Seni burada g\u00f6rmek harika.  \nE\u011flenmeye haz\u0131r ol! \ud83c\udf8a  \n%split%  \n\u2728 %user%, toplulu\u011fumuzun bir par\u00e7as\u0131 oldu\u011fun i\u00e7in \u00e7ok mutluyuz.  \nKeyifli vakitler! \ud83c\udf1f  \n%split%  \n\ud83c\udf8a Hey %user%! Art\u0131k tamamen buradas\u0131n.  \nYeni maceralar seni bekliyor! \ud83d\ude80  \n%split%  \n\ud83c\udf1f Ho\u015f geldin %user%! Her zaman burada seni destekleyen bir ekip var.  \nHaydi ba\u015flayal\u0131m! \ud83e\ude84  \n%split%  \n\u2705 %user%, art\u0131k resmi bir \u00fcyemizsin!  \nHadi e\u011flence ba\u015flas\u0131n! \u2728  \n%split%  \n\ud83c\udf89 Merhaba %user%! Seni aram\u0131zda g\u00f6rmek harika.  \nHemen sohbete kat\u0131l! \ud83d\udde8\ufe0f  \n%split%  \n\ud83c\udf88 %user%, toplulu\u011fumuza ho\u015f geldin!  \nBuras\u0131 art\u0131k senin de evin. \ud83c\udfe1  \n%split%  \n\u2728 Ho\u015f geldin %user%! Bug\u00fcn harika bir g\u00fcn \u00e7\u00fcnk\u00fc sen geldin.  \nKeyifli vakitler dileriz! \ud83c\udf1f"


UnogBot : Bot = None
Server_Unog : Guild = None