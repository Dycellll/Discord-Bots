import discord
import os
import json
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="A.", intents=intents, help_command=None)

guild_id = 1362623568739045627
tl_channel_id = 1368686922859548835

def ReadJson(file='amethystdatabase.json'):
    file_path = os.path.join('Databases', file)
    if not os.path.exists(file_path):
        WriteJson({
            "tierlist": {
                "tiers": {
                    "S+": [],
                    "S": [],
                    "A": [],
                    "B": [],
                    "C": [],
                    "D": [],
                    "F": []
                },
                "msg_id": None
            }
        }, file)
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)

def WriteJson(data, file='amethystdatabase.json', indent=4):
    file_path = os.path.join('Databases', file)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=indent)

async def autocomplete_type(interaction: discord.Interaction, types, current: str) -> list[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=choice_type, value=choice_type)
        for choice_type in types
        if current.lower() in choice_type.lower()
    ]

async def set_status():
    await bot.change_presence(
        activity=discord.Game(name="A.help | Amethyst Bot"),
        status=discord.Status.dnd
    )

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} - {bot.user.id}")
    bot.tree.add_command(TierGroup())
    await set_status()
    await bot.tree.sync()

async def make_tierlist():
    data = ReadJson()
    guild = bot.get_guild(guild_id)
    tierlist = "# Amethyst Tierlist\n"
    
    for tier_name in ["S+", "S", "A", "B", "C", "D", "F"]:
        tier_members = data["tierlist"]["tiers"].get(tier_name, [])
        if not tier_members:
            continue
            
        tierlist += f"## {tier_name} Tier\n"
        for member_id in tier_members:
            member = guild.get_member(int(member_id))
            if member:
                tierlist += f"- {member.mention}\n"
    
    unranked = []
    all_ranked = []
    for tier_members in data["tierlist"]["tiers"].values():
        all_ranked.extend(tier_members)
        
    for member in guild.members:
        if member.bot:
            continue
        if str(member.id) not in all_ranked:
            unranked.append(member)
    
    if unranked:
        tierlist += "## Unranked\n"
        for member in unranked:
            tierlist += f"- {member.mention}\n"
    
    return tierlist

async def update_tierlist():
    data = ReadJson()
    guild = bot.get_guild(guild_id)
    channel = guild.get_channel(tl_channel_id)
    
    if not any(len(members) > 0 for members in data["tierlist"]["tiers"].values()):
        print("No ranked members found.")
        return
    
    tierlist_content = await make_tierlist()
    
    if not data["tierlist"].get("msg_id"):
        msg = await channel.send(tierlist_content)
        data["tierlist"]["msg_id"] = msg.id
        WriteJson(data)
        return
    
    try:
        msg = await channel.fetch_message(data["tierlist"]["msg_id"])
        await msg.edit(content=tierlist_content)
    except discord.NotFound:
        msg = await channel.send(tierlist_content)
        data["tierlist"]["msg_id"] = msg.id
        WriteJson(data)

class TierGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="tier")
    
    @app_commands.command(name="add", description="Add a new member to the tierlist")
    @app_commands.describe(
        member="The member to rank.",
        rank="The tier to set.",
        position="Position in the tier (default: end)",
        below="Member to place this member below (overrides position)"
    )
    async def rank_member(self, interaction: discord.Interaction, 
                        member: discord.Member, 
                        rank: str,
                        position: int = None,
                        below: discord.Member = None):
        await interaction.response.defer(thinking=True, ephemeral=True)
        guild = interaction.guild
        if guild.id != guild_id:
            return await interaction.followup.send("This command can only be used in the Amethyst server.", ephemeral=True)
        if member.bot:
            return await interaction.followup.send("You cannot rank a bot.", ephemeral=True)
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
        
        data = ReadJson()
        for tier in data["tierlist"]["tiers"].values():
            if str(member.id) in tier:
                return await interaction.followup.send(
                    "This member is already ranked. Use /tier move to modify this member's position.",
                    ephemeral=True
                )
        
        if rank not in data["tierlist"]["tiers"]:
            return await interaction.followup.send("Invalid rank. Valid ranks are S+, S, A, B, C, D, F.", ephemeral=True)
        
        if below:
            if str(below.id) not in data["tierlist"]["tiers"][rank]:
                return await interaction.followup.send(
                    f"{below.mention} is not in the {rank} tier.",
                    ephemeral=True
                )
            position = data["tierlist"]["tiers"][rank].index(str(below.id)) + 1
        
        if position is None:
            data["tierlist"]["tiers"][rank].append(str(member.id))
        else:
            position = max(0, min(position, len(data["tierlist"]["tiers"][rank])))
            data["tierlist"]["tiers"][rank].insert(position, str(member.id))
        
        WriteJson(data)
        await update_tierlist()
        await interaction.followup.send(
            f"Ranked {member.mention} as {rank} at position {position if position is not None else 'end'}.",
            ephemeral=True
        )

    @rank_member.autocomplete("rank")
    async def rank_autocomplete(self, interaction: discord.Interaction, current: str):
        types = ["S+", "S", "A", "B", "C", "D", "F"]
        return await autocomplete_type(interaction, types, current)
    
    @app_commands.command(name="move", description="Move a member to a different tier/position.")
    @app_commands.describe(
        member="The member to move.",
        rank="The tier to set.",
        position="Position in the tier (default: end)",
        below="Member to place this member below (overrides position)"
    )
    async def move_member(self, interaction: discord.Interaction,
                        member: discord.Member,
                        rank: str,
                        position: int = None,
                        below: discord.Member = None):
        await interaction.response.defer(thinking=True, ephemeral=True)
        guild = interaction.guild
        if guild.id != guild_id:
            return await interaction.followup.send("This command can only be used in the Amethyst server.", ephemeral=True)
        if member.bot:
            return await interaction.followup.send("You cannot rank a bot.", ephemeral=True)
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
        
        data = ReadJson()
        current_tier = None
        for tier_name, tier_members in data["tierlist"]["tiers"].items():
            if str(member.id) in tier_members:
                current_tier = tier_name
                tier_members.remove(str(member.id))
                break
        
        if current_tier is None:
            return await interaction.followup.send(
                "This member is not ranked. Use /tier add to rank this member.",
                ephemeral=True
            )
        
        if rank not in data["tierlist"]["tiers"]:
            return await interaction.followup.send("Invalid rank. Valid ranks are S+, S, A, B, C, D, F.", ephemeral=True)
        
        if below:
            if str(below.id) not in data["tierlist"]["tiers"][rank]:
                return await interaction.followup.send(
                    f"{below.mention} is not in the {rank} tier.",
                    ephemeral=True
                )
            position = data["tierlist"]["tiers"][rank].index(str(below.id)) + 1
        
        if position is None:
            data["tierlist"]["tiers"][rank].append(str(member.id))
        else:
            position = max(0, min(position, len(data["tierlist"]["tiers"][rank])))
            data["tierlist"]["tiers"][rank].insert(position, str(member.id))
        
        WriteJson(data)
        await update_tierlist()
        await interaction.followup.send(
            f"Moved {member.mention} to {rank} tier at position {position if position is not None else 'end'}.",
            ephemeral=True
        )
    
    @move_member.autocomplete("rank")
    async def move_autocomplete(self, interaction: discord.Interaction, current: str):
        types = ["S+", "S", "A", "B", "C", "D", "F"]
        return await autocomplete_type(interaction, types, current)

    @app_commands.command(name="remove", description="Remove a member from the tierlist.")
    @app_commands.describe(
        member="The member to remove.",
    )
    async def remove_member(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(thinking=True, ephemeral=True)
        guild = interaction.guild
        if guild.id != guild_id:
            return await interaction.followup.send("This command can only be used in the Amethyst server.", ephemeral=True)
        if member.bot:
            return await interaction.followup.send("You cannot rank a bot.", ephemeral=True)
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
        
        data = ReadJson()
        removed = False
        for tier in data["tierlist"]["tiers"].values():
            if str(member.id) in tier:
                tier.remove(str(member.id))
                removed = True
                break
        
        if not removed:
            return await interaction.followup.send("This member is not ranked.", ephemeral=True)
        
        WriteJson(data)
        await update_tierlist()
        await interaction.followup.send(f"Removed {member.mention} from the tierlist.", ephemeral=True)
    
    @app_commands.command(name="swap", description="Swap two members' positions in the same tier")
    @app_commands.describe(
        member1="First member to swap",
        member2="Second member to swap"
    )
    async def swap_members(self, interaction: discord.Interaction,
                         member1: discord.Member,
                         member2: discord.Member):
        await interaction.response.defer(thinking=True, ephemeral=True)
        guild = interaction.guild
        if guild.id != guild_id:
            return await interaction.followup.send("This command can only be used in the Amethyst server.", ephemeral=True)
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
        
        data = ReadJson()
        tier_name = None
        pos1, pos2 = -1, -1
        
        for tier, members in data["tierlist"]["tiers"].items():
            if str(member1.id) in members and str(member2.id) in members:
                tier_name = tier
                pos1 = members.index(str(member1.id))
                pos2 = members.index(str(member2.id))
                break
        
        if tier_name is None:
            return await interaction.followup.send(
                "Both members must be in the same tier to swap.",
                ephemeral=True
            )
        
        data["tierlist"]["tiers"][tier_name][pos1], data["tierlist"]["tiers"][tier_name][pos2] = \
            data["tierlist"]["tiers"][tier_name][pos2], data["tierlist"]["tiers"][tier_name][pos1]
        
        WriteJson(data)
        await update_tierlist()
        await interaction.followup.send(
            f"Swapped positions of {member1.mention} and {member2.mention} in {tier_name} tier.",
            ephemeral=True
        )
    
    @app_commands.command(name="update", description="Update the tierlist.")
    async def update(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        guild = interaction.guild
        if guild.id != guild_id:
            return await interaction.followup.send("This command can only be used in the Amethyst server.", ephemeral=True)
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
        
        await update_tierlist()
        await interaction.followup.send("Updated the tierlist.", ephemeral=True)
