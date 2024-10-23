from pathlib import Path
import pickle
import os

from discord import Intents, Client
from discord.app_commands import CommandTree

from application.types import Player

TOKEN = os.environ["DISCORD_BOT_TOKEN"]

intents = Intents.default()
client = Client(intents=intents)
tree = CommandTree(client=client)

DATABASE: dict[int, list[Player]] = {}

DATABASE_FILENAME = "discord_bot_database.pickle"


@client.event
async def on_ready():
    print("Bot ready.")
    try:
        await tree.sync()
    except Exception as e:
        print(e)


def run():
    try:
        database_file = Path(DATABASE_FILENAME)
        print(database_file.absolute(), database_file.exists())

        if database_file.exists():
            with open(DATABASE_FILENAME, "rb") as read_file:
                DATABASE = pickle.load(read_file)

        client.run(token=TOKEN)
    finally:
        with open(DATABASE_FILENAME, "wb") as write_file:
            pickle.dump(DATABASE, write_file)
