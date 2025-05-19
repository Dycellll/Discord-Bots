import discord, secret
from discord.ext import commands

token = secret.MODTOKEN

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="O.", intents=intents)


async def SetPresence():
    await discord.Client.change_presence(
        status=discord.Status.idle,    activity=discord.Activity(
    type=discord.ActivityType.playing, name="Obscura Mod"
            ), self=bot
        )


@bot.event
async def on_ready(): 
    await SetPresence()
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    await bot.tree.sync()


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    print(f"{message.author.name} said: '{message.content}'")


@bot.event
async def on_member_join(member):
    print(f"{member.display_name} has joined the server.")
    dycel = await bot.fetch_user(1099017318232764447)
    channel_id = 1255833508115644438
    channel = await bot.fetch_channel(channel_id)
    if channel:
        await channel.send(f"Welcome to the server, {member.mention}!\n\nGet roles in the roles channel, and uh {dycel.mention} will give u the mod musician role if u are one.")
    else:
        print(f"Channel with ID {channel_id} not found.")