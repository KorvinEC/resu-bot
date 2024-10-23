from discord import Interaction, Embed, Color, User
from discord.app_commands import check, CommandTree

from application.types import Player, RolesType
from application.commands.checks import is_admin
from application.database import DATABASE


@check(is_admin)
async def add_player(
    interaction: Interaction,
    user: User,
    opgg_url: str,
    primary_role: RolesType,
    secondary_role: RolesType | None = None,
):
    # Create a thread under the command message
    if interaction.channel_id is None:
        embed = Embed(title="Error", description="Chaneel does not have id", color=Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Create a thread under the command message
    if interaction.channel_id not in DATABASE.data:
        embed = Embed(title="Error", description="No such channel in database", color=Color.red())
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

    DATABASE.data[interaction.channel_id].append(player)
    DATABASE.dump_pickle()

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
    print("Setting up add_player command")
    tree.command(name="add_player", description="Add player to current thread")(add_player)
