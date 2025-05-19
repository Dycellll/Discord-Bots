import discord, secret, aiohttp, io, json, asyncio, os, random, heapq, requests, traceback, Cogs.ReactionRoles
from discord import FFmpegPCMAudio, app_commands
from discord.ext import commands, tasks
from discord.utils import get
from glob import glob
from groq import Groq
from Cogs.AI_Commands import setup as setup_ai_commands
from Cogs.ReactionRoles import setup as setup_reaction_roles
from Cogs.BugReport import setup as setup_bug_report
from Cogs.SuggestionGive import setup as setup_suggestion
from Cogs.Music_Commands import setup as setup_music_commands

Token = secret.ASSISTANTTOKEN
client = Groq(
    api_key=secret.GROQ_API_KEY,
)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="D.", intents=intents, help_command=None)

dycel_id = 1099017318232764447
main_server_id = 1315332542987108454

json_lock_txt = asyncio.Lock()
json_lock_vc = asyncio.Lock()

helpEmbed = discord.Embed(
    title="Help",
    description="A list of all available commands.",
    color=discord.Color.purple()
)

helpEmbed.add_field(
    name="🤖 Bot Commands",
    value=(
        "**/bot info** - Bot info.\n"
        "**/bug report** - Report a bug.\n"
        "**/suggestion give** - Suggest a feature."
    ),
    inline=False
)

helpEmbed.add_field(
    name="🎵 Music Commands",
    value=(
        "**/vc join** - Join your VC.\n"
        "**/vc leave** - Leave the VC.\n"
        "**/music play** - Play a song.\n"
        "**/music stop** - Stop the music."
    ),
    inline=False
)

helpEmbed.add_field(
    name="🔊 Soundboard Commands",
    value=(
        "**/soundboard play** - Play a soundboard.\n"
        "**/soundboard stop** - Stop the soundboard.\n"
        "**/soundboard save** - Save a soundboard.\n"
        "**/soundboard delete** - Delete a soundboard.\n"
        "**/soundboard list** - List your soundboards."
    ),
    inline=False
)

helpEmbed.add_field(
    name="🏆 Stats and Leaderboards",
    value=(
        "**/stats** - View member stats.\n"
        "**/leaderboard** - View the server leaderboard."
    ),
    inline=False
)

helpEmbed.add_field(
    name="🎮 Fun Commands",
    value=(
        "**/fun dice-roll** - Play Dice Roll.\n"
        "**/fun coin-flip** - Flip a coin.\n"
        "**/fun guess-the-number** - Guess the number.\n"
        "**/fun rock-paper-scissors** - Play RPS.\n"
        "**/fun 8ball** - Ask the 8-ball.\n"
        "**/fun dap / hug / kiss / welcome** - Interact with members."
    ),
    inline=False
)

helpEmbed.add_field(
    name="💥 Moderation Commands",
    value=(
        "**/moderation report** - Report a rule breaker.\n"
        "**/role give/remove** - Manage roles.\n"
        "**/reactionrole (or /rr)** - Create/edit reaction roles.\n"
        "**/autorole add/remove** - Manage autoroles."
    ),
    inline=False
)

emoji_num1 = "<:Number1:1316867910542557256>"
emoji_num2 = "<:Number2:1316867961587372143>"
emoji_num3 = "<:Number3:1316867995682865305>"
emoji_num4 = "<:Number4:1316868020119015455>"
emoji_num5 = "<:Number5:1316868042436640941>"
emoji_num6 = "<:Number6:1316868070756581437>"
emoji_num7 = "<:Number7:1316868090675466324>"
emoji_num8 = "<:Number8:1316868114729930813>"
emoji_num9 = "<:Number9:1316868142902935645>"
emoji_num10 = "<:Number10:1316868186699857960>"
emoji_num11 = "<:Number11:1352743296174260417>"
emoji_num12 = "<:Number12:1352743303866744843>"
emoji_num13 = "<:Number13:1352743310644482088>"
emoji_num14 = "<:Number14:1352743317443710996>"
emoji_num15 = "<:Number15:1352743324284616776>"
emoji_start_bar_full = "<:StartBarFull:1317872617759440968>"
emoji_start_bar_empty = "<:StartBarEmpty:1317872871443402874>"
emoji_mid_bar_full = "<:MidBarFull:1317872910698020914>"
emoji_mid_bar_empty = "<:MidBarEmpty:1317872952204726322>"
emoji_end_bar_full = "<:EndBarFull:1317873000695205959>"
emoji_end_bar_empty = "<:EndBarEmpty:1317873044005584907>"

def GetBarEmoji(filled:bool, spot:int):
    if filled:
        if spot == 1:
            return emoji_start_bar_full
        elif spot == 2:
            return emoji_mid_bar_full
        elif spot == 3:
            return emoji_end_bar_full
    else:
        if spot == 1:
            return emoji_start_bar_empty
        elif spot == 2:
            return emoji_mid_bar_empty
        elif spot == 3:
            return emoji_end_bar_empty
        

async def SetPresence():
    await discord.Client.change_presence(
        status=discord.Status.idle,    activity=discord.Activity(
    type=discord.ActivityType.playing, name="Bot stuff"
            ), self=bot
        )

def ReadJson(file='database.json'):
    file_path = os.path.join('Databases', file)
    if not os.path.exists(file_path):
        WriteJson({}, file)
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)

def WriteJson(data, file='database.json', indent=4):
    file_path = os.path.join('Databases', file)
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=indent)

async def AsyncReadJson(file='database.json'):
    file_path = os.path.join('Databases', file)
    if not os.path.exists(file_path):
        return {}

    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        try:
            content = jsonfile.read()
            data = json.loads(content)
            return data
        except json.JSONDecodeError as e:
            return {}

async def AsyncWriteJson(data, file='database.json', indent=4):
    file_path = os.path.join('Databases', file)
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=indent)

async def SyncJsonData():
    data = ReadJson()
    if "guilds" not in data:
        data["guilds"] = {}

    for guild in bot.guilds:
        guild_id_str = str(guild.id)

        if guild_id_str not in data["guilds"]:
            data["guilds"][guild_id_str] = {}

        guild_data = data["guilds"][guild_id_str]
        guild_data.setdefault("users", {})
        guild_data.setdefault("tasks", {})
        guild_data.setdefault("bot", {})
        guild_data["bot"].setdefault("rr_messages", {})
        guild_data["bot"].setdefault("autoroles", {})
        guild_data["bot"].setdefault("blacklisted_ids", {})
        guild_data["bot"].setdefault("logs_channel", 1)

        for member in guild.members:
            if not member.bot:
                member_id_str = str(member.id)

                if member_id_str in data["guilds"].get(str(main_server_id), {}).get("users", {}):
                    for member_guild in member.mutual_guilds:
                        member_guild_id_str = str(member_guild.id)
                        if (
                            member_guild_id_str != str(main_server_id)
                            and member_id_str in data["guilds"][str(main_server_id)]["users"]
                        ):
                            if member_guild_id_str not in data["guilds"]:
                                data["guilds"][member_guild_id_str] = {}
                            if "users" not in data["guilds"][member_guild_id_str]:
                                data["guilds"][member_guild_id_str]["users"] = {}
                            data["guilds"][member_guild_id_str]["users"].setdefault(member_id_str, {})
                            data["guilds"][member_guild_id_str]["users"][member_id_str]["soundboards"] = data["guilds"][str(main_server_id)]["users"][member_id_str]["soundboards"]

                user_data = guild_data["users"].setdefault(member_id_str, {})
                user_data.setdefault("id", member.id)
                user_data.setdefault("avatar_url", member.avatar.url if member.avatar else None)
                user_data.setdefault("boost_streak", 0)
                user_data.setdefault("xp_text", 0)
                user_data.setdefault("xp_vc", 0)
                user_data.setdefault("lvl_text", 1)
                user_data.setdefault("lvl_vc", 1)
                user_data.setdefault("soundboards", {})

    data["code_lines"] = len(open('BotAssistant.py', 'r', encoding='utf-8').readlines())
    WriteJson(data)

