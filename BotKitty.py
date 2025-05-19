import discord, secret, os, json, random, time, asyncio, utils, Cogs.ReactionRoles
from discord import app_commands, Color
from discord.ext import commands
from discord.utils import get
from groq import Groq
from Cogs.AI_Commands import setup as setup_ai_commands
from Cogs.ReactionRoles import setup as setup_reaction_roles
from Cogs.BugReport import setup as setup_bug_report
from Cogs.SuggestionGive import setup as setup_suggestion
from Cogs.Music_Commands import setup as setup_music_commands
from Cogs.Economy import setup as setup_economy

client = Groq(
    api_key=secret.GROQ_API_KEY,
)

token = secret.KITTYTOKEN

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)


emoji_num1 = "<:Number1:1331742901138358312>"
emoji_num2 = "<:Number2:1331742933455736842>"
emoji_num3 = "<:Number3:1331742955899191316>"
emoji_num4 = "<:Number4:1331742977370095696>"
emoji_num5 = "<:Number5:1331743024195043411>"
emoji_num6 = "<:Number6:1331743048840777811>"
emoji_num7 = "<:Number7:1331743070894686278>"
emoji_num8 = "<:Number8:1331743095200419902>"
emoji_num9 = "<:Number9:1331743116071272488>"
emoji_num10 = "<:Number10:1331743141706858546>"
emoji_num11 = "<:Number11:1352743019673026570>"
emoji_num12 = "<:Number12:1352743028040929291>"
emoji_num13 = "<:Number13:1352743035632619521>"
emoji_num14 = "<:Number14:1352743044046389361>"
emoji_num15 = "<:Number15:1352743051012870254>"

color_purple = discord.Color.from_str("#8a31de")

dycel_id = 1099017318232764447 
general_id = 1315433980769865861
intros_id = 1315434980138156082
roles_id = 1315440407437643816

def ReadJson(file='kittydatabase.json'):
    file_path = os.path.join('Databases', file)
    if not os.path.exists(file_path):
        WriteJson({}, file)
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)

def WriteJson(data, file='kittydatabase.json', indent=4):
    file_path = os.path.join('Databases', file)
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=indent)

async def SetPresence():
    await discord.Client.change_presence(
        status=discord.Status.idle,    activity=discord.Activity(
    type=discord.ActivityType.playing, name="with cats"
            ), self=bot
        )

async def DataGen():
    if not utils.path_exists("kittydatabase.json"):
        WriteJson({})
    
    data = ReadJson()
    for guild in bot.guilds:
        guild_id = str(guild.id)
        guild_data = data.setdefault("guilds", {}).setdefault(guild_id, {})
        memberdata = guild_data.setdefault("members", {})
        botdata = guild_data.setdefault("bot", {})
        rrdata = botdata.setdefault("rr_messages", {})
        
        for member in guild.members:
            if not member.bot:
                _ = guild_data["members"].setdefault(str(member.id), {})
                _bal = _.setdefault("balance", {})
                _bal.setdefault("wallet", 0)
                _bal.setdefault("bank", 0)
    
    WriteJson(data)

@bot.event
async def on_raw_reaction_add(payload):
    data = ReadJson()
    await Cogs.ReactionRoles.on_rr_add(bot, data, payload)

@bot.event
async def on_raw_reaction_remove(payload):
    data = ReadJson()
    await Cogs.ReactionRoles.on_rr_remove(bot, data, payload)

emojisList = [emoji_num1, emoji_num2, emoji_num3, emoji_num4, emoji_num5, emoji_num6, emoji_num7, emoji_num8, emoji_num9, emoji_num10, emoji_num11, emoji_num12, emoji_num13, emoji_num14, emoji_num15]

async def add_cogs():
    await setup_bug_report(bot)
    await setup_ai_commands(bot, client)
    await setup_reaction_roles(bot, "kittydatabase.json", emojisList, ["rr"])
    await setup_suggestion(bot)
    await setup_music_commands(bot)
    await setup_economy(bot, 1315433980258029588, "kittydatabase.json")

