import discord, os, json, random, time, utils

default_file:str
guild:discord.Guild
bot:discord.Client
color_purple = discord.Color.from_str("#8a31de")

async def setup(_bot, guild_id, database):
    global guild, default_file, bot
    bot = _bot
    guild = bot.get_guild(guild_id)
    default_file = database

def ReadJson(file=default_file):
    file_path = os.path.join('Databases', file)
    if not os.path.exists(file_path):
        WriteJson({}, file)
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)

def WriteJson(data, file=default_file, indent=4):
    file_path = os.path.join('Databases', file)
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=indent)

def MakeBalanceEmbed(member: discord.Member):
    try:
        data = ReadJson()
        member_data = data["guilds"][str(member.guild.id)]["members"].get(str(member.id), {})
        balance = member_data.get("balance", {})
        wallet = balance.get("wallet", 0)
        bank = balance.get("bank", 0)
    except Exception as e:
        print(f"Error in MakeBalanceEmbed: {e}")
        wallet = 0
        bank = 0

    embed = discord.Embed(
        title="Balance",
        description=f"**Balance for {member.mention}**",
        color=color_purple
    )
    embed.add_field(
        name="💵 Wallet",
        value=(
            f"{wallet}\n"
        ),
        inline=True
    )
    embed.add_field(
        name="🏦 Bank",
        value=(
            f"{bank}"
        ),
        inline=True
    )
    embed.set_footer(text=member.name, icon_url=member.avatar.url)
    return embed

@bot.command(aliases=['bal', 'balance'])
async def ctx_balance(ctx, member:str=None):
    if member == None:
        member = ctx.author
    else:
        member = await utils.StrToMember(member, guild)
        if isinstance(member, str):
            await ctx.send(member)
            return
    if member.bot:
        await ctx.send("You can't get a bot's balance!")
        return
    embed = MakeBalanceEmbed(member)
    await ctx.send(embed=embed)

@bot.tree.command(name="balance", description="Get a member's balance")
async def command_balance(interaction:discord.Interaction, member:discord.Member=None):
    if member == None:
        member = interaction.user
    if member.bot:
        await interaction.response.send_message("You can't get a bot's balance!", ephemeral=True)
        return
    embed = MakeBalanceEmbed(member)
    await interaction.response.send_message(embed=embed)


async def DoDeposit(user:discord.Member, amount):
    data = ReadJson()
    member_data = data["guilds"][str(user.guild.id)]["members"].get(str(user.id), {})
    balance = member_data.get("balance", {})
    wallet = balance.get("wallet", 0)
    bank = balance.get("bank", 0)
    if isinstance(amount, str):
        if amount == "all":
            amount = wallet
        elif amount == "error":
            print("Error in DoDeposit()")
            return None
        elif amount.endswith("%"):
            amount = int(utils.GetPercent(wallet, float(amount.replace("%", ""))))
    else:
        amount = int(amount)
    embed = discord.Embed(
        title="Deposit",
        description=f"Successfully deposited {amount} to {user.mention}'s bank.",
        color=discord.Color.green()
    )
    if wallet >= amount:
        wallet -= amount
        bank += amount
    else:
        embed.description=f"You don't have enough money in your wallet to deposit {amount}."
        embed.color=discord.Color.red()
    data["guilds"][str(user.guild.id)]["members"][str(user.id)]["balance"]["wallet"] = wallet
    data["guilds"][str(user.guild.id)]["members"][str(user.id)]["balance"]["bank"] = bank
    WriteJson(data)
    embed.set_footer(text=user.name, icon_url=user.avatar.url)
    return embed


@bot.command(aliases=["deposit", "dep"])
async def ctx_deposit(ctx, amount:str):
    await ctx.send(embed=await DoDeposit(ctx.author, utils.StrToInt(amount)))

@bot.tree.command(name="deposit", description="Deposit money to your bank")
async def command_deposit(interaction:discord.Interaction, amount:str):
    await interaction.response.send_message(embed=await DoDeposit(interaction.user, utils.StrToInt(amount)))


async def DoWithdraw(user:discord.Member, amount):
    data = ReadJson()
    member_data = data["guilds"][str(user.guild.id)]["members"].get(str(user.id), {})
    balance = member_data.get("balance", {})
    wallet = balance.get("wallet", 0)
    bank = balance.get("bank", 0)
    
    if isinstance(amount, str):
        if amount == "all":
            amount = bank
        elif amount == "error":
            print("Error in DoWithdraw()")
            return None
        elif amount.endswith("%"):
            amount = int(utils.GetPercent(bank, float(amount.replace("%", ""))))
    else:
        amount = int(amount)
    embed = discord.Embed(
        title="Withdraw",
        description=f"Successfully withdrawn {amount} to {user.mention}'s wallet.",
        color=discord.Color.green()
    )
    if bank >= amount:
        wallet += amount
        bank -= amount
    else:
        embed.description=f"You don't have enough money in your bank to withdraw {amount}."
        embed.color=discord.Color.red()
    data["guilds"][str(user.guild.id)]["members"][str(user.id)]["balance"]["wallet"] = wallet
    data["guilds"][str(user.guild.id)]["members"][str(user.id)]["balance"]["bank"] = bank
    WriteJson(data)
    embed.set_footer(text=user.name, icon_url=user.avatar.url)
    return embed 


