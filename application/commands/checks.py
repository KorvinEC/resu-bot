from discord import Interaction


# Check if the user is an admin
def is_admin(interaction: Interaction):
    return interaction.user.guild_permissions.administrator
