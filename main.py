from pathlib import Path
import pickle
from random import randint
import randomname
import os

from discord import Intents, Client, Interaction, Embed, Color, User
from discord.app_commands import CommandTree, autocomplete, describe, Choice
from discord.channel import TextChannel

from application.types import Player, RolesType, PrimaryRoleType, SecondaryRoleType
from application.create_teams import create_teams

TOKEN = os.environ["DISCORD_BOT_TOKEN"]

intents = Intents.default()
client = Client(intents=intents)
tree = CommandTree(client=client)

DATABASE_FILENAME = "discord_bot_database.pickle"

DATABASE: dict[int, list[Player]] = {}


@client.event
async def on_ready():
    print("Bot ready.")
    try:
        await tree.sync()
    except Exception as e:
        print(e)


@tree.command(name="create_tournment_thread", description="Create tournment thread")
@describe(name="Tournment name")
async def create_tournment_thread(interaction: Interaction, name: str | None = None):
    # Create a thread under the command message

    if not interaction.channel:
        embed = Embed(
            title="Error", description="Channel does not exists", color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if not isinstance(interaction.channel, TextChannel):
        embed = Embed(
            title="Error", description="Not a text channel", color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if name is None:
        name = randomname.generate(sep=" ")

    thread = await interaction.channel.create_thread(
        name=name,
        message=interaction.message,
        auto_archive_duration=60,  # Duration in minutes
    )
    DATABASE[thread.id] = []

    with open(DATABASE_FILENAME, "wb") as file:
        pickle.dump(DATABASE, file)

    embed = Embed(
        title="Success",
        description=f"Tournment thread created: {thread.mention}",
        color=Color.green(),
    )

    await interaction.response.send_message(embed=embed)


@tree.command(
    name="participate", description="Participate in current current thread tournment"
)
@describe(opgg_url="OpGG link", primary_role="Primary role")
async def participate(
    interaction: Interaction,
    opgg_url: str,
    primary_role: PrimaryRoleType,
    secondary_role: SecondaryRoleType = None,
):
    if interaction.channel_id is None:
        embed = Embed(
            title="Error", description="Chaneel does not have id", color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    warning_embed = None
    if primary_role == secondary_role:
        warning_embed = Embed(
            title="Warining",
            description="Primary and secondary role can't be identical. Only primary is selected.",
            color=Color.yellow(),
        )

    player = Player.create_and_validate(
        interaction.user.id, opgg_url, primary_role, secondary_role
    )

    DATABASE[interaction.channel_id].append(player)

    with open(DATABASE_FILENAME, "wb") as file:
        pickle.dump(DATABASE, file)

    embdes = [
        Embed(
            title="Player added",
            description=f"`{player.uuid}` {player.discord_mention} {player.discord_opgg_url} {player.discord_roles}",
            color=Color.green(),
        )
    ]

    if warning_embed:
        embdes.append(warning_embed)

    await interaction.response.send_message(embeds=embdes)


@tree.command(
    name="generate_team", description="Generate teams from people on this thread"
)
async def generate_team(interaction: Interaction):
    if interaction.channel_id is None:
        embed = Embed(
            title="Error", description="Chaneel does not have id", color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    players = DATABASE.get(interaction.channel_id, None)

    if players is None:
        embed = Embed(
            title="Error", description="No players in database", color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    teams, leftover_players = create_teams(players)

    embeds: list[Embed] = []

    for team in teams:
        description = []

        for role, player in team.items():
            if player:
                description.append(
                    f"`{role}` - {player.discord_mention} {player.discord_opgg_url} {player.discord_roles}"
                )
            else:
                description.append(f"`{role}` - No player")

        embeds.append(
            Embed(
                title=f"Team: `{randomname.generate(sep=' ')}`",
                description="\n".join(description),
                color=Color(randint(0, 16777215)),
            )
        )

    if not leftover_players:
        await interaction.response.send_message(embeds=embeds)
        return

    description = "\n".join((
        f"{player.discord_mention} {player.discord_opgg_url} {player.discord_roles}"
        for player in leftover_players
    ))

    embeds.append(
        Embed(title="Leftover players", description=description, color=Color.red())
    )

    await interaction.response.send_message(embeds=embeds)
    return


@tree.command(name="add_player", description="Add player to current thread")
async def add_player(
    interaction: Interaction,
    user: User,
    opgg_url: str,
    primary_role: RolesType,
    secondary_role: RolesType | None = None,
):
    # Create a thread under the command message
    if interaction.channel_id is None:
        embed = Embed(
            title="Error", description="Chaneel does not have id", color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    warning_embed = None
    if primary_role == secondary_role:
        warning_embed = Embed(
            title="Warining",
            description="Primary and secondary role can't be identical. Only primary is selected.",
            color=Color.yellow(),
        )

    player = Player.create_and_validate(user.id, opgg_url, primary_role, secondary_role)

    DATABASE[interaction.channel_id].append(player)

    with open(DATABASE_FILENAME, "wb") as file:
        pickle.dump(DATABASE, file)

    embdes = [
        Embed(
            title="Player added",
            description=f"`{player.uuid}` {player.discord_mention} {player.discord_opgg_url} {player.discord_roles}",
            color=Color.green(),
        )
    ]

    if warning_embed:
        embdes.append(warning_embed)

    await interaction.response.send_message(embeds=embdes)


@tree.command(name="list_players", description="List players in current thread")
async def list_players(interaction: Interaction):
    if interaction.channel_id is None:
        embed = Embed(
            title="Error", description="Chaneel does not have id", color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if interaction.channel_id not in DATABASE:
        embed = Embed(
            title="Error",
            description="This channel does not have players",
            color=Color.red(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = Embed(title="Players", color=Color.green())

    for player in DATABASE[interaction.channel_id]:
        embed.add_field(
            name=player.uuid,
            value=f"{player.discord_mention} {player.discord_opgg_url} {player.discord_roles}",
            inline=False,
        )

    await interaction.response.send_message(embed=embed)
    return


async def kick_autocomplete(
    interaction: Interaction, current: str
) -> list[Choice[str]]:
    if interaction.channel_id is None:
        embed = Embed(
            title="Error", description="Chaneel does not have id", color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return []

    if interaction.channel_id not in DATABASE:
        embed = Embed(
            title="Error",
            description="This channel does not have players",
            color=Color.red(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return []

    options = [
        str(player.uuid)
        for player in DATABASE[interaction.channel_id]
        if current in str(player.uuid)
    ]
    return [Choice(name=item, value=item) for item in options]


@tree.command(name="kick", description="Kick from current tournment")
@autocomplete(user_uuid=kick_autocomplete)
async def kick(
    interaction: Interaction,
    user_uuid: str,
):
    if interaction.channel_id is None:
        embed = Embed(
            title="Error", description="Chaneel does not have id", color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if interaction.channel_id not in DATABASE:
        embed = Embed(
            title="Error",
            description="This channel does not have players",
            color=Color.red(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    for player in DATABASE[interaction.channel_id]:
        if str(player.uuid) != user_uuid:
            continue

        DATABASE[interaction.channel_id].remove(player)

        embed = Embed(
            title="Success",
            description=f"Player `{player.uuid}` {player.discord_mention} was removed",
            color=Color.green(),
        )
        await interaction.response.send_message(embed=embed)
        return
    else:
        embed = Embed(
            title="Failure",
            description=f"Player with UUID `{user_uuid}` not found",
            color=Color.red(),
        )
        await interaction.response.send_message(embed=embed)
        return


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
