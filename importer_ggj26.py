import csv
from io import StringIO
from discord import Interaction,Attachment
from discord import app_commands
import bot_globals
import tinydb
from tinydb import Query
from bot_models import UnogMember
from bot_globals import TABLE_JAM_FORMS
class ImporterGGJ26():
    """ Teams Importer for GGJ26 """
    async def run(interaction : Interaction, attachment : Attachment):
        # 1️⃣ Read file bytes from Discord
        file_bytes: bytes = await attachment.read()

        # 2️⃣ Decode bytes → text
        text = file_bytes.decode("utf-8-sig")  # utf-8-sig handles Excel BOM

        # 3️⃣ Create text stream
        csv_stream = StringIO(text)

        # 4️⃣ Read CSV
        reader = csv.DictReader(csv_stream)

        for row_number, row in enumerate(reader, start=1):
            # Each row is dict[str, str]
            name_surname = row["Adınız Soyadınız"]
            email = row["E-posta adresiniz"]
            birthday = row["Doğum Tarihi"]
            preference = row["Katılım tercihiniz nedir?"]
            discord_username = row["Discord kullanıcı adınız"]
            teamname = row["Takımınızın adı var mı?"]
            if preference == "Online (ÜNOG Discord)":
                TABLE_JAM_FORMS.upsert({"name":name_surname.strip().title(),"email":email.strip(),"birthday":birthday,"username":discord_username.strip().removeprefix("@"),"teamName":teamname.strip().lower().replace(" ","-")},Query().username == discord_username)

        await interaction.response.send_message(
            "İçe aktarım başarılı ✅",
            ephemeral=True,delete_after=30
        )