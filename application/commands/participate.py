import pickle

from discord import Interaction, Embed, Color
from discord.app_commands import (
    describe,
)

from application.commands import tree, DATABASE, DATABASE_FILENAME
from discord import Interaction, Embed, Color
from discord.app_commands import describe, CommandTree

from application.types import Player, PrimaryRoleType, SecondaryRoleType


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


def setup(tree: CommandTree):
    print(f"Setting up {participate.__name__} command")
    tree.command(name="participate", description="Participate in current current thread tournment")(participate)
