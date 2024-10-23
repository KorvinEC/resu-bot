import os

from discord import Intents, Client, Interaction
from discord.app_commands import CommandTree

from application.database import DATABASE
from application.commands import (
    setup_add_player,
    setup_create_tournment_thread,
    setup_generate_teams,
    setup_kick,
    setup_list_players,
    setup_participate,
)


TOKEN = os.environ["DISCORD_BOT_TOKEN"]

intents = Intents.default()
client = Client(intents=intents)
tree = CommandTree(client=client)

for setup in (
    setup_list_players,
    setup_add_player,
    setup_create_tournment_thread,
    setup_generate_teams,
    setup_kick,
    setup_participate,
):
    setup(tree)


@tree.command(name="test")
async def test( interaction: Interaction):
    await interaction.response.send_message(content="Test")


@client.event
async def on_ready():
    print("Bot ready")
    try:
        await tree.sync()
    except Exception as e:
        print(f"Exception: {e}")


# TODO: Doesn't work
@client.event
async def on_guild_available(guild):
    # Sync the commands with the guild when the bot is ready
    print(f"Sync tree for guild: {guild}")
    await tree.sync(guild=guild)


def run():
    # Load command files
    try:
        DATABASE.load_from_pickle()
        client.run(token=TOKEN)
    finally:
        DATABASE.dump_pickle()


if __name__ == "__main__":
    run()