@bot.command(aliases=["withdraw", "with", "wd"])
async def ctx_withdraw(ctx, amount:str):
    await ctx.send(embed=await DoWithdraw(ctx.author, utils.StrToInt(amount)))

@bot.tree.command(name="withdraw", description="Withdraw money to your wallet")
async def command_withdraw(interaction:discord.Interaction, amount:str):
    await interaction.response.send_message(embed=await DoWithdraw(interaction.user, utils.StrToInt(amount)))


beg_cooldowns = {}
beg_cooldown_time = 30

def RunBeg(member: discord.Member):
    current_time = time.time()

    if member.id in beg_cooldowns:
        time_left = beg_cooldowns[member.id] - current_time
        if time_left > 0:
            embed = discord.Embed(
                title="Cooldown",
                description=f"You are on cooldown. Please wait **{int(time_left)} seconds** before using the command again.",
                color=color_purple
            )
            embed.set_footer(text=member.name, icon_url=member.avatar.url)
            return embed
    
    data = ReadJson()
    dialData = ReadJson("kittydialogue.json")
    beg_dial = dialData["dialogue"]["beg"]
    member_data = data["guilds"][str(member.guild.id)]["members"].get(str(member.id), {})
    wallet = member_data.get("balance", {}).get("wallet", 0)

    descr = ""
    color:discord.Color

    rand = random.randint(1, 10)
    if rand == 5:
        descr = random.choice(beg_dial["fail"])
        color = discord.Color.red()
        GainLog = "lost **"
        try:
            decrement = int(wallet / 2)
        except:
            decrement = 0
        GainLog += str(decrement)
        GainLog += " coins**."
        wallet -= decrement
    else:
        descr = random.choice(beg_dial["success"])
        color = discord.Color.green()
        GainLog = "gained **"
        increment = random.randint(100, 500)
        GainLog += str(increment)
        GainLog += " coins**."
        wallet += increment

    embed = discord.Embed(
        title="Beg",
        description=f"{descr} You {GainLog}",
        color=color
    )
    embed.set_footer(text=member.name, icon_url=member.avatar.url)
    
    data["guilds"][str(member.guild.id)]["members"][str(member.id)]["balance"]["wallet"] = wallet
    WriteJson(data)
    
    beg_cooldowns[member.id] = current_time + beg_cooldown_time
    
    return embed

@bot.command(name="beg")
async def ctx_beg(ctx):
    await ctx.send(embed=RunBeg(ctx.author))

@bot.tree.command(name="beg", description="Beg for money")
async def command_beg(interaction:discord.Interaction):
    await interaction.response.send_message(embed=RunBeg(interaction.user))


