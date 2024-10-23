from discord import Interaction, Embed, Color
from discord.app_commands import CommandTree

from application.database import DATABASE


async def list_players(interaction: Interaction):
    if interaction.channel_id is None:
        embed = Embed(
            title="Error", description="Chaneel does not have id", color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if interaction.channel_id not in DATABASE.data:
        embed = Embed(
            title="Error",
            description="This channel does not have players",
            color=Color.red(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = Embed(title="Players", color=Color.green())

    for player in DATABASE.data[interaction.channel_id]:
        embed.add_field(
            name=player.uuid,
            value=f"{player.discord_mention} {player.discord_opgg_url} {player.discord_roles}",
            inline=False,
        )

    await interaction.response.send_message(embed=embed)
    return


def setup(tree: CommandTree):
    print(f"Setting up {list_players.__name__} command")
    tree.command(name="list_players", description="List players in current thread")(list_players)

