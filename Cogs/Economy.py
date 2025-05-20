import discord, os, json, random, time, utils
from discord.ext import commands

class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.color_purple = discord.Color.from_str("#8a31de")
        self.beg_cooldowns = {}
        self.beg_cooldown_time = 30

    def read_json(self, file='kittydatabase.json'):
        file_path = os.path.join('Databases', file)
        if not os.path.exists(file_path):
            self.write_json({}, file)
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            return json.load(jsonfile)

    def write_json(self, data, file='kittydatabase.json', indent=4):
        file_path = os.path.join('Databases', file)
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=indent)

    def make_balance_embed(self, member: discord.Member):
        try:
            data = self.read_json()
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
            color=self.color_purple
        )
        embed.add_field(name="💵 Wallet", value=f"{wallet}", inline=True)
        embed.add_field(name="🏦 Bank", value=f"{bank}", inline=True)
        embed.set_footer(text=member.name, icon_url=member.avatar.url)
        return embed

    @commands.hybrid_command(name="balance", aliases=['bal'], description="Get a member's balance")
    async def balance(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        if member.bot:
            await ctx.send("You can't get a bot's balance!", ephemeral=True)
            return
        await ctx.send(embed=self.make_balance_embed(member))

    async def do_deposit(self, user: discord.Member, amount):
        data = self.read_json()
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
        self.write_json(data)
        embed.set_footer(text=user.name, icon_url=user.avatar.url)
        return embed

    @commands.hybrid_command(name="deposit", aliases=["dep"], description="Deposit money to your bank")
    async def deposit(self, ctx: commands.Context, amount: str):
        await ctx.send(embed=await self.do_deposit(ctx.author, utils.StrToInt(amount)))

    async def do_withdraw(self, user: discord.Member, amount):
        data = self.read_json()
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
        self.write_json(data)
        embed.set_footer(text=user.name, icon_url=user.avatar.url)
        return embed

    @commands.hybrid_command(name="withdraw", aliases=["with", "wd"], description="Withdraw money to your wallet")
    async def withdraw(self, ctx: commands.Context, amount: str):
        await ctx.send(embed=await self.do_withdraw(ctx.author, utils.StrToInt(amount)))

    def run_beg(self, member: discord.Member):
        current_time = time.time()

        if member.id in self.beg_cooldowns:
            time_left = self.beg_cooldowns[member.id] - current_time
            if time_left > 0:
                embed = discord.Embed(
                    title="Cooldown",
                    description=f"Wait {int(time_left)} seconds before begging again.",
                    color=self.color_purple
                )
                embed.set_footer(text=member.name, icon_url=member.avatar.url)
                return embed

        data = self.read_json()
        dialData = self.read_json("kittydialogue.json")
        beg_dial = dialData["dialogue"]["beg"]
        member_data = data["guilds"][str(member.guild.id)]["members"].get(str(member.id), {})
        wallet = member_data.get("balance", {}).get("wallet", 0)

        descr = ""
        color = discord.Color.red()
        GainLog = "lost **"
        
        rand = random.randint(1, 10)
        if rand == 5:
            descr = random.choice(beg_dial["fail"])
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
        self.write_json(data)
        self.beg_cooldowns[member.id] = current_time + self.beg_cooldown_time
        
        return embed

    @commands.hybrid_command(name="beg", description="Beg for money")
    async def beg(self, ctx: commands.Context):
        await ctx.send(embed=self.run_beg(ctx.author))

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
            self.data = self.read_json()
            self.wallet = self.data["guilds"][str(self.user.guild.id)]["members"][str(self.user.id)]["balance"]["wallet"]
            player_score = self.get_score(True)
            dealer_score = self.get_score(False)

            embed = discord.Embed(title="Blackjack Game", color=discord.Color.green())
            embed.add_field(name=f"Your Score: {player_score}", value=f"Cards: {len(self.player_card)}", inline=False)
            embed.add_field(name=f"Dealer's Score: {dealer_score}", value=f"Cards: {len(self.dealer_card)}", inline=False)
            embed.add_field(name="Your Bet", value=f"{self.bet_amount} coins", inline=False)

            if self.game_over:
                if self.player_busted:
                    embed.add_field(name="Result", value=f"You busted! Lost {self.bet_amount} coins.", inline=False)
                    embed.color = discord.Color.red()
                    self.wallet -= self.bet_amount
                elif self.dealer_busted:
                    embed.add_field(name="Result", value=f"Dealer busted! Won {self.bet_amount} coins!", inline=False)
                    self.wallet += self.bet_amount
                else:
                    if player_score > dealer_score:
                        embed.add_field(name="Result", value=f"You win! Won {self.bet_amount} coins!", inline=False)
                        self.wallet += self.bet_amount
                    elif player_score < dealer_score:
                        embed.add_field(name="Result", value=f"Dealer wins! Lost {self.bet_amount} coins.", inline=False)
                        embed.color = discord.Color.red()
                        self.wallet -= self.bet_amount
                    else:
                        embed.add_field(name="Result", value="It's a tie! Bet returned.", inline=False)

                self.data["guilds"][str(self.user.guild.id)]["members"][str(self.user.id)]["balance"]["wallet"] = self.wallet
                self.write_json(self.data)
                self.remove_buttons = True

            if self.remove_buttons:
                self.clear_items()

            await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
        async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user != self.user:
                await interaction.response.send_message("This isn't your game!", ephemeral=True)
                return
            if self.game_over:
                await interaction.response.send_message("Game over!", ephemeral=True)
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
                await interaction.response.send_message("This isn't your game!", ephemeral=True)
                return
            if self.game_over:
                await interaction.response.send_message("Game over!", ephemeral=True)
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
                await interaction.response.send_message("This isn't your game!", ephemeral=True)
                return
            if self.game_over:
                await interaction.response.send_message("Game over!", ephemeral=True)
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

    def blackjack(self, member: discord.Member, bet_amount):
        card_categories = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        cards_list = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
        deck = [(card, category) for category in card_categories for card in cards_list]
        random.shuffle(deck)

        player_card = [deck.pop(), deck.pop()]
        dealer_card = [deck.pop(), deck.pop()]

        data = self.read_json()
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

        view = self.BlackJackView(member, player_card, dealer_card, deck, bet_amount, data)
        return view

    @commands.hybrid_command(name="blackjack", aliases=["bj"], description="Play blackjack")
    async def blackjack_cmd(self, ctx: commands.Context, amount: str):
        view = self.blackjack(ctx.author, utils.StrToInt(amount))
        if not view:
            await ctx.send("Invalid bet amount!", ephemeral=True)
            return

        embed = discord.Embed(title="Blackjack", color=discord.Color.green())
        embed.add_field(name=f"Your Score: {view.get_score(True)}", value=f"Cards: {len(view.player_card)}", inline=False)
        embed.add_field(name=f"Dealer's Score: {view.get_score(False)}", value=f"Cards: {len(view.dealer_card)}", inline=False)
        embed.add_field(name="Your Bet", value=f"{view.bet_amount} coins", inline=False)
        await ctx.send(embed=embed, view=view)

    def dick_fight(self, member: discord.Member, bet_amount):
        embed = discord.Embed(title="Dick Fight", color=self.color_purple)
        data = self.read_json()
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
            embed.description = f"Your lil dick won! Gained {bet_amount} coins! 🐈\nDick strength: {df}%"
            wallet += bet_amount
        else:
            embed.color = discord.Color.red()
            embed.description = f"Your lil dick lost! Lost {bet_amount} coins! 🐈\nDick strength: {df}%"
            wallet -= bet_amount
        
        embed.set_footer(text=member.name, icon_url=member.avatar.url)
        player_data["balance"]["wallet"] = wallet
        player_data["df"] = df
        data["guilds"][str(member.guild.id)]["members"][str(member.id)] = player_data
        self.write_json(data)
        return embed

    @commands.hybrid_command(name="dickfight", aliases=["df"], description="Fight with your dick")
    async def dickfight(self, ctx: commands.Context, amount: str):
        embed = self.dick_fight(ctx.author, utils.StrToInt(amount))
        await ctx.send(embed=embed)

    async def leaderboard(self, guild, user=None):
        data = self.read_json()
        member_balances = []
        
        for member_id, member_data in data["guilds"][str(guild.id)]["members"].items():
            wallet = member_data["balance"]["wallet"]
            bank = member_data["balance"]["bank"]
            total = wallet + bank
            member_balances.append((member_id, total))

        member_balances.sort(key=lambda x: x[1], reverse=True)
        top_10 = member_balances[:10]

        embed = discord.Embed(title="Top 10 Richest", color=self.color_purple)
        runner_found = False
        
        for rank, (member_id, total) in enumerate(top_10, start=1):
            member = await self.bot.fetch_user(member_id)
            if member.id == user.id:
                runner_found = True
                embed.description += f"**{rank}.** **{member.name}** • {total} coins\n"
            else:
                embed.description += f"{rank}. {member.name} • {total} coins\n"

        if user and not runner_found:
            runner_id = str(user.id)
            runner_total = next((total for mid, total in member_balances if mid == runner_id), 0)
            runner_rank = len([x for x in member_balances if x[1] > runner_total]) + 1
            embed.description += f"\n**{runner_rank}.** **{user.name}** • {runner_total} coins"
        
        return embed

    @commands.hybrid_command(name="leaderboard", aliases=["lb"], description="Show wealth leaderboard")
    async def leaderboard_cmd(self, ctx: commands.Context):
        embed = await self.leaderboard(ctx.guild, ctx.author)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))