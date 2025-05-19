import discord
from discord import app_commands
from discord.utils import get

dycel_id = 1099017318232764447

class BugGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="bug", description="Bug-related commands")
    
    @app_commands.command(name="report", description="Report a bot bug to Dycel")
    async def bug_report(self, interaction:discord.Interaction):
        found_dycel:bool = False
        for mem in interaction.guild.members:
            if mem.id == dycel_id:
                found_dycel = True
        if found_dycel == False:
            await interaction.response.send_message("Dycel is not in this server, so you can't use this command.", ephemeral=True)
            return
        embed = discord.Embed(
            title="Report a bug",
            description="Click the button below to report a bug about the bot to Dycel.",
            color=discord.Color.purple()
        )
        view = BugReportView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class BugReportModal(discord.ui.Modal):
    input_field: discord.ui.TextInput
    def __init__(self):
        super().__init__(title="Report a bug")
        self.input_field = discord.ui.TextInput(
            label=f"Describe the bug here",
            placeholder="The bug is that...",
            style=discord.TextStyle.long,
            required=True
        )
        self.add_item(self.input_field)
    async def on_submit(self, interaction: discord.Interaction):
        dycel:discord.Member = get(interaction.guild.members, id=dycel_id)
        embed = discord.Embed(
            title="Bug report",
            description=self.input_field.value,
            color=discord.Color.red()
        )
        embed.set_footer(icon_url=interaction.user.avatar.url, text=interaction.user.name)
        await interaction.response.send_message("Bug report successfully submitted.", ephemeral=True)
        await dycel.send(embed=embed)

class BugReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.interaction_handled = False
    
    @discord.ui.button(label="Report a bug", style=discord.ButtonStyle.red)
    async def ReportABug(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.interaction_handled:
            await interaction.response.send_message("Alredy reported a bug with this button. Run the command again to report another bug", ephemeral=True)
            return
        self.interaction_handled = True
        modal = BugReportModal()
        await interaction.response.send_modal(modal)

async def setup(bot):
    bot.tree.add_command(BugGroup())