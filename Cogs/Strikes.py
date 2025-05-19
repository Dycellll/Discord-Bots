import discord
from discord import app_commands
from discord.utils import get

class StrikesGroup(app_commands.Group):
    def __init__(self, guild, strike1id, strike2id, strike3id):
        super().__init__(name="strike", description="Strikes-related commands")
        self.strike1id = strike1id
        self.strike2id = strike2id
        self.strike3id = strike3id
        self.Strike1Role = get(guild.roles, id=strike1id)
        self.Strike2Role = get(guild.roles, id=strike2id)
        self.Strike3Role = get(guild.roles, id=strike3id)
    
    @app_commands.command(name="add", description="Add a strike to a member.")
    @app_commands.describe(
        member="The member to add a strike to.",
        reason="The reason for the strike."
    )
    async def strike_add(self, interaction:discord.Interaction, member:discord.Member, reason:str="No reason provided."):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have the MANAGE ROLES permission.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        if member.get_role(self.strike1id) != None:
            await member.remove_roles(self.Strike1Role)
            await member.add_roles(self.Strike2Role)
            await interaction.followup.send(f"Successfully added a strike to {member.mention} for reason: {reason}. They now have 2 strikes.")
        elif member.get_role(self.strike2id) != None:
            await member.remove_roles(self.Strike2Role)
            await member.add_roles(self.Strike3Role)
            await interaction.followup.send(f"Successfully added a strike to {member.mention} for reason: {reason}. They now have 3 strikes.")
        elif member.get_role(self.strike3id) != None:
            await interaction.followup.send(f"{member.mention} already has 3 strikes. Please discuss a punishment with the mod team.")
        else:
            await member.add_roles(self.Strike1Role)
            await interaction.followup.send(f"Successfully added a strike to {member.mention} for reason: {reason}. They now have 1 strike.")
    
    @app_commands.command(name="remove", description="Remove a strike from a member.")
    @app_commands.describe(
        member="The member to remove a strike from."
    )
    async def strike_remove(self, interaction:discord.Interaction, member:discord.Member):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have the MANAGE ROLES permission.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        if member.get_role(self.strike1id) != None:
            await member.remove_roles(self.Strike1Role)
            await interaction.followup.send(f"Successfully removed a strike from {member.mention}. They now have 0 strikes.")
        elif member.get_role(self.strike2id) != None:
            await member.remove_roles(self.Strike2Role)
            await member.add_roles(self.Strike1Role)
            await interaction.followup.send(f"Successfully removed a strike from {member.mention}. They now have 1 strike.")
        elif member.get_role(self.strike3id) != None:
            await member.remove_roles(self.Strike3Role)
            await member.add_roles(self.Strike2Role)
            await interaction.followup.send(f"Successfully removed a strike from {member.mention}. They now have 2 strikes.")
        else:
            await interaction.followup.send(f"{member.mention} doesn't have any strikes.")
    
    @app_commands.command(name="clear", description="Clear all strikes from a member.")
    @app_commands.describe(
        member="The member to clear strikes from."
    )
    async def strike_clear(self, interaction:discord.Interaction, member:discord.Member):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have the MANAGE ROLES permission.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        found:bool = False
        if member.get_role(self.strike1id) != None:
            found = True
            await member.remove_roles(self.Strike1Role)
        if member.get_role(self.strike2id) != None:
            found = True
            await member.remove_roles(self.Strike2Role)
        if member.get_role(self.strike3id) != None:
            found = True
            await member.remove_roles(self.Strike3Role)
        
        if found: 
            await interaction.followup.send(f"Successfully cleared all strikes from {member.mention}.")
        else:
            await interaction.followup.send(f"{member.mention} doesn't have any strikes to clear.")
    
    @app_commands.command(name="check", description="Check the strikes of a member.")
    @app_commands.describe(
        member="The member to check strikes of."
    )
    async def strike_check(self, interaction:discord.Interaction, member:discord.Member):
        await interaction.response.defer(ephemeral=True)
        strikes:int = 0
        if member.get_role(self.strike1id) != None:
            strikes = 1
        if member.get_role(self.strike2id) != None:
            strikes = 2
        if member.get_role(self.strike3id) != None:
            strikes = 3
        await interaction.followup.send(f"{member.mention} has {strikes} strikes.")


async def setup(bot, guild_id, strike1id, strike2id, strike3id):
    guild = bot.get_guild(guild_id)
    bot.tree.add_command(StrikesGroup(guild, strike1id, strike2id, strike3id))