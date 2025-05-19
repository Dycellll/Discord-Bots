import discord, re, os, json
from discord import app_commands
from discord.utils import get

class ReactionRoles(app_commands.Group):
    def __init__(self, databaseName, emojisList):
        super().__init__(name="reactionrole", description="ReactionRoles-related commands")
        self.databaseName = databaseName
        self.emojisList = emojisList
    
    def ReadJson(self):
        file = self.databaseName
        file_path = os.path.join('Databases', file)
        if not os.path.exists(file_path):
            self.WriteJson({}, file)
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            return json.load(jsonfile)

    def WriteJson(self, data, indent=4):
        file = self.databaseName
        file_path = os.path.join('Databases', file)
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=indent)
    
    def GetNumEmoji(self, num: int):
        for emoji in self.emojisList:
            start_index = emoji.find("Number") + len("Number")
            end_index = emoji.find(":", start_index)
            
            emoji_value_str = emoji[start_index:end_index]
            
            emoji_num = int(emoji_value_str)
            
            if num == emoji_num:
                return emoji
        return None

    @app_commands.command(name="make", description="Create a reaction role.")
    @app_commands.describe(
        channel="The channel to send the reactionrole in.",
        title="The title of the embed.",
        hex="The color hex code of the embed (ex: #123456). Defaults to #FFFFFF.",
        roles= "A list of roles (ex: @Member, @Staff (Comma is optional)). Max 15 roles."
    )
    async def rr_make(self, interaction:discord.Interaction, channel:discord.TextChannel, title:str, hex:str, roles:str):
        if interaction.user.guild_permissions.manage_roles:
            await interaction.response.defer(ephemeral=True)
            if not hex.startswith("#"):
                hex = "#" + hex
            if len(hex) != 7 or bool(re.fullmatch(r"#([A-Fa-f0-9]{6})", hex)) is False:
                await interaction.followup.send("Invalid hex code.")
                return
            else:
                role_mentions = roles.split(" ") 
                roles_list = []
                guild = interaction.guild
                for role_mention in role_mentions:
                    if role_mention.replace(" ", "") == "":
                        continue
                    role_mention = role_mention.strip().replace(",", "")
                    role = None 
                    print(f"Processing: {role_mention}")
                    if role_mention.startswith("<@&") and role_mention.endswith(">"):
                        print("Mention role")
                        try:
                            role_id = int(role_mention.replace("<@&", "").replace(">", ""))
                            role = get(guild.roles, id=role_id)
                        except ValueError:
                            print(f"Invalid role mention format: {role_mention}")
                    else:
                        print("Role name")
                        role = get(guild.roles, name=role_mention)
                    if role:
                        print(f"Found role: {role.name}")
                        roles_list.append(role)
                    else:
                        print(f"Role not found: {role_mention}")

                if not roles_list:
                    await interaction.followup.send("Invalid role(s) given.")
                    return
                elif len(roles_list) <= 0:
                    await interaction.followup.send("The roles list mustn't be empty.")
                    return
                elif len(roles_list) > 15:
                    await interaction.followup.send("The roles list mustn't be longer than 15 roles.")
                    return

                i = 1
                description:str = ""
                used_emojis:str = ""
                used_emojis_list = []
                roles_ids_list = []
                for role in roles_list:
                    description += f"{self.GetNumEmoji(i)} - {role.mention}\n"
                    used_emojis += self.GetNumEmoji(i) + "\n"
                    used_emojis_list.append(self.GetNumEmoji(i))
                    roles_ids_list.append(role.id)
                    i += 1
                embed = discord.Embed(
                    title=title,
                    description=description,
                    color=discord.Color.from_str(hex)
                )
                data = self.ReadJson()
                guild_id = str(interaction.guild_id)
                if "guilds" not in data:
                    data["guilds"] = {}
                if guild_id not in data["guilds"]:
                    data["guilds"][guild_id] = {"bot": {"rr_messages": {}}}
                rr_msg = await channel.send(embed=embed)
                rr_msg_data = {
                    "roles_amount" : i - 1,
                    "channel" : rr_msg.channel.id,
                    "used_emojis": used_emojis_list,
                    "roles_list": roles_ids_list
                }
                data["guilds"][guild_id]["bot"]["rr_messages"][str(rr_msg.id)] = rr_msg_data
                self.WriteJson(data)
                for emoji in used_emojis_list:
                    await rr_msg.add_reaction(emoji)
                await interaction.followup.send(f"Successfully created reaction role in {channel.mention}")
        else:
            await interaction.followup.send("You don't have the MANAGE ROLES permission.")
    

    @app_commands.command(name="delete", description="Delete a reaction role.")
    async def rr_delete(self, interaction:discord.Interaction, message_id:str):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have the MANAGE ROLES permission.", ephemeral=True)
            return
        data = self.ReadJson()
        guild_id = str(interaction.guild_id)
        msg_id = int(message_id)
        if message_id in data["guilds"][guild_id]["bot"]["rr_messages"]:
            guild = interaction.guild
            channel:discord.TextChannel = await guild.fetch_channel(int(data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["channel"]))
            message = await channel.fetch_message(msg_id)
            await message.delete()
            del data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]
            self.WriteJson(data)
            await interaction.response.send_message("Successfully deleted reactionrole", ephemeral=True)
        else:
            await interaction.response.send_message("There is no reactionrole with that id.", ephemeral=True)
    

    @app_commands.command(name="edit-visuals", description="Edit a reaction role's visuals.")
    @app_commands.describe(
        message_id="The id of the reactionrole to edit.",
        title="The title of the edited embed.",
        hex="The color hex code of the edited embed (ex: #123456)."
        )
    async def rr_edit_visuals(self, interaction:discord.Interaction, message_id:str, title:str="", hex:str=""):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have the MANAGE ROLES permission.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        data = self.ReadJson()
        rr_msg:discord.Message
        rr_msg_channel:discord.TextChannel
        rr_msg_guild:discord.Guild
        rr_title:str=title
        rr_hex:str=hex
        rr_embed:discord.Embed
        guild_id = str(interaction.guild_id)
        if message_id in data["guilds"][guild_id]["bot"]["rr_messages"]:
            rr_msg_guild = interaction.guild
            rr_msg_channel = get(rr_msg_guild.channels, id=data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["channel"])
            rr_msg = await rr_msg_channel.fetch_message(message_id)
        
        for embed in rr_msg.embeds:
            rr_embed = embed
        if rr_title != "":
            rr_embed.title = rr_title
        if rr_hex != "":
            if not rr_hex.startswith("#"):
                    rr_hex = "#" + rr_hex
            if len(rr_hex) != 7 or bool(re.fullmatch(r"#([A-Fa-f0-9]{6})", rr_hex)) is False:
                await interaction.followup.send("Invalid hex code.")
                return
            rr_embed.color = discord.Color.from_str(rr_hex)
        
        await rr_msg.edit(embed=embed)
        self.WriteJson(data)
        await interaction.followup.send(f"Successfully edited reaction role {rr_msg.id}'s visuals in {rr_msg_channel.mention}")
        
    @app_commands.command(name="add-role", description="Add a role to an existing reactionrole.")
    @app_commands.describe(
        message_id="The id of the reactionrole to edit.",
        role= "The role to add."
    )
    async def rr_add_role(self, interaction:discord.Interaction, message_id:str, role:discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have the MANAGE ROLES permission.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        data = self.ReadJson()
        rr_msg:discord.Message
        rr_msg_channel:discord.TextChannel
        rr_msg_guild:discord.Guild
        rr_embed:discord.Embed
        guild_id = str(interaction.guild_id)
        if message_id in data["guilds"][guild_id]["bot"]["rr_messages"]:
            rr_msg_guild = interaction.guild
            rr_msg_channel = get(rr_msg_guild.channels, id=data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["channel"])
            rr_msg = await rr_msg_channel.fetch_message(message_id)

        if len(data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["roles_list"]) + 1 > 15:
            await interaction.followup.send("That reactionrole has already max roles.")
            return
        
        data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["roles_amount"] += 1
        emoji_to_use:str = self.GetNumEmoji(data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["roles_amount"])
        data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["used_emojis"].append(emoji_to_use)
        data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["roles_list"].append(role.id)
        i = 1
        description:str = ""
        for rolee in data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["roles_list"]:
            roleee = get(rr_msg_guild.roles, id=rolee)
            description += f"{self.GetNumEmoji(i)} - {roleee.mention}\n"
            i += 1
        
        new_embed:discord.Embed
        for embed in rr_msg.embeds:
            new_embed = embed
        new_embed.description = description
        self.WriteJson(data)
        await rr_msg.edit(embed=new_embed)
        await rr_msg.add_reaction(emoji_to_use)
        await interaction.followup.send(f"Successfully added role {role.mention} to reaction role {rr_msg.id} in {rr_msg_channel.mention}")

    @app_commands.command(name="edit-roles", description="Edit the roles of an existing reactionrole. Use add-role for single edits instead.")
    @app_commands.describe(
        message_id="The id of the reactionrole to edit.",
        roles="A list of roles (ex: @Member, @Staff (Comma is optional)). Max 15 roles."
    )
    async def rr_edit_roles(self, interaction: discord.Interaction, message_id: str, roles: str):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have the MANAGE ROLES permission.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        data = self.ReadJson()
        rr_msg: discord.Message
        rr_msg_channel: discord.TextChannel
        rr_msg_guild: discord.Guild
        guild_id = str(interaction.guild_id)
        if message_id in data["guilds"][guild_id]["bot"]["rr_messages"]:
            rr_msg_guild = interaction.guild
            rr_msg_channel = get(rr_msg_guild.channels, id=data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["channel"])
            rr_msg = await rr_msg_channel.fetch_message(message_id)

            await rr_msg.clear_reactions()

            role_mentions = roles.split(" ")
            roles_list = []
            for role_mention in role_mentions:
                if role_mention.replace(" ", "") == "":
                    continue
                role_mention = role_mention.strip().replace(",", "")
                role = None
                if role_mention.startswith("<@&") and role_mention.endswith(">"):
                    try:
                        role_id = int(role_mention.replace("<@&", "").replace(">", ""))
                        role = get(rr_msg_guild.roles, id=role_id)
                    except ValueError:
                        print(f"Invalid role mention format: {role_mention}")
                else:
                    role = get(rr_msg_guild.roles, name=role_mention)
                if role:
                    roles_list.append(role)
                else:
                    print(f"Role not found: {role_mention}")

            if not roles_list:
                await interaction.followup.send("Invalid role(s) given.")
                return
            elif len(roles_list) <= 0:
                await interaction.followup.send("The roles list mustn't be empty.")
                return
            elif len(roles_list) > 15:
                await interaction.followup.send("The roles list mustn't be longer than 10 roles.")
                return

            data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["roles_list"] = [role.id for role in roles_list]
            data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["roles_amount"] = len(roles_list)
            data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["used_emojis"] = []

            i = 1
            description = ""
            for role in roles_list:
                emoji_to_use = self.GetNumEmoji(i)
                data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["used_emojis"].append(emoji_to_use)
                description += f"{emoji_to_use} - {role.mention}\n"
                i += 1

            new_embed = rr_msg.embeds[0]
            new_embed.description = description
            self.WriteJson(data)
            await rr_msg.edit(embed=new_embed)
            for emoji in data["guilds"][guild_id]["bot"]["rr_messages"][str(message_id)]["used_emojis"]:
                await rr_msg.add_reaction(emoji)
            await interaction.followup.send(f"Successfully edited roles for reaction role {rr_msg.id} in {rr_msg_channel.mention}")
        else:
            await interaction.followup.send("There is no reactionrole with that id.", ephemeral=True)

async def on_rr_add(bot, data, payload):
    if payload.user_id == bot.user.id:
        return
    
    message_id = str(payload.message_id)
    emoji = payload.emoji
    channel = bot.get_channel(payload.channel_id)
    message:discord.Message
    guild = channel.guild
    member:discord.Member = guild.get_member(payload.user_id)

    try:
        message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        print(f"Message with ID {message_id} not found.")
        return

    if message_id in data["guilds"][str(member.guild.id)]["bot"]["rr_messages"]:
        if f"<:{emoji.name}:{emoji.id}>" in data["guilds"][str(member.guild.id)]["bot"]["rr_messages"][str(message_id)]["used_emojis"]:
            role_index = data["guilds"][str(member.guild.id)]["bot"]["rr_messages"][str(message_id)]["used_emojis"].index(f"<:{emoji.name}:{emoji.id}>")
            roles_list = [guild.get_role(role_id) for role_id in data["guilds"][str(member.guild.id)]["bot"]["rr_messages"][str(message_id)]["roles_list"]]
            if role_index < len(roles_list):
                role = roles_list[role_index]
                try:
                    await member.add_roles(role)
                except:
                    hold = 1

async def on_rr_remove(bot, data, payload):
    if payload.user_id == bot.user.id:
        return
    
    message_id = str(payload.message_id)
    emoji = payload.emoji
    channel = bot.get_channel(payload.channel_id)
    message:discord.Message
    guild = channel.guild
    member:discord.Member = guild.get_member(payload.user_id)

    try:
        message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        print(f"Message with ID {message_id} not found.")
        return

    if message_id in data["guilds"][str(member.guild.id)]["bot"]["rr_messages"]:
        if f"<:{emoji.name}:{emoji.id}>" in data["guilds"][str(member.guild.id)]["bot"]["rr_messages"][str(message_id)]["used_emojis"]:
            role_index = data["guilds"][str(member.guild.id)]["bot"]["rr_messages"][str(message_id)]["used_emojis"].index(f"<:{emoji.name}:{emoji.id}>")
            roles_list = [guild.get_role(role_id) for role_id in data["guilds"][str(member.guild.id)]["bot"]["rr_messages"][str(message_id)]["roles_list"]]
            if role_index < len(roles_list):
                role = roles_list[role_index]
                try:
                    await member.remove_roles(role)
                except:
                    hold = 1

async def setup(bot, databaseName, emojisList, aliases):
    reaction_roles_group = ReactionRoles(databaseName, emojisList)
    bot.tree.add_command(reaction_roles_group)
    for alias in aliases:
        rr_alias = app_commands.Group(name=alias, description="Alias for the ReactionRoles group.")
        rr_alias.add_command(reaction_roles_group.rr_make)
        rr_alias.add_command(reaction_roles_group.rr_delete)
        rr_alias.add_command(reaction_roles_group.rr_edit_visuals)
        rr_alias.add_command(reaction_roles_group.rr_add_role)
        rr_alias.add_command(reaction_roles_group.rr_edit_roles)
        bot.tree.add_command(rr_alias)