@bot.event
async def on_ready(): 
    await SetPresence()
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    await DataGen()
    bot.tree.add_command(JoinsGroup())
    await add_cogs()
    await bot.tree.sync()


async def AskAI(question:str):
    if len(question) > 400:
        return None
    await asyncio.sleep(0)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{question}",
            }
        ],
        model="llama-3.1-8b-instant",
        timeout=1
    )

    return chat_completion.choices[0].message.content

async def AskAISmart(question: str):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{question}",
                }
            ],
            model="llama-3.3-70b-versatile",
            timeout=10
        )

        return chat_completion.choices[0].message.content

    except asyncio.TimeoutError:
        return "Error: The AI took too long to respond. Please try again later."
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"


async def HasMeow(message: discord.Message):
    try:
        AI_result = await AskAI(f"Check if this sentence is trying to mean 'meow'. If yes, reply with 'Yes.'. Else, reply with 'No.'. '{message.content}'")
        
        if AI_result == "Yes.":
            return True
        else:
            return False
    except Exception as e:
        print(f"Error in HasMeow: {e}")
        return False

async def HasPurr(message: discord.Message):
    try:
        AI_result = await AskAI(f"Check if this sentence is trying to mean 'purr'. If yes, reply with 'Yes.'. Else, reply with 'No.'. '{message.content}'")
        
        if AI_result == "Yes.":
            return True
        else:
            return False
    except Exception as e:
        print(f"Error in HasPurr: {e}")
        return False


async def CheckCat(message:discord.Message):
    if message.channel.id == 1332196842544562257:
        if await HasMeow(message):
            await message.reply(GetMeow())
        elif await HasPurr(message):
            await message.reply(GetPurr())


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)
    await CheckCat(message)


    print(f"{message.author.name} said: '{message.content}'")

def GetMeow():
    try:
        if not utils.path_exists("meowbase.json"):
            WriteJson({"meows":["dycel is an idiot, tell him to fix the meowbase"], "purrs":["dycel is an idiot, tell him to fix the meowbase"]}, "meowbase.json")
        
        data = ReadJson("meowbase.json")
        meow = random.choice(data["meows"])

        return meow
    except:
        print("Error in GetMeow(). Trying again...")
        return GetMeow()


def GetPurr():
    try:
        if not utils.path_exists("meowbase.json"):
            WriteJson({"meows":["dycel is an idiot, tell him to fix the meowbase"], "purrs":["dycel is an idiot, tell him to fix the meowbase"]}, "meowbase.json")
        
        data = ReadJson("meowbase.json")
        purr = random.choice(data["purrs"])

        return purr
    except:
        print("Error in GetPurr(). Trying again...")
        return GetPurr()

def MakeJoinEmbed(member:discord.Member):
    channel_roles = member.guild.get_channel(roles_id)
    channel_intros = member.guild.get_channel(intros_id)
    embed = discord.Embed(
        title="Welcome",
        description=f"Welcome to {member.guild.name}, {member.mention}!\nCheck out {channel_intros.mention} to introduce yourself, and {channel_roles.mention} to get some roles!",
        color=color_purple
    )
    embed.set_footer(text=bot.user.display_name, icon_url=bot.user.avatar.url)
    return embed

@bot.event
async def on_member_join(member:discord.Member):
    kittyrole:discord.Role = None
    roles = await member.guild.fetch_roles()
    for role in roles:
        if role.id == 1315441052320141362:
            kittyrole = role
            break
    join_msg = f"{member.display_name} has joined the server."
    data = ReadJson()
    guild_id = str(member.guild.id)

    if not member.bot:
        if data["guilds"][guild_id]["joins"] == True:
            if kittyrole == None:
                print("kittyrole is None")
            else:
                try:
                    await member.add_roles(kittyrole)
                except Exception as e:
                    print(f"Error when assigning member role: {e}")
            channel = member.guild.get_channel(general_id)
            channel.send(embed=MakeJoinEmbed(member))
        else:
            await member.send("Joins are currently disabled in the kitty server.")
            await member.kick()
            join_msg += " But got kicked, due to joins being off."
            print(join_msg)
            return

    print(join_msg)


