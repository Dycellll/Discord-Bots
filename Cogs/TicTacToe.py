import discord
from discord import app_commands, Embed
from discord.ui import Button, View
from typing import Optional

class TicTacToeButton(Button):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y
    
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToeView = self.view
        
        if view.board[self.y][self.x] != 0:
            return await interaction.response.defer()
        if view.current_player != interaction.user:
            return await interaction.response.send_message("It's not your turn!", ephemeral=True)
        
        view.board[self.y][self.x] = view.current_player_id
        self.style = discord.ButtonStyle.success if view.current_player_id == 1 else discord.ButtonStyle.danger
        self.label = "X" if view.current_player_id == 1 else "O"
        self.disabled = True
        
        winner = view.check_winner()
        embed = view.create_embed()
        
        if winner is not None:
            if winner == 0:
                embed.description = "**Game Over!** It's a tie!"
            else:
                winner_name = view.player1.display_name if winner == 1 else view.player2.display_name
                embed.description = f"**Game Over!** {winner_name} wins!"
            
            for child in view.children:
                child.disabled = True
            view.stop()
            return await interaction.response.edit_message(embed=embed, view=view)
        
        view.current_player = view.player2 if view.current_player_id == 1 else view.player1
        view.current_player_id = 2 if view.current_player_id == 1 else 1
        
        embed.description = f"{view.current_player.mention}'s turn ({'X' if view.current_player_id == 1 else 'O'})"
        await interaction.response.edit_message(embed=embed, view=view)

class TicTacToeView(View):
    def __init__(self, player1: discord.Member, player2: discord.Member):
        super().__init__(timeout=180)
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.current_player_id = 1
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))
    
    def create_embed(self) -> Embed:
        embed = Embed(
            title="🎮 Tic-Tac-Toe",
            color=discord.Color.purple(),
            description=f"{self.current_player.mention}'s turn ({'X' if self.current_player_id == 1 else 'O'})"
        )
        embed.add_field(
            name="Players",
            value=f"❌ {self.player1.mention}\n⭕ {self.player2.mention}",
            inline=False
        )
        return embed
    
    def check_winner(self) -> Optional[int]:
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] != 0:
                return row[0]
        
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != 0:
                return self.board[0][col]
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != 0:
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != 0:
            return self.board[0][2]
        
        # Check for tie
        if all(cell != 0 for row in self.board for cell in row):
            return 0
        
        return None

class Games(app_commands.Group):
    def __init__(self):
        super().__init__(name="games", description="Game commands")

    @app_commands.command(name="tictactoe", description="Play Tic-Tac-Toe with another player")
    async def tictactoe(self, interaction: discord.Interaction, opponent: discord.Member):
        if opponent.bot:
            return await interaction.response.send_message("You can't play with bots!", ephemeral=True)
        if opponent == interaction.user:
            return await interaction.response.send_message("You can't play with yourself!", ephemeral=True)
        
        view = TicTacToeView(interaction.user, opponent)
        embed = view.create_embed()
        
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()