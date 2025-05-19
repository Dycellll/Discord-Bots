import Cogs.TicTacToe
import discord, secret, os, json, utils, random, datetime, Cogs.ReactionRoles, Cogs.Counting
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import get
from groq import Groq
from Cogs.AI_Commands import setup as setup_ai_commands
from Cogs.ReactionRoles import setup as setup_reaction_roles
from Cogs.BugReport import setup as setup_bug_report
from Cogs.SuggestionGive import setup as setup_suggestion_give
from Cogs.Music_Commands import setup as setup_music_commands
from Cogs.Strikes import setup as setup_strikes_commands
from sympy import sympify

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="N.", intents=intents)

main_guild_id = 1330268320502382724
counting_channel_id = 1355588226513113126

client = Groq(
    api_key=secret.GROQ_API_KEY,
)

def ReadJson(file='nerddatabase.json'):
    file_path = os.path.join('Databases', file)
    if not os.path.exists(file_path):
        WriteJson({}, file)
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)

def WriteJson(data, file='nerddatabase.json', indent=4):
    file_path = os.path.join('Databases', file)
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=indent)


async def DataGen():
    if not utils.path_exists("nerddatabase.json"):
        WriteJson({})
    
    data = ReadJson()
    for guild in bot.guilds:
        guild_id = str(guild.id)
        guild_data = data.setdefault("guilds", {}).setdefault(guild_id, {})
        memberdata = guild_data.setdefault("members", {})
        botdata = guild_data.setdefault("bot", {})
        delaysdata = botdata.setdefault("delays", {})
        rrdata = botdata.setdefault("rr_messages", {})
        
        for member in guild.members:
            if not member.bot:
                _ = guild_data["members"].setdefault(str(member.id), {})
    
    WriteJson(data)


async def SetPresence():
    await discord.Client.change_presence(
        status=discord.Status.idle,    activity=discord.Activity(
    type=discord.ActivityType.playing, name="VS Code"
            ), self=bot
        )

emoji_num1 = "<:Number1:1352729415918030919>"
emoji_num2 = "<:Number2:1352729427813077002>"
emoji_num3 = "<:Number3:1352729437396799508>"
emoji_num4 = "<:Number4:1352729451955490947>"
emoji_num5 = "<:Number5:1352729460222197850>"
emoji_num6 = "<:Number6:1352729470867476651>"
emoji_num7 = "<:Number7:1352729478287069225>"
emoji_num8 = "<:Number8:1352729485681889373>"
emoji_num9 = "<:Number9:1352729492027740220>"
emoji_num10 = "<:Number10:1352729499565035621>"
emoji_num11 = "<:Number11:1352743581294530764>"
emoji_num12 = "<:Number12:1352743589293064304>"
emoji_num13 = "<:Number13:1352743595928584285>"
emoji_num14 = "<:Number14:1352743603180408905>"
emoji_num15 = "<:Number15:1352743609270534349>"

emojisList = [emoji_num1, emoji_num2, emoji_num3, emoji_num4, emoji_num5, emoji_num6, emoji_num7, emoji_num8, emoji_num9, emoji_num10, emoji_num11, emoji_num12, emoji_num13, emoji_num14, emoji_num15]

async def add_cogs():
    await setup_ai_commands(bot, client)
    await setup_reaction_roles(bot, "nerddatabase.json", emojisList, ["rr"])
    await setup_bug_report(bot)
    await setup_suggestion_give(bot)
    await setup_music_commands(bot)
    await setup_strikes_commands(bot, main_guild_id, 1330288206951878860, 1330288308617613383, 1330288410904100967)
    bot.tree.add_command(Cogs.TicTacToe.Games())

@bot.event
async def on_ready(): 
    await DataGen()
    await SetPresence()
    await add_cogs()
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    await bot.tree.sync()
    #CheckDeadChat.start()

#@tasks.loop(minutes=60)
async def CheckDeadChat():
    for guild in bot.guilds:
        if guild.id == main_guild_id:
            data = ReadJson()

            if "delays" not in data["guilds"][str(guild.id)]["bot"]:
                data["guilds"][str(guild.id)]["bot"]["delays"] = {}

            delays = data["guilds"][str(guild.id)]["bot"]["delays"]
            delays.setdefault("deadchat", 32)
            delays.setdefault("last_deadchat", f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            last_deadchat = datetime.datetime.strptime(delays["last_deadchat"], '%Y-%m-%d %H:%M:%S')
            now = datetime.datetime.now()
            diff = now - last_deadchat
            
            if diff.total_seconds() >= delays["deadchat"] * 60 * 60:
                delays["last_deadchat"] = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                await PingDeadChat()

            WriteJson(data)

async def PingDeadChat():
    for guild in bot.guilds:
        if guild.id == main_guild_id:
            channel:discord.Channel = guild.get_channel(1330268321366413440)
            role:discord.Role = guild.get_role(1352752930859515988)
            data = ReadJson()
            if not "deadchat_messages" in data["guilds"][str(guild.id)]["bot"]:
                data["guilds"][str(guild.id)]["bot"]["deadchat_messages"] = []
            messages = data["guilds"][str(guild.id)]["bot"]["deadchat_messages"]
            if len(messages) > 0:
                msg = random.choice(messages).replace("{role}", role.mention)
                await channel.send(msg)
            else:
                await channel.send(f"{role.mention} hi! How are you doing?")
            WriteJson(data)

@bot.event
async def on_raw_reaction_add(payload):
    data = ReadJson()
    await Cogs.ReactionRoles.on_rr_add(bot, data, payload)

@bot.event
async def on_raw_reaction_remove(payload):
    data = ReadJson()
    await Cogs.ReactionRoles.on_rr_remove(bot, data, payload)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await Cogs.Counting.on_msg(message, counting_channel_id, "nerddatabase.json")