@bot.tree.command(name="meow", description="Meow")
async def meow(interaction:discord.Interaction):
    await interaction.response.send_message(GetMeow())

@bot.tree.command(name="purr", description="Purr")
async def purr(interaction:discord.Interaction):
    await interaction.response.send_message(GetPurr())


class JoinsGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="joins")

    @app_commands.command(name="enable", description="Enables member joins")
    async def joins_enable(self, interaction:discord.Interaction):
        if not interaction.permissions.moderate_members:
            await interaction.response.send_message("You don't have the MODERATE MEMBERS permission to use this command.", ephemeral=True)
            return
        
        data = ReadJson()
        guild_id = str(interaction.guild_id)
        if data["guilds"][guild_id]["joins"] == False:
            data["guilds"][guild_id]["joins"] = True
            await interaction.response.send_message("Successfully enabled joins.")
            WriteJson(data)
            return
        else:
            await interaction.response.send_message("Joins are already enabled", ephemeral=True)
            return
    
    @app_commands.command(name="disable", description="Disables member joins")
    async def joins_disable(self, interaction:discord.Interaction):
        if not interaction.permissions.moderate_members:
            await interaction.response.send_message("You don't have the MODERATE MEMBERS permission to use this command.", ephemeral=True)
            return
        
        data = ReadJson()
        guild_id = str(interaction.guild_id)
        if data["guilds"][guild_id]["joins"] == True:
            data["guilds"][guild_id]["joins"] = False
            await interaction.response.send_message("Successfully disabled joins.")
            WriteJson(data)
            return
        else:
            await interaction.response.send_message("Joins are already disabled", ephemeral=True)
            return


# MISC COMMANDS

async def ShipEmbed(member1:str, member2:str):
    data = ReadJson("kittyships.json")
    current = data[f"{member1} - {member2}"]
    desc = "**Hmmm, I wonder if we have a new couple here?**\n"
    AI_Request = await AskAI(f"Generate a ship name with the 2 names that I give you. If they were like 'Mark' and 'Dog' it'd be something like 'Maog'. They can also not be actual names, but letters or other words (example: if it was 's' and 'z', it would be 'sz'). Reply with only the ship name, case sensitive to the names. '{member1}' and '{member2}'")
    desc += f"`{member1}` + `{member2}` = ✨ `{AI_Request}` ✨\n"
    quote = ""
    desc += quote
    percent = f"**{current}%**"
    desc += percent
    embed = discord.Embed(
        title="Ship",
        description=desc,
        color=color_purple
    )
    return embed

@bot.command(name="ship")
async def ctx_ship(ctx, name1:str, name2:str=None):
    try:
        namebackup = name1
        name1 = await StrToMember(name1)
        if name1 == "Invalid member.":
            name1 = namebackup
        else:
            name1 = name1.name
    except:
        print("Error modifying name1 in ctx_ship")
        return
    if name2 == None:
        print("")
        try:
            name2 = name1
            name1 = ctx.author.name
        except:
            print("Error modifying name1 and name2 due to name2 being None")
            return
    else:
        namebackup = name2
        name2 = await StrToMember(name2)
        if name2 == "Invalid member.":
            name2 = namebackup
        else:
            name2 = name2.name
    dataname = "kittyships.json"
    if not utils.path_exists(dataname):
        WriteJson({}, dataname)
    data = ReadJson(dataname)
    current_ship = f"{name1} - {name2}"
    data.setdefault(current_ship, random.randint(0, 100))
    WriteJson(data, dataname)
    await ctx.send(embed=await ShipEmbed(name1, name2))

@bot.tree.command(name="ship", description="Ship two members")
async def command_ship(interaction:discord.Interaction, member1:str, member2:str=None):
    try:
        namebackup = member1
        member1 = await StrToMember(member1)
        if member1 == "Invalid member.":
            member1 = namebackup
        else:
            member1 = member1.name
    except:
        print("Error modifying member1 in command_ship")
        return
    if member2 == None:
        try:
            member2 = member1
            member1 = interaction.user.name
        except:
            print("Error modifying member1 and member2 due to member2 being None")
            return
    else:
        namebackup = member2
        member2 = await StrToMember(member2)
        if member2 == "Invalid member.":
            member2 = namebackup
        else:
            member2 = member2.name
    dataname = "kittyships.json"
    if not utils.path_exists(dataname):
        WriteJson({}, dataname)
    data = ReadJson(dataname)
    current_ship = f"{member1} - {member2}"
    data.setdefault(current_ship, random.randint(0, 100))
    WriteJson(data, dataname)
    await interaction.response.send_message(embed=await ShipEmbed(member1, member2))


