import discord
from discord import app_commands
from discord.utils import get

dycel_id = 1099017318232764447

class SuggestionGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="suggestion", description="Suggestion-related commands")
    
    @app_commands.command(name="submit", description="Submit a suggestion to Dycel for something to add to the bot or server")
    async def suggestion_submit(self, interaction:discord.Interaction):
        found_dycel:bool = False
        for mem in interaction.guild.members:
            if mem.id == dycel_id:
                found_dycel = True
        if found_dycel == False:
            await interaction.response.send_message("Dycel is not in this server, so you can't use this command.", ephemeral=True)
            return
        embed = discord.Embed(
            title="Submit a suggestion",
            description="Click the button below to give Dycel a suggestion of something to add to the bot or server.",
            color=discord.Color.purple()
        )
        view = SuggestionGiveView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class SuggestionGiveModal(discord.ui.Modal):
    input_field: discord.ui.TextInput
    def __init__(self):
        super().__init__(title="Submit a suggestion")
        self.input_field = discord.ui.TextInput(
            label=f"Describe your suggestion here",
            placeholder="You should add...",
            style=discord.TextStyle.long,
            required=True
        )
        self.add_item(self.input_field)
    async def on_submit(self, interaction: discord.Interaction):
        dycel:discord.Member = get(interaction.guild.members, id=dycel_id)
        embed = discord.Embed(
            title="Suggestion",
            description=self.input_field.value,
            color=discord.Color.green()
        )
        embed.set_footer(icon_url=interaction.user.avatar.url, text=interaction.user.name)
        await interaction.response.send_message("Suggestion successfully submitted.", ephemeral=True)
        await dycel.send(embed=embed)

class SuggestionGiveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.interaction_handled = False
    
    @discord.ui.button(label="Submit a suggestion", style=discord.ButtonStyle.success)
    async def ReportABug(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.interaction_handled:
            await interaction.response.send_message("Alredy submitted a suggestion with this button. Run the command again to submit another suggestion.", ephemeral=True)
            return
        self.interaction_handled = True
        modal = SuggestionGiveModal()
        await interaction.response.send_modal(modal)

async def setup(bot):
    bot.tree.add_command(SuggestionGroup())