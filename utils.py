import os

def path_exists(path:str) -> bool:
    """Check if a path exists in the Databases folder."""
    return os.path.exists(os.path.join('Databases', path))

async def StrToMember(string: str, guild):
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

def GetPercent(num, percent):
    perc = float(percent)
    n = float(num)
    return int((perc / 100) * n)

def StrToInt(string:str):
    string = string.lower()
    try:
        return int(string)
    except:
        if string == "all" or string == "max":
            return "all"
        elif string.endswith("%"):
            print("Found percent in StrToInt()")
            try:
                value = float(string.replace("%", ""))
                if value == 100:
                    return "all"
                elif value < 100:
                    if value == 0:
                        return 0
                    elif value > 0:
                        print(f"Returning {value}% from StrToInt()")
                        return f"{value}%"
                else:
                    return "all"
            except Exception as e:
                print(f"Error {e} in StrToInt()")
                return
        else:
            if string.endswith("k"):
                try:
                    return int(string.replace("k", "")) * 1000
                except:
                    return "error"
            elif string.endswith("m"):
                try: 
                    return int(string.replace("m", "")) * 1000000
                except:
                    return "error"
            else:
                return "error" 