async def FriendEmbed(member1:str, member2:str):
    data = ReadJson("kittyfriends.json")
    current = data[f"{member1} - {member2}"]
    desc = "**Hmmm, I wonder if we have new best friends here?**\n"
    AI_Request = await AskAI(f"Generate a ship name with the 2 names that I give you. If they were like 'Mark' and 'Dog' it'd be something like 'Maog'. They can also not be actual names, but letters or other words (example: if it was 's' and 'z', it would be 'sz'). Reply with only the ship name, case sensitive to the names. '{member1}' and '{member2}'")
    desc += f"`{member1}` + `{member2}` = ✨ `{AI_Request}` ✨\n"
    quote = ""
    desc += quote
    percent = f"**{current}%**"
    desc += percent
    embed = discord.Embed(
        title="Friendship",
        description=desc,
        color=color_purple
    )
    return embed

@bot.command(name="friendship")
async def ctx_friend(ctx, name1:str, name2:str=None):
    try:
        namebackup = name1
        name1 = await StrToMember(name1)
        if name1 == "Invalid member.":
            name1 = namebackup
        else:
            name1 = name1.name
    except:
        print("Error modifying name1 in ctx_friend")
        return
    if name2 == None:
        print("")
        try:
            name2 = name1
            name1 = ctx.author.name
        except:
            print("Error modifying name1 and name2 due to name2 being None")
            return
    else:
        namebackup = name2
        name2 = await StrToMember(name2)
        if name2 == "Invalid member.":
            name2 = namebackup
        else:
            name2 = name2.name
    dataname = "kittyfriends.json"
    if not utils.path_exists(dataname):
        WriteJson({}, dataname)
    data = ReadJson(dataname)
    current_friend = f"{name1} - {name2}"
    data.setdefault(current_friend, random.randint(0, 100))
    WriteJson(data, dataname)
    await ctx.send(embed=await FriendEmbed(name1, name2))

@bot.tree.command(name="friendship", description="Check two members' friendship level")
async def command_friend(interaction:discord.Interaction, member1:str, member2:str=None):
    try:
        namebackup = member1
        member1 = await StrToMember(member1)
        if member1 == "Invalid member.":
            member1 = namebackup
        else:
            member1 = member1.name
    except:
        print("Error modifying member1 in command_friend")
        return
    if member2 == None:
        try:
            member2 = member1
            member1 = interaction.user.name
        except:
            print("Error modifying member1 and member2 due to member2 being None")
            return
    else:
        namebackup = member2
        member2 = await StrToMember(member2)
        if member2 == "Invalid member.":
            member2 = namebackup
        else:
            member2 = member2.name
    dataname = "kittyfriends.json"
    if not utils.path_exists(dataname):
        WriteJson({}, dataname)
    data = ReadJson(dataname)
    current_friend = f"{member1} - {member2}"
    data.setdefault(current_friend, random.randint(0, 100))
    WriteJson(data, dataname)
    await interaction.response.send_message(embed=await FriendEmbed(member1, member2))

async def StrToMember(string: str):
    guild_id = 1315433980258029588
    guild = bot.get_guild(guild_id)

    if not guild:
        return "Invalid member."

    print(f"Input string: {string}")

    if string.startswith("<@") and string.endswith(">"):
        try:
            member_id = string.replace("<@", "").replace(">", "").replace("!", "")
            member_id = int(member_id)
            member = await guild.fetch_member(member_id)
            return member
        except Exception as e:
            return "Invalid member."

    string = string.lower()

    for member in guild.members:
        if member.name.lower().startswith(string) or (member.nick and member.nick.lower().startswith(string)):
            return member

    return "Invalid member."