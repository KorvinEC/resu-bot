from discord import Interaction, Embed, Color
from discord.app_commands import (
    autocomplete,
    Choice,
    check,
    CommandTree
)

from application.database import DATABASE
from application.commands.checks import is_admin


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


@check(is_admin)
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


def setup(tree: CommandTree):
    print(f"Setting up {kick.__name__} command")
    tree.command(name="kick", description="Kick from current tournment")(kick)