class BlackJackView(discord.ui.View):
    def __init__(self, user, player_card, dealer_card, deck, bet_amount, data):
        super().__init__(timeout=60)
        self.user = user
        self.player_card = player_card
        self.dealer_card = dealer_card
        self.deck = deck
        self.player_busted = False
        self.dealer_busted = False
        self.game_over = False
        self.bet_amount = bet_amount
        self.data = data
        self.wallet = data["guilds"][str(user.guild.id)]["members"][str(user.id)]["balance"]["wallet"]
        self.remove_buttons = False

        for button in self.children:
            if isinstance(button, discord.ui.Button) and button.label == "Double Down" and self.wallet < self.bet_amount * 2:
                button.disabled = True

    def card_value(self, card): 
        if card[0] in ['Jack', 'Queen', 'King']: 
            return 10
        elif card[0] == 'Ace': 
            return 11
        else: 
            return int(card[0]) 

    def get_score(self, player=True):
        cards = self.player_card if player else self.dealer_card
        score = sum(self.card_value(card) for card in cards)
        ace_count = sum(1 for card in cards if card[0] == 'Ace')
        while score > 21 and ace_count:
            score -= 10
            ace_count -= 1
        return score

    async def update_embed(self, interaction):
        self.data = ReadJson()
        self.wallet = self.data["members"][str(self.user.id)]["balance"]["wallet"]
        player_score = self.get_score(True)
        dealer_score = self.get_score(False)

        embed = discord.Embed(title="Blackjack Game", color=discord.Color.green())
        
        embed.add_field(name=f"Your Score: {player_score}", value=f"Cards: **{len(self.player_card)}**", inline=False)
        embed.add_field(name=f"Dealer's Score: {dealer_score}", value=f"Cards: **{len(self.dealer_card)}**", inline=False)
        
        embed.add_field(name="Your Bet", value=f"{self.bet_amount} coins", inline=False)
        
        if self.game_over:
            if self.player_busted:
                embed.add_field(name="Result", value=f"You busted! Dealer wins! You lose **{self.bet_amount} coins**.", inline=False)
                embed.color = discord.Color.red()
                self.wallet -= self.bet_amount
            elif self.dealer_busted:
                embed.add_field(name="Result", value=f"Dealer busted! You win! You gain **{self.bet_amount} coins**.", inline=False)
                self.wallet += self.bet_amount
            else:
                if player_score > dealer_score:
                    embed.add_field(name="Result", value=f"You win! You win **{self.bet_amount} coins**.", inline=False)
                    self.wallet += self.bet_amount
                elif player_score < dealer_score:
                    embed.add_field(name="Result", value=f"Dealer wins! You lose **{self.bet_amount} coins**.", inline=False)
                    embed.color = discord.Color.red()
                    self.wallet -= self.bet_amount
                else:
                    embed.add_field(name="Result", value="It's a tie! Your bet is returned.", inline=False)

            self.data["guilds"][str(self.user.guild.id)]["members"][str(self.user.id)]["balance"]["wallet"] = self.wallet
            WriteJson(self.data)
            
            self.remove_buttons = True

        for button in self.children:
            if isinstance(button, discord.ui.Button) and button.label == "Double Down":
                if not self.wallet < self.bet_amount * 2:
                    button.disabled = False
                else:
                    button.disabled = True

        if self.remove_buttons:
            self.clear_items()

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("This isn't your instance of the game!", ephemeral=True)
            return
        if self.game_over:
            await interaction.response.send_message("The game is over.", ephemeral=True)
            return
        
        new_card = self.deck.pop()
        self.player_card.append(new_card)

        player_score = self.get_score(True)
        if player_score > 21:
            self.player_busted = True
            self.game_over = True

        await self.update_embed(interaction)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.success)
    async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("This isn't your instance of the game!", ephemeral=True)
            return
        if self.game_over:
            await interaction.response.send_message("The game is over.", ephemeral=True)
            return
        
        dealer_score = self.get_score(False)
        while dealer_score < 17:
            self.dealer_card.append(self.deck.pop())
            dealer_score = self.get_score(False)

        if dealer_score > 21:
            self.dealer_busted = True

        self.game_over = True
        await self.update_embed(interaction)

    @discord.ui.button(label="Double Down", style=discord.ButtonStyle.gray)
    async def double_down_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("This isn't your instance of the game!", ephemeral=True)
            return
        if self.game_over:
            await interaction.response.send_message("The game is over.", ephemeral=True)
            return
        
        new_card = self.deck.pop()
        self.player_card.append(new_card)
        if self.wallet >= self.bet_amount * 2:
            self.bet_amount *= 2
        player_score = self.get_score(True)
        if player_score > 21:
            self.player_busted = True
            self.game_over = True

        await self.update_embed(interaction)



def BlackJack(member: discord.Member, bet_amount):
    card_categories = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    cards_list = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
    deck = [(card, category) for category in card_categories for card in cards_list]
    random.shuffle(deck)

    player_card = [deck.pop(), deck.pop()]
    dealer_card = [deck.pop(), deck.pop()]

    data = ReadJson()
    player_data = data["guilds"][str(member.guild.id)]["members"][str(member.id)]
    wallet = player_data["balance"]["wallet"]

    if isinstance(bet_amount, str):
        if bet_amount == "all":
            bet_amount = wallet
        elif bet_amount == "error":
            return None
        elif bet_amount.endswith("%"):
            bet_amount = int(utils.GetPercent(wallet, float(bet_amount.replace("%", ""))))
    else:
        if int(bet_amount) > wallet:
            return None
        bet_amount = int(bet_amount)

    view = BlackJackView(member, player_card, dealer_card, deck, bet_amount, data)
    
    return view




@bot.command(aliases=["bj", "blackjack", "blackj", "bjack"])
async def ctx_blackjack(ctx, amount: str):
    view = BlackJack(ctx.author, utils.StrToInt(amount))
    if not view:
        await ctx.send("Invalid bet amount!")
        return

    embed = discord.Embed(title="Blackjack Game", color=discord.Color.green())
    embed.add_field(name=f"Your Score: {view.get_score(True)}", value=f"Cards: **{len(view.player_card)}**", inline=False)
    embed.add_field(name=f"Dealer's Score: {view.get_score(False)}", value=f"Cards: **{len(view.dealer_card)}**", inline=False)
    embed.add_field(name="Your bet", value=f"{view.bet_amount} coins", inline=False)

    await ctx.send(embed=embed, view=view)

