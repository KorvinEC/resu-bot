import randomname

from discord import Interaction, Embed, Color
from discord.app_commands import describe, check, CommandTree
from discord.channel import TextChannel

from application.commands.checks import is_admin
from application.database import DATABASE


@check(is_admin)
@describe(name="Tournment name")
async def create_tournment_thread(interaction: Interaction, name: str | None = None):
    # Create a thread under the command message

    if not interaction.channel:
        embed = Embed(title="Error", description="Channel does not exists", color=Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if not isinstance(interaction.channel, TextChannel):
        embed = Embed(title="Error", description="Not a text channel", color=Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if name is None:
        name = randomname.generate(sep=" ")

    thread = await interaction.channel.create_thread(
        name=name,
        message=interaction.message,
        auto_archive_duration=60,  # Duration in minutes
    )
    DATABASE.data[thread.id] = []
    DATABASE.dump_pickle()

    embed = Embed(
        title="Success",
        description=f"Tournment thread created: {thread.mention}",
        color=Color.green(),
    )

    await interaction.response.send_message(embed=embed)


def setup(tree: CommandTree):
    print("Setting up create_tournment_thread command")
    tree.command(name="create_tournment_thread", description="Create tournment thread")(create_tournment_thread)
