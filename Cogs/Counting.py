import os, json
from sympy import sympify

def ReadJson(file):
    file_path = os.path.join('Databases', file)
    if not os.path.exists(file_path):
        WriteJson({}, file)
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)

def WriteJson(data, file, indent=4):
    file_path = os.path.join('Databases', file)
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=indent)

async def on_msg(message, counting_channel_id, database):
    data = ReadJson(database)
    guild_id = str(message.guild.id)
    
    if "bot" not in data["guilds"][guild_id]:
        data["guilds"][guild_id]["bot"] = {}
    bot_data = data["guilds"][guild_id]["bot"]
    
    bot_data.setdefault("Count", 0)
    bot_data.setdefault("Last_Counter", 0)

    if message.channel.id != counting_channel_id:
        return

    try:
        result = sympify(message.content)

        if not result.is_number:
            raise ValueError("Not a number")
        
        current_count = bot_data["Count"]
        expected_number = current_count + 1
        last_counter = bot_data["Last_Counter"]

        if message.author.id == last_counter:
            await message.add_reaction("❌")
            await message.channel.send(
                f"You can't count twice in a row! Game over at **{current_count}**!"
            )
            bot_data["Count"] = 0
            bot_data["Last_Counter"] = 0
            WriteJson(data, database)
            return
        
        if not result.is_integer:
            await message.add_reaction("❌")
            await message.channel.send(
                f"Wrong number! You can only count with integers! Game over at **{current_count}**!"
            )
            bot_data["Count"] = 0
            bot_data["Last_Counter"] = 0

        if int(result) == expected_number:
            bot_data["Count"] = expected_number
            bot_data["Last_Counter"] = message.author.id
            await message.add_reaction("✅")
        else:
            await message.add_reaction("❌")
            await message.channel.send(
                f"Wrong number! The correct number was: **{expected_number}**. Game over at **{current_count}**!"
            )
            bot_data["Count"] = 0
            bot_data["Last_Counter"] = 0

    except Exception as e:
        pass
    finally:
        data["guilds"][guild_id]["bot"] = bot_data
        WriteJson(data, database)