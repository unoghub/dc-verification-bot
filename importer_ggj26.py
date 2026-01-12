import csv
from io import StringIO
from discord import Interaction,Attachment
from discord import app_commands
import bot_globals
import tinydb

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

            print(f"Row {row_number}: {name_surname} {email} {birthday} {preference} {discord_username} {teamname}")

        await interaction.response.send_message(
            "CSV processed successfully ✅",
            ephemeral=True
        )