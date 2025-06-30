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

async def SetPresence():
    await discord.Client.change_presence(
        status=discord.Status.idle,    activity=discord.Activity(
    type=discord.ActivityType.playing, name="Bot stuff"
            ), self=bot
        )


@bot.event
async def on_ready():
    try:
        await SetPresence()
        await bot.tree.sync()

        print(f'Logged in as {bot.user.name} - {bot.user.id}')

    except Exception as e:
        print(f"An error occurred in on_ready: {e}")
        traceback.print_exc()


@bot.command(name="find_id")
async def find_id(ctx, id):
    user = await bot.fetch_user(int(id))
    if user is None:
        print(f"User with ID {id} not found.")
        return None
    await ctx.channel.send(f"ID {id} belongs to {user.name} aka {user.display_name} mentioned as {user.mention}.")