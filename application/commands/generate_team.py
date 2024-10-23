from random import randint
import randomname

from discord import Interaction, Embed, Color
from discord.app_commands import check, CheckFailure, CommandTree

from application.commands.checks import is_admin
from application.create_teams import create_teams


@check(is_admin)
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

    description = "\n".join(
        (
            f"{player.discord_mention} {player.discord_opgg_url} {player.discord_roles}"
            for player in leftover_players
        )
    )

    embeds.append(
        Embed(title="Leftover players", description=description, color=Color.red())
    )

    await interaction.response.send_message(embeds=embeds)
    return


async def is_admin_error(interaction: Interaction, error):
    if isinstance(error, CheckFailure):
        await interaction.response.send_message(
            embed=Embed(
                title="Error",
                description="You do not have permission to use this command.",
                color=Color.red(),
            ),
            ephemeral=True,
        )


def setup(tree: CommandTree):
    print(f"Setting up {generate_team.__name__} command")
    gt = tree.command(
        name="generate_team", description="Generate teams from people on this thread"
    )(generate_team)
    gt.error(is_admin_error)