@bot.tree.command(name="blackjack", description="Start a game of Blackjack")
async def command_blackjack(interaction: discord.Interaction, amount: str):
    view = BlackJack(interaction.user, utils.StrToInt(amount))
    if not view:
        await interaction.response.send_message("Invalid bet amount!", ephemeral=True)
        return

    embed = discord.Embed(title="Blackjack Game", color=discord.Color.green())
    embed.add_field(name=f"Your Score: {view.get_score(True)}", value=f"Cards: **{len(view.player_card)}**", inline=False)
    embed.add_field(name=f"Dealer's Score: {view.get_score(False)}", value=f"Cards: **{len(view.dealer_card)}**", inline=False)
    embed.add_field(name="Your bet", value=f"{view.bet_amount} coins", inline=False)

    await interaction.response.send_message(embed=embed, view=view)

def DickFight(member: discord.Member, bet_amount):
    embed = discord.Embed(
        title="Dick Fight",
        description="",
        color=color_purple
    )
    data = ReadJson()
    won = False
    player_data = data["guilds"][str(member.guild.id)]["members"][str(member.id)]
    df = player_data.setdefault("df", 50)
    wallet = player_data["balance"]["wallet"]
    if random.randint(1, 100) >= df:
        won = True
        if df < 85:
            df += 1
    else:
        df = 50
    
    if isinstance(bet_amount, str):
        if bet_amount == "all":
            bet_amount = wallet
        elif bet_amount == "error":
            return None
        elif bet_amount.endswith("%"):
            bet_amount = int(utils.GetPercent(wallet, float(bet_amount.replace("%", ""))))
    else:
        if int(bet_amount) > wallet:
            return None
        bet_amount = int(bet_amount)

    if won:
        embed.color = discord.Color.green()
        embed.description = f"Your lil dick won the fight, and made you **{bet_amount} coins** richer! 🐈\nDick strength (chance of winning): {df}%\n-# Hint: 'Dick' is a very common pet name"
        wallet += bet_amount
    else:
        embed.color = discord.Color.red()
        embed.description = f"Your lil dick lost the fight... there are always bigger fishes in the sea. You lost **{bet_amount} coins**! 🐈\nDick strength (chance of winning): {df}%\n-# Hint: 'Dick' is a very common pet name"
        wallet -= bet_amount
    
    embed.set_footer(text=member.name, icon_url=member.avatar.url)
    player_data["balance"]["wallet"] = wallet
    player_data["df"] = df
    data["guilds"][str(member.guild.id)]["members"][str(member.id)] = player_data
    WriteJson(data)
    return embed


@bot.command(aliases=["df", "dickf", "dfight", "dickfight"])
async def ctx_df(ctx, amount:str):
    embed = DickFight(ctx.author, utils.StrToInt(amount))
    await ctx.send(embed=embed)

@bot.tree.command(name="dickfight", description="Make your dick fight against another dick")
async def command_df(interaction:discord.Interaction, amount:str):
    embed = DickFight(interaction.user, utils.StrToInt(amount))
    await interaction.response.send_message(embed=embed)

async def LeaderBoard(guild, user=None):
    data = ReadJson()
    member_balances = []
    
    for member_id, member_data in data["guilds"][str(guild.id)]["members"].items():
        wallet_balance = member_data["balance"]["wallet"]
        bank_balance = member_data["balance"]["bank"]
        total_balance = wallet_balance + bank_balance
        member_balances.append((member_id, total_balance))

    member_balances.sort(key=lambda x: x[1], reverse=True)
    
    top_10 = member_balances[:10]

    embed = discord.Embed(title="Top 10 Richest Users", description="", color=color_purple)
    runner_found = False
    for rank, (member_id, total_balance) in enumerate(top_10, start=1):
        topper = await bot.fetch_user(member_id)
        if topper.id == user.id:
            runner_found = True
            embed.description += f"**{rank}.** **{topper.name}** • {total_balance} coins\n"
        else:
            embed.description += f"**{rank}.** {topper.name} • {total_balance} coins\n"

    if user:
        runner_id = str(user.id)
        
        if not runner_found:
            runner_balance = next((total_balance for member_id, total_balance in member_balances if str(member_id) == runner_id), 0)
            runner_rank = len(member_balances) + 1
            embed.description += f"\n**{runner_rank}.** **{user.name}** • {runner_balance} coins"
    
    return embed


@bot.command(aliases=["lb", "leaderb", "lboard", "leaderboard"])
async def ctx_leaderboard(ctx):
    await ctx.send(embed=await LeaderBoard(ctx.guild, ctx.author))

@bot.tree.command(name="leaderboard", description="Get a leaderboard of the 10 richest members")
async def command_leaderboard(interaction: discord.Interaction):
    await interaction.response.send_message(embed=await LeaderBoard(interaction.guild, interaction.user))