emojisList = [emoji_num1, emoji_num2, emoji_num3, emoji_num4, emoji_num5, emoji_num6, emoji_num7, emoji_num8, emoji_num9, emoji_num10, emoji_num11, emoji_num12, emoji_num13, emoji_num14, emoji_num15]

async def add_cogs():
    await setup_ai_commands(bot, client)
    await setup_reaction_roles(bot, "database.json", emojisList, ["rr"])
    await setup_bug_report(bot)
    await setup_suggestion(bot)
    await setup_music_commands(bot)

@bot.event
async def on_ready():
    try:
        bot.tree.add_command(VcGroup())
        bot.tree.add_command(SoundboardGroup())
        bot.tree.add_command(ModerationGroup())
        bot.tree.add_command(RoleGroup())
        bot.tree.add_command(FunGroup())
        bot.tree.add_command(AutoroleGroup())
        bot.tree.add_command(BotGroup())

        await add_cogs()
        
        await SetPresence()
        await bot.tree.sync()
        await SyncJsonData()
        check_avatars.start()

        print(f'Logged in as {bot.user.name} - {bot.user.id}')

    except Exception as e:
        print(f"An error occurred in on_ready: {e}")
        traceback.print_exc()

@bot.event
async def on_member_join(member:discord.Member):
    print("Member joined")
    data = ReadJson()
    if member.bot:
        print("Bot joined")
        if member.guild.id == main_server_id:
            role1 = get(member.guild.roles, id=1315332542987108460)
            role2 = get(member.guild.roles, id=1315332542987108456)
            await member.add_roles(role1)
            print("Added role 1")
            await member.add_roles(role2)
            print("Added role 2")
    else:
        member_BLed:bool = False
        autorole_ids = data["guilds"][str(member.guild.id)]["bot"]["autoroles"]
        for role_id in autorole_ids:
            role = get(member.guild.roles, id=int(role_id))
            if role is None:
                print(f"Role with ID {role_id} not found in guild {member.guild.name}.")
                continue
            try:
                await member.add_roles(role)
                print(f"Assigned role {role.name} to {member.name}")
            except discord.Forbidden:
                print(f"Insufficient permissions to assign role {role.name}.")
            except discord.HTTPException as e:
                print(f"HTTP error when assigning role {role.name}: {e}")

        if str(member.id) in data["guilds"][str(member.guild.id)]["bot"]["blacklisted_ids"]:
            if member.guild.id == main_server_id:
                blacklisted_channel:discord.TextChannel = get(member.guild.channels, id=1318310000791126076)
                dycel_user = get(member.guild.members, id=dycel_id)
                bl_role:discord.Role = get(member.guild.roles, id=1318314673912938609)
                await member.add_roles(bl_role)
                data["guilds"][str(member.guild.id)]["bot"]["blacklisted_ids"][str(member.id)] = member.id
                try:
                    user = await bot.fetch_user(696312787827294218)
                    await member.guild.ban(user, reason="Silver's alt")
                except:
                    pass
                WriteJson(data)
                member_BLed = True
        
        data["guilds"][str(member.guild.id)]["users"][str(member.id)] = {"id" : member.id, "avatar_url" : member.avatar.url, "boost_streak": 0, "xp_text" : 0, "xp_vc" : 0, "lvl_text" : 1, "lvl_vc" : 1, "soundboards" : {}}
        if str(member.id) in data["guilds"].get(str(main_server_id), {}).get("users", {}):
            for member_guild in member.mutual_guilds:
                member_guild_id_str = str(member_guild.id)
                if (
                    member_guild_id_str != str(main_server_id)
                    and str(member.id) in data["guilds"][str(main_server_id)]["users"]
                ):
                    data["guilds"][member_guild_id_str]["users"][str(member.id)]["soundboards"] = data["guilds"][str(main_server_id)]["users"][str(member.id)]["soundboards"]
        WriteJson(data)
        welcome_channel = member.guild.get_channel(1315332542987108462)
        embed = discord.Embed(
            title="Welcome!",
            description=f"Welcome, {member.mention}! We're glad to have you here 🎉",
            color=discord.Color.dark_purple()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Member #{len(member.guild.members)}")
        if member_BLed:
            blacklisted_channel:discord.TextChannel = get(member.guild.channels, id=1318310000791126076)
            await blacklisted_channel.send(f"{member.mention}, you have been blacklisted from the server! I wonder what you did to deserve this. Well, try to ask {dycel_user.mention} to be whitelisted, maybe he'll listen to you.")
            embed.description = f"Welcome, {member.mention}! We're... not really glad to have you here, since you're blacklisted from the server."
            embed.color = discord.Color.dark_red()
        await welcome_channel.send(embed=embed)
    WriteJson(data)


@bot.event
async def on_member_update(before, after):
    data = ReadJson()
    if str(after.id) not in data["guilds"][str(after.guild.id)]["users"]:
        return
    if not after.bot and after.premium_since is None:
        data["guilds"][str(after.guild.id)]["users"][str(after.id)]["boost_streak"] = 0
    if not after.bot and before.premium_since != after.premium_since and after.premium_since is not None:
        data["guilds"][str(after.guild.id)]["users"][str(after.id)]["boost_streak"] += 1
        channel = get(after.guild.text_channels, id=1315332542987108462)
        if channel is not None:
            embed = discord.Embed(
                title="🎉 Thank You for Boosting! 🎉",
                description=f"{after.mention} just boosted the server! Thank you for your support! 💜",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=after.avatar.url) 
            streak = data["guilds"][str(after.guild.id)]["users"][str(after.id)]["boost_streak"]
            embed.set_footer(text=f"🔥🔥🔥 Streak: x{streak} 🔥🔥🔥")
            await channel.send(embed=embed)
    WriteJson(data)


async def detectG(message:discord.Message):
    if "😏" in message.content or "😘" in message.content:
        await message.add_reaction("🏳️‍🌈")


@bot.event
async def on_error(event, *args, **kwargs):
    print(f"An error occurred in event {event}: {args}, {kwargs}")


@bot.event
async def on_message(message: discord.Message):
    await detectG(message)
    await SyncJsonData()

    if not message.author.bot:
        try:
            async with json_lock_txt:
                data = await AsyncReadJson()
                def get_latest_message_file():
                    files = glob(os.path.join("Databases", "messages*.json"))
                    
                    if not files:
                        print("[DEBUG] No messages files found. Initializing messages1.json.")
                        WriteJson({}, "messages1.json")
                        return os.path.join("Databases", "messages1.json")
                    
                    files.sort(key=lambda x: int(os.path.basename(x).replace("messages", "").replace(".json", "")))
                    return files[-1]
                
                latest_file = get_latest_message_file()
                if not latest_file:
                    raise ValueError("Failed to determine the latest messages file.")
                
                def file_line_count(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            return sum(1 for _ in f)
                    except FileNotFoundError:
                        return 0

                if file_line_count(latest_file) >= 100_000:
                    latest_number = int(latest_file.replace("messages", "").replace(".json", ""))
                    latest_file = f"messages{latest_number + 1}.json"
                    WriteJson({}, latest_file)
                    print(f"[DEBUG] Created new file: {latest_file}")
                
                try:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        msg_data = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    print(f"[DEBUG] Initializing {latest_file} due to missing or corrupted data.")
                    msg_data = {}
                    WriteJson(msg_data, latest_file)
                
                msg_data[str(message.id)] = {
                    "content": message.content,
                    "author": message.author.id,
                    "attachments": [
                        {"filename": attachment.filename, "url": attachment.url}
                        for attachment in message.attachments
                    ]
                }
                
                user_id = str(message.author.id)
                guild_id = str(message.guild.id)
                user_data = data["guilds"][guild_id]["users"][user_id]

                xp_gain = random.randint(9, 11)
                user_data["xp_text"] += xp_gain
                
                current_level = user_data["lvl_text"]
                next_level = current_level + 1
                if current_level == 1:
                    required_xp = 357
                else:
                    required_xp = 197 * (current_level - 1) + 197 * current_level
                
                if user_data["xp_text"] >= required_xp:
                    user_data["lvl_text"] = next_level
                    
                await AsyncWriteJson(data)
                
                try:
                    with open(latest_file, 'w', encoding='utf-8') as f:
                        json.dump(msg_data, f, indent=4)
                except Exception as e:
                    print(f"[DEBUG] Failed to write to {latest_file}: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()

    await bot.process_commands(message)


@tasks.loop(minutes=1)
async def check_avatars():
    data = ReadJson()
    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                if data["guilds"][str(guild.id)]["users"][str(member.id)]["avatar_url"] != member.avatar.url:
                    data["guilds"][str(guild.id)]["users"][str(member.id)]["avatar_url"] = member.avatar.url
    await SyncJsonData()
    WriteJson(data)


@bot.event
async def on_guild_join(guild:discord.Guild):
    await SyncJsonData()
    embed = discord.Embed(
        title="Hey",
        description="Yooo thx for adding me to your server!!\nSet the logs channel with /logs-channel-set to get:\ncool message logs for deleted messages\nAND\ncool message logs for edited messages (better than any other bot fr)",
        color=discord.Color.purple()
    )
    await guild.owner.send(embed=embed)


def find_message_file(msg_id: str):
    files = glob("messages*.json")
    files.sort(key=lambda x: int(x.replace("messages", "").replace(".json", "")))

    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if msg_id in data:
                    return file, data
        except (FileNotFoundError, json.JSONDecodeError):
            continue

    return None, None


@bot.event
async def on_raw_message_edit(payload):
    data = ReadJson()
    channel = bot.get_channel(payload.channel_id)
    guild = channel.guild

    if data["guilds"][str(guild.id)]["bot"]["logs_channel"] != 1:
        logs_channel = get(guild.channels, id=data["guilds"][str(guild.id)]["bot"]["logs_channel"])

    msg_id = str(payload.message_id)
    before_content: str = None

    try:
        after: discord.Message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        return

    if after.author.bot:
        return

    file_name, msg_data = find_message_file(msg_id)
    if not msg_data:
        return

    before_content = msg_data[msg_id]["content"]

    if before_content == after.content:
        return

    embed = discord.Embed(
        title="Edited message",
        description=f"{after.author.display_name} ({after.author.name}) just edited this message.\n"
                    f"**Before:** {before_content}\n**After:** {after.content}",
        color=discord.Color.blue()
    )

    files_array = []
    if after.attachments:
        for attachment in after.attachments:
            embed.add_field(name="Attachment", value=attachment.url, inline=False)

            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as response:
                    if response.status != 200:
                        continue

                    data = await response.read()
                    file = discord.File(fp=io.BytesIO(data), filename=attachment.filename)
                    files_array.append(file)

    msg_data[msg_id]["content"] = after.content
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(msg_data, f, indent=4)

    if data["guilds"][str(guild.id)]["bot"]["logs_channel"] != 1:
        await logs_channel.send(content=f"{before_content} --> {after.content}\n\nMessage ID: {after.id}", embed=embed, files=files_array)


@bot.event
async def on_raw_message_delete(payload):
    data = ReadJson()
    msg_id = str(payload.message_id)
    channel = bot.get_channel(payload.channel_id)
    guild = channel.guild

    if data["guilds"][str(guild.id)]["bot"]["logs_channel"] != 1:
        logs_channel = get(guild.channels, id=data["guilds"][str(guild.id)]["bot"]["logs_channel"])

    file_name, msg_data = find_message_file(msg_id)
    if not msg_data:
        return

    msg_content = msg_data[msg_id]["content"]
    msg_author = get(guild.members, id=int(msg_data[msg_id]["author"]))
    msg_attachments = msg_data[msg_id]["attachments"]

    if msg_author.bot:
        return

    embed = discord.Embed(
        title="Deleted message",
        description=f"{msg_author.display_name} ({msg_author.name}) deleted a message in {channel.mention}:\n{msg_content}",
        color=discord.Color.red()
    )

    files_array = []
    if msg_attachments:
        for attachment in msg_data[msg_id]["files"]:
            embed.add_field(name="Attachment", value=attachment["url"], inline=False)

            async with aiohttp.ClientSession() as session:
                async with session.get(attachment["url"]) as response:
                    if response.status != 200:
                        continue

                    data = await response.read()
                    file = discord.File(fp=io.BytesIO(data), filename=attachment["filename"])
                    files_array.append(file)

    if data["guilds"][str(guild.id)]["bot"]["logs_channel"] != 1:
        await logs_channel.send(content=f"{msg_content}\n\nMessage ID: {msg_id}", embed=embed, files=files_array)

    del msg_data[msg_id]
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(msg_data, f, indent=4)


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    data = ReadJson()
    
    guild_id = str(member.guild.id)
    tasks = data["guilds"][guild_id]["tasks"]

    for dataset in list(tasks.keys()):
        temp_member = member.guild.get_member(int(dataset))
        if temp_member is None or temp_member.voice is None:
            del tasks[dataset]
            await AsyncWriteJson(data)

    if not member.bot and after.channel and not before.channel:
        if str(member.id) not in tasks:
            tasks[str(member.id)] = True
            await AsyncWriteJson(data)
            asyncio.create_task(increment_xp(member))

    if not member.bot and not after.channel and before.channel:
        if str(member.id) in tasks:
            del tasks[str(member.id)]
            await AsyncWriteJson(data)


async def increment_xp_foruser(member: discord.Member):
    data = ReadJson()
    async with json_lock_vc:
        guild_id_str = str(member.guild.id)
        member_id_str = str(member.id)
        data["guilds"][guild_id_str]["users"][member_id_str]["xp_vc"] += random.randint(3, 4)

        next_level = data["guilds"][guild_id_str]["users"][member_id_str]["lvl_vc"] + 1
        if data["guilds"][guild_id_str]["users"][member_id_str]["lvl_vc"] - 1 > 0:
            required_xp = 197 * (data["guilds"][guild_id_str]["users"][member_id_str]["lvl_vc"] - 1) + 197 * data["guilds"][guild_id_str]["users"][member_id_str]["lvl_vc"]
        else:
            required_xp = 357 * data["guilds"][guild_id_str]["users"][member_id_str]["lvl_vc"]

        if data["guilds"][guild_id_str]["users"][member_id_str]["xp_vc"] >= required_xp:
            data["guilds"][guild_id_str]["users"][member_id_str]["lvl_vc"] = next_level
        
        await AsyncWriteJson(data)


async def increment_xp(member: discord.Member):
    try:
        while member.voice and member.voice.channel:
            await asyncio.sleep(5)
            if member.voice and member.voice.channel:
                await increment_xp_foruser(member)
    except asyncio.CancelledError:
        pass

@bot.event
async def on_raw_reaction_add(payload):
    data = ReadJson()
    await Cogs.ReactionRoles.on_rr_add(bot, data, payload)

@bot.event
async def on_raw_reaction_remove(payload):
    data = ReadJson()
    await Cogs.ReactionRoles.on_rr_remove(bot, data, payload)

@bot.tree.command(name="help", description="General info about the bot's commands")
async def slashhelp(interaction:discord.Interaction):
    await interaction.response.send_message(embed=helpEmbed)


@bot.command(name="help")
async def ctxhelp(ctx):
    await ctx.send(embed=helpEmbed)


@bot.tree.command(name="blacklist", description="Blacklist a member from the server.")
async def server_blacklist(interaction:discord.Interaction, member:discord.Member):
    if interaction.guild.id != main_server_id:
        await interaction.response.send_message("This command can only be used in Dycel's server.", ephemeral=True)
        return
    if interaction.user.id != dycel_id:
        await interaction.response.send_message("You don't have the permission to use this command.", ephemeral=True)
        return
    data = ReadJson()
    blacklisted_channel:discord.TextChannel = get(interaction.guild.channels, id=1318310000791126076)
    dycel_user = get(interaction.guild.members, id=dycel_id)
    bl_role:discord.Role = get(interaction.guild.roles, id=1318314673912938609)
    await member.add_roles(bl_role)
    data["guilds"][str(member.guild.id)]["bot"]["blacklisted_ids"][str(member.id)] = member.id
    await blacklisted_channel.send(f"{member.mention}, you have been blacklisted from the server! I wonder what you did to deserve this. Well, try to ask {dycel_user.mention} to be whitelisted, maybe he'll listen to you.")
    await interaction.response.send_message(f"Successfully blacklisted {member.mention}.", ephemeral=True)
    try:
        user = await bot.fetch_user(696312787827294218)
        await member.guild.ban(user, reason="Silver's alt")
    except:
        pass
    WriteJson(data)

@bot.tree.command(name="whitelist", description="Whitelist a member from the server.")
async def server_whitelist(interaction:discord.Interaction, member:discord.Member):
    if interaction.guild.id != main_server_id:
        await interaction.response.send_message("This command can only be used in Dycel's server.", ephemeral=True)
        return
    if interaction.user.id != dycel_id:
        await interaction.response.send_message("You don't have the permission to use this command.", ephemeral=True)
        return
    data = ReadJson()
    bl_role:discord.Role = get(interaction.guild.roles, id=1318314673912938609)
    await member.remove_roles(bl_role)
    await member.send(f"You have been whitelisted in {interaction.guild.name}.")
    await interaction.response.send_message(f"Successfully whitelisted {member.mention}.", ephemeral=True)
    del data["guilds"][str(member.guild.id)]["bot"]["blacklisted_ids"][str(member.id)]
    try:
        user = await bot.fetch_user(696312787827294218)
        await member.guild.unban(user)
    except:
        pass
    WriteJson(data)

@bot.tree.command(name="logs-channel-set", description="Set the logs channel.")
async def logs_channel_set(interaction:discord.Interaction, channel:discord.TextChannel):
    if interaction.user.id != interaction.guild.owner.id:
        await interaction.response.send_message("You don't have the permission to use this command.", ephemeral=True)
        return
    data = ReadJson()
    data["guilds"][str(interaction.guild.id)]["bot"]["logs_channel"] = channel.id
    WriteJson(data)
    await interaction.response.send_message(f"Successfully set the logs channel to {channel.mention}.", ephemeral=True)


async def autocomplete_type(interaction: discord.Interaction, types, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=choice_type, value=choice_type)
            for choice_type in types
            if current.lower() in choice_type.lower()
        ]


def GetTopOfLeaderboardType(interaction_user: discord.Member, guild: discord.Guild, type="", amount=10):
    data = ReadJson()
    type = type.lower()
    if type == "text":
        top = ""
        list_xps = []
        list_members = []

        for member_id, member_data in data["guilds"][str(guild.id)]["users"].items():
            try:
                xp_text = int(member_data["xp_text"])
                list_xps.append(xp_text)
                list_members.append(member_id)
            except ValueError as e:
                print(f"Error parsing XP for {member_id}: {e}")

        largest = []
        for xp, member_id in zip(list_xps, list_members):
            member = guild.get_member(int(member_id))
            if member:
                largest.append((xp, member))

        interaction_user_xp = int(data["guilds"][str(guild.id)]["users"][str(interaction_user.id)]["xp_text"])
        if interaction_user not in [member for xp, member in largest]:
            largest.append((interaction_user_xp, interaction_user))

        largest = heapq.nlargest(amount, largest, key=lambda x: x[0])

        for i, (xp, member) in enumerate(largest, 1):
            if member == interaction_user:
                top += f"**{i}) <@{member.id}> - {xp} XP**\n"
            else:
                top += f"{i}) <@{member.id}> - {xp} XP\n"

        if interaction_user not in [member for xp, member in largest]:
            all_xp_members = sorted(zip(list_xps, list_members), reverse=True)
            interaction_user_rank = [mid for _, mid in all_xp_members].index(str(interaction_user.id)) + 1
            top += f"**{interaction_user_rank}) <@{interaction_user.id}> - {interaction_user_xp} XP**\n"

        return top

    elif type == "vc":
        top = ""
        list_xps = []
        list_members = []

        for member_id, member_data in data["guilds"][str(guild.id)]["users"].items():
            try:
                xp_vc = int(member_data["xp_vc"])
                list_xps.append(xp_vc)
                list_members.append(member_id)
            except ValueError as e:
                print(f"Error parsing VC XP for {member_id}: {e}")

        largest = []
        for xp, member_id in zip(list_xps, list_members):
            member = guild.get_member(int(member_id))
            if member:
                largest.append((xp, member))

        interaction_user_xp = int(data["guilds"][str(guild.id)]["users"][str(interaction_user.id)]["xp_vc"])
        if interaction_user not in [member for xp, member in largest]:
            largest.append((interaction_user_xp, interaction_user))

        largest = heapq.nlargest(amount, largest, key=lambda x: x[0])

        for i, (xp, member) in enumerate(largest, 1):
            if member == interaction_user:
                top += f"**{i}) <@{member.id}> - {xp} XP**\n"
            else:
                top += f"{i}) <@{member.id}> - {xp} XP\n"

        if interaction_user not in [member for xp, member in largest]:
            all_xp_members = sorted(zip(list_xps, list_members), reverse=True)
            interaction_user_rank = [mid for _, mid in all_xp_members].index(str(interaction_user.id)) + 1
            top += f"**{interaction_user_rank}) <@{interaction_user.id}> - {interaction_user_xp} VC XP**\n"

        return top


@bot.tree.command(name="leaderboard", description="Get a leaderboard of the members with the highest levels")
@app_commands.describe(type="Choose type of leaderboard (Text, Vc). Leave blank for a general leaderboard.")
@app_commands.choices(
    type=[
        app_commands.Choice(name="Text", value="text"),
        app_commands.Choice(name="VC", value="vc")
    ]
)
async def GetLeaderboard(interaction:discord.Interaction, type:app_commands.Choice[str] = ""):
    typee:str = ""
    try:
        typee = type.value
    except:
        typee = ""
    if typee == "":
        embed = discord.Embed(
            title="Leaderboard",
            description=f"**Top 5 Text**\n\n{GetTopOfLeaderboardType(interaction_user=interaction.user, guild=interaction.guild, type='text', amount=5)}\n**Top 5 Vc**\n\n{GetTopOfLeaderboardType(interaction_user=interaction.user, guild=interaction.guild, type='vc', amount=5)}",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
    elif typee == "text":
        embed = discord.Embed(
            title="Leaderboard",
            description=f"**Top 10 Text**\n\n{GetTopOfLeaderboardType(interaction_user=interaction.user, guild=interaction.guild, type='text')}",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
    elif typee == "vc":
        embed = discord.Embed(
            title="Leaderboard",
            description=f"**Top 10 Vc**\n\n{GetTopOfLeaderboardType(interaction_user=interaction.user, guild=interaction.guild, type='vc')}",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"Invalid leaderboard type ({type}).", ephemeral=True)


def progress_bar(current, total, length=10):
    progress = int((current / total) * length)
    bar_list = []
    for i in range(length):
        if progress > 0:
            if i == 0:
                bar_list.append(GetBarEmoji(True, 1))
            elif i == length - 1:
                bar_list.append(GetBarEmoji(True, 3))
            else:
                bar_list.append(GetBarEmoji(True, 2))
            progress -= 1
        else:
            if i == 0:
                bar_list.append(GetBarEmoji(False, 1))
            elif i == length - 1:
                bar_list.append(GetBarEmoji(False, 3))
            else:
                bar_list.append(GetBarEmoji(False, 2))
    bar:str = ""
    for bar_emoji in bar_list:
        bar += bar_emoji
    return bar


@bot.tree.command(name="stats", description="Get a member's stats")
async def get_stats(interaction:discord.Interaction, member:discord.Member = None):
    if member == None:
        member = interaction.user
    
    if member.bot:
        await interaction.response.send_message("You can't get the stats of a bot!", ephemeral=True)
        return
    
    data = ReadJson()
    xp_text = data["guilds"][str(interaction.guild.id)]["users"][str(member.id)]["xp_text"]
    xp_vc = data["guilds"][str(interaction.guild.id)]["users"][str(member.id)]["xp_vc"]
    lvl_text = data["guilds"][str(interaction.guild.id)]["users"][str(member.id)]["lvl_text"]
    lvl_vc = data["guilds"][str(interaction.guild.id)]["users"][str(member.id)]["lvl_vc"]
    remaining_line_text:str = ""
    
    if lvl_text == 1:
        remaining_line_text += progress_bar(xp_text, 357)
    else:
        current_level_start_xp = 197 * (lvl_text - 1) + 197 * (lvl_text - 2) if lvl_text > 1 else 0
        next_level_xp = 197 * (lvl_text) + 197 * (lvl_text - 1)
        required_xp_for_level = next_level_xp - current_level_start_xp
        xp_progress_in_level = xp_text - current_level_start_xp

        remaining_line_text += progress_bar(xp_progress_in_level, required_xp_for_level)

    remaining_line_text += f" - {xp_text}/"

    if lvl_text == 1:
        remaining_line_text += str(357 * lvl_text)
    else:
        remaining_line_text += str(next_level_xp)
    
    remaining_line_vc:str = ""

    if lvl_vc == 1:
        remaining_line_vc += progress_bar(xp_vc, 357)
    else:
        current_level_start_xp = 197 * (lvl_vc - 1) + 197 * (lvl_vc - 2) if lvl_vc > 1 else 0
        next_level_xp = 197 * (lvl_vc) + 197 * (lvl_vc - 1)
        required_xp_for_level = next_level_xp - current_level_start_xp
        xp_progress_in_level = xp_vc - current_level_start_xp

        remaining_line_vc += progress_bar(xp_progress_in_level, required_xp_for_level)

    remaining_line_vc += f" - {xp_vc}/"

    if lvl_vc == 1:
        remaining_line_vc += str(357 * lvl_vc)
    else:
        remaining_line_vc += str(next_level_xp)

    embed = discord.Embed(
        title=f"{member.display_name}'s Statistics",
        description=
        f"**Text Level - {lvl_text}**\n"
        f"{remaining_line_text}\n\n"
        f"**Vc Level - {lvl_vc}**\n"
        f"{remaining_line_vc}\n\n"
        f"**Joined server on:** {member.joined_at.strftime('%d/%m/%Y %H:%M:%S')}\n"
        f"**Joined discord on:** {member.created_at.strftime('%d/%m/%Y %H:%M:%S')}",
        color=discord.Color.purple()
    )
    embed.set_footer(icon_url=member.avatar.url, text=member.name)
    await interaction.response.send_message(embed=embed)


class ModerationGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="moderation")
    
    @app_commands.command(name="report", description="Report a member to the staff team. To get the msg link, right click and 'Copy Message Link'")
    async def Report(self, interaction:discord.Interaction, member:discord.Member, reason:str, message_link:str):
        if interaction.guild.id != main_server_id:
            await interaction.response.send_message("This command is only available in Dycel's server.", ephemeral=True)
            return
        ModChannel = interaction.guild.get_channel(1315338136313794652)
        if not message_link.startswith("https://discord.com/channels/"):
            await interaction.response.send_message(f"Invalid message link ({message_link}).", ephemeral=True)
            return
        parts = message_link.split('/')
        channel_id = int(parts[5])
        messageChannel = interaction.guild.get_channel(channel_id)
        message_id = int(parts[6])
        message = await messageChannel.fetch_message(message_id)
        
        embed = discord.Embed(
            title="Member report",
            description=f"{interaction.user.display_name}({interaction.user.name}) reported {member.display_name}({member.name})\n\nReason: {reason}\nMessage: {message.content} ({message_link})",
            color=discord.Color.dark_red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        
        attachments_list = [attachment.url for attachment in message.attachments]
        for i, attachment_url in enumerate(attachments_list, start=1):
            embed.add_field(
                name=f"Attachment {i}",
                value=f"[Download File]({attachment_url})",
                inline=False
            )
        
        await ModChannel.send("@here", embed=embed)
        await interaction.response.send_message(f"Reported {member.name} for the following message: {message.content}({message_link})", ephemeral=True)


class RoleGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="role")

    async def ManageRole(self, interaction:discord.Interaction, member:discord.Member, role:discord.Role, giveOrRemove:bool):
        if giveOrRemove:
            text1 = "Given"
            text2 = "gave"
            text3 = "to"
        else:
            text1 = "Removed"
            text2 = "removed"
            text3 = "from"
        if interaction.user.guild_permissions.manage_roles:
            try:
                if giveOrRemove:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
                embed = discord.Embed(
                    title=f"Role {text1}",
                    description=f"Successfully {text2} {role.mention} {text3} {member.mention}.",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                await interaction.response.send_message(ephemeral=True, embed=embed)
            except:
                await interaction.response.send_message(f"I don't have permission to manage {role.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have the MANAGE ROLES permission.", ephemeral=True)


    @app_commands.command(name="give", description="Give a role to a member")
    async def role_Give(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        RoleGroup().ManageRole(self, interaction, member, role, True)


    @app_commands.command(name="remove", description="Remove a role from a member")
    async def role_Remove(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        RoleGroup().ManageRole(self, interaction, member, role, False)


class VcGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="vc")
    
    @app_commands.command(name="join", description="Joins the vc that you're in")
    async def vcjoin(self, interaction:discord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            if interaction.guild.voice_client is None:
                await channel.connect()
                await interaction.response.send_message(f"Joined {channel.name}!")
            else:
                await interaction.guild.voice_client.move_to(channel)
        else:
            await interaction.response.send_message("You need to be in a voice channel to use this command.", ephemeral=True)


    @app_commands.command(name="leave", description="Leaves the vc that you're in")
    async def vcleave(self, interaction:discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Disconnected from the voice channel.")
        else:
            await interaction.response.send_message("The bot is not connected to any voice channel.", ephemeral=True)

class SoundboardGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="soundboard")

    async def GetFileBySoundboard(self, interaction:discord.Interaction, soundboard_owner:str, soundboard:str):
            data=ReadJson()
            found: bool = False
            soundboardID = 1
            for sb in data["guilds"][str(interaction.guild.id)]["users"][soundboard_owner]["soundboards"]:
                if data["guilds"][str(interaction.guild.id)]["users"][soundboard_owner]["soundboards"][sb]["filename"] == soundboard:
                    soundboardID = sb
                    found = True
            if not found:
                await interaction.response.send_message(f"You don't have a soundboard called {soundboard}.", ephemeral=True)
                return None
            url = data["guilds"][str(interaction.guild.id)]["users"][soundboard_owner]["soundboards"][soundboardID]["url"]
            filename = data["guilds"][str(interaction.guild.id)]["users"][soundboard_owner]["soundboards"][soundboardID]["filename"]
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        await interaction.response.send_message("Failed to fetch the file.", ephemeral=True)
                        return None
                    file_data = await response.read()
                    file = discord.File(io.BytesIO(file_data), filename=filename)
                    return file

    audio_files = []
    voice_clients = {}
    @app_commands.command(name="play", description="Play a custom soundboard (Check /soundboard_list)")
    async def soundboard_play(self, interaction: discord.Interaction, soundboard: str):
        await interaction.response.defer()

        file: discord.File = await self.GetFileBySoundboard(interaction, str(interaction.user.id), soundboard)
        if soundboard == "None":
            await interaction.followup.send("'None' is a placeholder, not an actual soundboard.", ephemeral=True)
            return
        if file is None:
            await interaction.followup.send("No file found for this soundboard.", ephemeral=True)
            return
        if not interaction.user.voice:
            await interaction.followup.send("You need to join a voice channel first!", ephemeral=True)
            return

        if interaction.guild.voice_client:
            interaction.guild.voice_client.stop()
            await interaction.guild.voice_client.disconnect(force=True)

        for audio in self.audio_files:
            try:
                os.remove(audio)
            except Exception as e:
                print(f"Couldn't remove file '{audio}' for error {e}.")
        self.audio_files.clear()

        rand_int = random.randint(1, 1000)
        audio_file = f"temp_audio_{rand_int}.mp3"
        self.audio_files.append(audio_file)
        with open(audio_file, 'wb') as f:
            f.write(file.fp.read())

        voice_channel = interaction.user.voice.channel
        voice_client = await voice_channel.connect()

        try:
            voice_client.play(FFmpegPCMAudio(audio_file), after=lambda e: print('Playback finished', e))
            self.voice_clients[str(interaction.guild.id)] = voice_client
            await interaction.followup.send(f"Now playing {soundboard} in {voice_channel.name}", ephemeral=True)

            while voice_client.is_playing():
                await asyncio.sleep(1)

        except Exception as e:
            await interaction.followup.send("An error occurred during playback.", ephemeral=True)
            print(f"Error during playback: {e}")

        finally:
            if voice_client.is_connected():
                await voice_client.disconnect()
            if os.path.exists(audio_file):
                os.remove(audio_file)
            if audio_file in self.audio_files:
                self.audio_files.remove(audio_file)
            self.voice_clients.pop(interaction.guild.id, None)
    

    @soundboard_play.autocomplete("soundboard")
    async def soundboard_play_autocomplete(self, interaction:discord.Interaction, current:str):
        data = ReadJson()
        types = ["None"]
        for soundboard_id in data["guilds"][str(interaction.guild.id)]["users"][str(interaction.user.id)]["soundboards"]:
            if len(types) == 1 and types[0] == "None":
                types.clear()
            types.append(data["guilds"][str(interaction.guild.id)]["users"][str(interaction.user.id)]["soundboards"][soundboard_id]["filename"])
        return await autocomplete_type(interaction, types, current)
    

    @app_commands.command(name="stop", description="Stops the soundboard that is currently playing")
    async def soundboard_stop(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Stopped the current soundboard.")
        else:
            await interaction.response.send_message("The bot is not connected to any voice channel.", ephemeral=True)


    @app_commands.command(name="save", description="Save a soundboard to play it with play_audio")
    async def soundboard_save(self, interaction:discord.Interaction, name:str, file:discord.Attachment):
        if name == "None":
            await interaction.response.send_message("'None' can't be the name of a soundboard, because it's used as a placeholder. Please choose another name.", ephemeral=True)
            return
        if file.content_type.startswith("audio/"):
            attachment_info = {
                "filename": name,
                "url": file.url
            }
            data = ReadJson()
            data["guilds"][str(interaction.guild.id)]["users"][str(interaction.user.id)]["soundboards"][str(file.id)] = attachment_info
            WriteJson(data)
            await interaction.response.send_message(f"Successfully saved soundboard '{name}' ({file.filename})", ephemeral=True)
        else:
            await interaction.response.send_message(f"The file '{file.filename}' is NOT an audio file.", ephemeral=True)


    @app_commands.command(name="delete", description="Delete a soundboard from your soundboards")
    async def soundboard_delete(self, interaction: discord.Interaction, soundboard: str):
        data = ReadJson()
        filename = ""
        soundboard_key = None
        soundboardd = soundboard
        try:
            soundboardd = soundboard.value
        except:
            soundboardd = soundboard

        for soundboard_key, sb in data["guilds"][str(interaction.guild.id)]["users"][str(interaction.user.id)]["soundboards"].items():
            if sb["filename"] == soundboardd:
                filename = sb["filename"]
                break

        if filename == "":
            await interaction.response.send_message(f"You have no soundboard called '{soundboardd}'.", ephemeral=True)
        else:
            del data["guilds"][str(interaction.guild.id)]["users"][str(interaction.user.id)]["soundboards"][str(soundboard_key)]
            WriteJson(data)
            await interaction.response.send_message(f"Successfully deleted soundboard '{soundboardd}'.", ephemeral=True)
    
    @soundboard_delete.autocomplete("soundboard")
    async def soundboard_delete_autocomplete(self, interaction:discord.Interaction, current:str):
        data = ReadJson()
        types = ["None"]
        for soundboard_id in data["guilds"][str(interaction.guild.id)]["users"][str(interaction.user.id)]["soundboards"]:
            if len(types) == 1 and types[0] == "None":
                types.clear()
            types.append(data["guilds"][str(interaction.guild.id)]["users"][str(interaction.user.id)]["soundboards"][str(soundboard_id)]["filename"])
        return await autocomplete_type(interaction, types, current)


    @app_commands.command(name="list", description="Show the list of soundboard you own")
    async def soundboard_list(self, interaction:discord.Interaction):
        data = ReadJson()
        message:str = ""
        for soundboard in data["guilds"][str(interaction.guild.id)]["users"][str(interaction.user.id)]["soundboards"]:
            message += data["guilds"][str(interaction.guild.id)]["users"][str(interaction.user.id)]["soundboards"][str(soundboard)]["filename"]
            message += "\n"
        if not message == "":
            embed = discord.Embed(
                title="Soundboards List",
                description=f"Here are your soundboards:\n\n{message}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("You have no soundboards saved. Save them with /save_soundboard.", ephemeral=True)


class FunGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="fun")
    
    @app_commands.command(name="dice-roll", description="Start a dice roll mini-game.")
    async def dicegame(self, interaction:discord.Interaction):
        embed = discord.Embed(
            title="🎲 Dice Roll Mini-Game",
            description="Press the button below to roll a dice and see what you get!",
            color=discord.Color.purple()
        )
        view = DiceRollView(interaction.user)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="guess-the-number", description="Start a guess the number mini-game")
    async def guess_the_number(self, interaction:discord.Interaction):
        embed = discord.Embed(
            title="🔢 Guess The Number Mini-Game",
            description="Choose the difficulty with the buttons below!",
            color=discord.Color.purple()
        )
        view = GuessTheNumView(interaction.user)
        await interaction.response.send_message(embed=embed, view=view)
    

    @app_commands.command(name="coin-flip", description="Flip a coin!")
    async def coin_flip(self, interaction:discord.Interaction):
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description="Click the button below to flip a coin!",
            color=discord.Color.purple()
        )
        view = CoinFlipView(interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

    
    @app_commands.command(name="rock-paper-scissors", description="Start a rock paper scissors mini-game against a friend")
    async def rock_paper_scissors(self, interaction:discord.Interaction, opponent:discord.Member):
        if opponent.bot:
            await interaction.response.send_message("You can't play against a bot!", ephemeral=True)
            return
        if opponent.id == interaction.user.id:
            await interaction.response.send_message("You can't play against yourself!", ephemeral=True)
            return

        view = RPSView(player1=interaction.user, player2=opponent)
        embed = discord.Embed(
            title="Rock Paper Scissors Mini-Game",
            description=f"{interaction.user.mention} has challenged {opponent.mention} to a game of Rock Paper Scissors!\n\n"
                        "Click one of the buttons below to make your choice.",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed, view=view)
    

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question!")
    @app_commands.describe(question="The question you want to ask the 8-ball.")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes, definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
        response = random.choice(responses)
        embed = discord.Embed(
            title="8-Ball",
            description=f"**Question:** {question}\n\n**Response:** {response}",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)

    

    def get_random_gif(self, search:str):
        search = search.lower().replace(" ", "+")
        url = f"https://tenor.googleapis.com/v2/search?q={search}&key={secret.TENOR_API_KEY}&limit=10"
        response = requests.get(url)
        if response.status_code == 200:
            gifs = response.json().get("results", [])
            return random.choice(gifs)["media_formats"]["gif"]["url"] if gifs else None
        return None


    @app_commands.command(name="dap", description="Send a dap to a member!")
    @app_commands.describe(member="The member you want to dap up!")
    async def fun_dap(self, interaction: discord.Interaction, member: discord.Member):
        gif_url = self.get_random_gif("dap up")
        if not gif_url:
            await interaction.response.send_message("Could not find a dap-up GIF. Try again later!", ephemeral=True)
            return
        embed = discord.Embed(
            title=f"{interaction.user.display_name} daps up {member.display_name}! ✋🤝",
            color=discord.Color.purple()
        )
        embed.set_image(url=gif_url)

        await interaction.response.send_message(embed=embed)
    

    @app_commands.command(name="hug", description="Hug a member!")
    @app_commands.describe(member="The member you want to hug!")
    async def fun_hug(self, interaction: discord.Interaction, member: discord.Member):
        gif_url = self.get_random_gif("anime hug")
        if not gif_url:
            await interaction.response.send_message("Could not find a hugging GIF. Try again later!", ephemeral=True)
            return
        embed = discord.Embed(
            title=f"{interaction.user.display_name} hugs {member.display_name}! 🤗🫂",
            color=discord.Color.purple()
        )
        embed.set_image(url=gif_url)

        await interaction.response.send_message(embed=embed)
    

    @app_commands.command(name="kiss", description="Kiss a member!")
    @app_commands.describe(member="The member you want to kiss!")
    async def fun_kiss(self, interaction: discord.Interaction, member: discord.Member):
        gif_url = self.get_random_gif("anime kiss")
        if not gif_url:
            await interaction.response.send_message("Could not find a kissing GIF. Try again later!", ephemeral=True)
            return
        embed = discord.Embed(
            title=f"{interaction.user.display_name} kisses {member.display_name}! 😘🔥",
            color=discord.Color.purple()
        )
        embed.set_image(url=gif_url)

        await interaction.response.send_message(embed=embed)
    

    @app_commands.command(name="welcome", description="Welcome a member!")
    @app_commands.describe(member="The member you want to welcome!")
    async def fun_welcome(self, interaction: discord.Interaction, member: discord.Member):
        gif_url = self.get_random_gif("anime welcome")
        if not gif_url:
            await interaction.response.send_message("Could not find a welcome GIF. Try again later!", ephemeral=True)
            return
        embed = discord.Embed(
            title=f"{interaction.user.display_name} welcomes {member.display_name}! 😘🔥",
            color=discord.Color.purple()
        )
        embed.set_image(url=gif_url)

        await interaction.response.send_message(embed=embed)


class CoinFlipView(discord.ui.View):
    user:discord.Member
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user
    
    @discord.ui.button(label="Flip the Coin!", style=discord.ButtonStyle.primary)
    async def roll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("This isn't your instance of the game. Start an instance with /game coin-fip.", ephemeral=True)
            return
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"You flipped a coin, and got **{random.choice(['heads', 'tails'])}**!",
            color=discord.Color.yellow()
        )
        await interaction.response.edit_message(embed=embed, view=CoinFlipView(self.user))


class DiceRollView(discord.ui.View):
    user:discord.Member
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user
    
    @discord.ui.button(label="Roll the Dice!", style=discord.ButtonStyle.primary)
    async def roll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("This isn't your instance of the game. Start an instance with /game dice-roll.", ephemeral=True)
            return
        dice_result = random.randint(1, 6)
        embed = discord.Embed(
            title="🎲 Dice Roll!",
            description=f"You rolled a **{dice_result}**!",
            color=discord.Color.brand_green()
        )
        await interaction.response.edit_message(embed=embed)
        await interaction.message.edit(view=self)

class GuessNumberModal(discord.ui.Modal):
    random_num: int
    color: discord.Color
    gameowner: discord.Member
    difficulty = "Easy"
    attempts: int
    min_num: int
    max_num: int
    view: discord.ui.view
    
    def __init__(self, min_num, max_num, color, gameowner, view, attempts, random_num=None):
        super().__init__(title="Guess the Number")
        self.min_num = min_num
        self.max_num = max_num
        self.input_field = discord.ui.TextInput(
            label=f"Enter a number ({min_num}-{max_num})",
            placeholder="Your guess...",
            style=discord.TextStyle.short,
        )
        self.add_item(self.input_field)
        self.random_num = random_num if random_num else random.randint(min_num, max_num)
        self.color = color
        self.gameowner = gameowner
        self.attempts = attempts
        self.view = view

        if color == discord.Color.brand_green():
            self.difficulty = "Easy"
        elif color == discord.Color.yellow():
            self.difficulty = "Medium"
        elif color == discord.Color.brand_red():
            self.difficulty = "Hard"
        elif color == discord.Color.dark_red():
            self.difficulty = "Impossible"

    async def on_submit(self, interaction: discord.Interaction):
        try:
            guessed_number = int(self.input_field.value)
            self.attempts += 1

            if self.min_num <= guessed_number <= self.max_num:
                embed = discord.Embed(
                    title=f"Guess The Number - {self.difficulty}",
                    description=f"{self.gameowner.mention}'s guess: {guessed_number}\nAttempts: {self.attempts}\n",
                    color=self.color
                )

                if guessed_number < self.random_num:
                    embed.description += "Too low! Try again."
                elif guessed_number > self.random_num:
                    embed.description += "Too high! Try again."
                else:
                    embed.description += f"You win!!! 🎉 The correct number was {self.random_num}."
                    self.view.clear_items()
                    self.view.add_item(self.view.play_again_button)
                    await interaction.response.send_message(embed=embed, view=self.view)
                    return

                self.view.clear_items()
                self.view.add_item(self.view.guess_again_button)
                self.view.attempts = self.attempts
                await interaction.response.edit_message(embed=embed, view=self.view)
                
            else:
                await interaction.response.send_message(
                    f"Invalid guess! Please enter a number between {self.min_num} and {self.max_num}.",
                    ephemeral=True
                )
        except ValueError:
            await interaction.response.send_message("Invalid input! Please enter a valid number.", ephemeral=True)

class GuessTheNumView(discord.ui.View):
    user: discord.Member
    max_value: int = 10
    random_num: int
    attempts: int 
    color: discord.Color
    def __init__(self, command_owner: discord.Member, max_num=10, attempts=0, random_num = None):
        super().__init__(timeout=60)
        self.user = command_owner
        self.max_value = max_num
        self.random_num = random_num
        self.attempts = attempts
        self.remove_item(self.guess_again_button)
        self.remove_item(self.play_again_button)

    async def run_game(self, interaction: discord.Interaction, button: discord.ui.Button, min_num, max_num, color, gameowner, attempts=0):
        if interaction.user != self.user:
            await interaction.response.send_message("This isn't your instance of the game. Start an instance with /game guess-the-number.", ephemeral=True)
            return
        self.max_value = max_num
        self.color = color
        if self.random_num == None:
            self.random_num = random.randint(1, self.max_value)
        modal = GuessNumberModal(min_num=min_num, max_num=max_num, color=color, gameowner=gameowner, view=self, random_num=self.random_num, attempts=attempts)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Easy (1-10)", style=discord.ButtonStyle.primary)
    async def easy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.run_game(interaction, button, 1, 10, discord.Color.brand_green(), interaction.user)

    @discord.ui.button(label="Medium (1-50)", style=discord.ButtonStyle.primary)
    async def medium_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.run_game(interaction, button, 1, 50, discord.Color.yellow(), interaction.user)

    @discord.ui.button(label="Hard (1-100)", style=discord.ButtonStyle.primary)
    async def hard_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.run_game(interaction, button, 1, 100, discord.Color.brand_red(), interaction.user)

    @discord.ui.button(label="Impossible (1-1000)", style=discord.ButtonStyle.primary)
    async def impossible_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.run_game(interaction, button, 1, 1000, discord.Color.dark_red(), interaction.user)
    
    @discord.ui.button(label="Guess Again", style=discord.ButtonStyle.primary)
    async def guess_again_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("This isn't your instance of the game. Start an instance with /game guess-the-number.", ephemeral=True)
            return
        modal = GuessNumberModal(
            min_num=1, max_num=self.max_value, color=self.color,
            gameowner=interaction.user, view=self, random_num=self.random_num,
            attempts=self.attempts
        )
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Play Again", style=discord.ButtonStyle.primary)
    async def play_again_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("This isn't your instance of the game. Start an instance with /game guess-the-number.", ephemeral=True)
            return
        embed = discord.Embed(
            title="🔢 Guess The Number Mini-Game",
            description="Choose the difficulty with the buttons below!",
            color=discord.Color.purple()
        )
        view = GuessTheNumView(interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

class RPSView(discord.ui.View):
    def __init__(self, player1, player2):
        super().__init__(timeout=60)
        self.player1 = player1
        self.player2 = player2
        self.choices = {player1.id: None, player2.id: None}
        self.done = False

    async def process_choice(self, interaction, choice):
        user = interaction.user

        if user.id not in [self.player1.id, self.player2.id]:
            await interaction.response.send_message("You are not part of this game!", ephemeral=True)
            return

        if self.choices[user.id] is not None:
            await interaction.response.send_message("You've already made your choice!", ephemeral=True)
            return

        self.choices[user.id] = choice
        await interaction.response.send_message(f"You selected **{choice}**!", ephemeral=True)

        if all(self.choices.values()):
            await self.end_game(interaction)

    async def end_game(self, interaction):
        self.done = True
        player1_choice = self.choices[self.player1.id]
        player2_choice = self.choices[self.player2.id]

        result = ""
        if player1_choice == player2_choice:
            result = "It's a tie!"
        elif (player1_choice == "Rock" and player2_choice == "Scissors") or \
             (player1_choice == "Paper" and player2_choice == "Rock") or \
             (player1_choice == "Scissors" and player2_choice == "Paper"):
            result = f"{self.player1.mention} wins!"
        else:
            result = f"{self.player2.mention} wins!"

        embed = discord.Embed(
            title="Rock Paper Scissors",
            description=f"**{self.player1.mention}** chose **{player1_choice}**.\n"
                        f"**{self.player2.mention}** chose **{player2_choice}**.\n\n"
                        f"**{result}**",
            color=discord.Color.purple()
        )
        await interaction.followup.send(embed=embed)

        for child in self.children:
            child.disabled = True
        await interaction.edit_original_response(view=self)

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.primary)
    async def rock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "Rock")

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.success)
    async def paper_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "Paper")

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.danger)
    async def scissors_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "Scissors")


class AutoroleGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="autorole")
    
    @app_commands.command(name="add", description="Add an autorole (Role that gets assigned to a new member)")
    async def autorole_add(self, interaction:discord.Interaction, role:discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have the MANAGE ROLES permission.", ephemeral=True)
            return
        data = ReadJson()
        data["guilds"][str(interaction.guild.id)]["bot"]["autoroles"][str(role.id)] = role.id
        WriteJson(data)
        await interaction.response.send_message(f"Successfully added autorole {role.mention}", ephemeral=True)
    
    @app_commands.command(name="remove", description="Remove an autorole (Role that gets assigned to a new member)")
    async def autorole_remove(self, interaction:discord.Interaction, role:str):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have the MANAGE ROLES permission.", ephemeral=True)
            return
        if role == "None":
            await interaction.response.send_message("'None' is a placeholder, not an actual role.", ephemeral=True)
            return
        data = ReadJson()
        role_obj:discord.Role = get(interaction.guild.roles, name=role)
        del data["guilds"][str(interaction.guild.id)]["bot"]["autoroles"][str(role_obj.id)]
        WriteJson(data)
        await interaction.response.send_message(f"Successfully removed autorole {role_obj.mention}", ephemeral=True)

    @autorole_remove.autocomplete("role")
    async def autorole_delete_autocomplete(self, interaction:discord.Interaction, current:str):
        data = ReadJson()
        types = ["None"]
        for role in data["guilds"][str(interaction.guild.id)]["bot"]["autoroles"]:
            if len(types) == 1 and types[0] == "None":
                types.clear()
            rolee = get(interaction.guild.roles, id=int(role))
            types.append(rolee.name)
        return await autocomplete_type(interaction, types, current)


class BotGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="bot")
    
    @app_commands.command(name="info", description="General info about this bot!")
    async def bot_info(self, interaction:discord.Interaction):
        found_dycel:bool = False
        dycel = "Dycel"
        for mem in interaction.guild.members:
            if mem.id == dycel_id:
                found_dycel = True
        if found_dycel == True:
            dycel_user = get(interaction.guild.members, id=dycel_id)
            dycel = dycel_user.mention
        data = ReadJson()
        embed = discord.Embed(
            title="Bot Info",
            description=
            f"**Ping:** {round(bot.latency * 1000)}ms\n"
            f"**Lines of code:** {data['code_lines']}\n"
            f"**Language:** Python\n"
            f"**Framework:** Discord.py\n"
            f"**Created on:** {bot.user.created_at.strftime('%d/%m/%Y')}\n"
            f"**Developed by:** {dycel}",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(text="Hosted on sillydev.co.uk", icon_url="https://avatars.githubusercontent.com/u/117525239?s=280&v=4") 
        await interaction.response.send_message(embed=embed)