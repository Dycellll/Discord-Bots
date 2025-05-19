import discord, asyncio
from discord import app_commands

class AICommands(app_commands.Group):
    def __init__(self, client):
        super().__init__(name="ai", description="AI-related commands")
        self.client = client

    async def AskAISmart(self, question: str):
        try:
            chat_completion = self.client.chat.completions.create(
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

    @app_commands.command(name="ask", description="Ask AI a question and get an answer.")
    @app_commands.describe(question="The question u want to ask to the AI.", ephemeral="Whether the answer message is only shown to you (True) or to everyone (False). Defaults to True.")
    async def ai_ask(self, ctx: discord.Interaction, question: str, ephemeral: bool = True):
        try:
            await ctx.response.defer(ephemeral=ephemeral)

            response = await self.AskAISmart(question)
            chunks = self.split_text(response, max_length=4096)

            embed = discord.Embed(
                title="AI Response (Part 1)",
                description=chunks[0],
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"User Question: {question}")

            await ctx.followup.send(embed=embed, ephemeral=ephemeral)

            for i, chunk in enumerate(chunks[1:], start=2):
                embed = discord.Embed(
                    title=f"AI Response (Part {i})",
                    description=chunk,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"User Question: {question}")

                await ctx.followup.send(embed=embed, ephemeral=ephemeral)

        except Exception as e:
            print(f"An error occurred: {e}")
            await ctx.followup.send("Sorry, something went wrong while processing your request.", ephemeral=True)  # Use ctx directly


    @app_commands.command(name="rizz", description="Ask AI for a pickup line, with optional specific parameters (Example: 'food' or 'sweet').")
    @app_commands.describe(parameters="The parameters you want to give to the AI.", ephemeral="Whether the answer message is only shown to you (True) or to everyone (False). Defaults to True.")
    async def ai_rizz(self, ctx: discord.Interaction, parameters: str = "", ephemeral: bool = True):
        try:
            await ctx.response.defer(ephemeral=ephemeral)

            if parameters == "":
                prompt = "Give me a random pickup line. Make it good but not obvious, since this same request will be ran many times. Return JUST the pickup line, nothing else"
            else:
                prompt = f"Give me a random pickup line. Make it good but not obvious, since this same request will be ran many times. Make it follow these parameters: {parameters}. Return JUST the pickup line, nothing else"

            response = await self.AskAISmart(prompt)
            chunks = self.split_text(response, max_length=4096)

            embed = discord.Embed(
                title="AI Response (Part 1)",
                description=chunks[0],
                color=discord.Color.blue()
            )

            await ctx.followup.send(embed=embed, ephemeral=ephemeral)

            for i, chunk in enumerate(chunks[1:], start=2):
                embed = discord.Embed(
                    title=f"AI Response (Part {i})",
                    description=chunk,
                    color=discord.Color.blue()
                )

                await ctx.followup.send(embed=embed, ephemeral=ephemeral)

        except Exception as e:
            print(f"An error occurred: {e}")
            await ctx.followup.send("Sorry, something went wrong while processing your request.", ephemeral=True)

    def split_text(self, text: str, max_length: int) -> list[str]:
        """Split text into chunks of max_length."""
        return [text[i:i + max_length] for i in range(0, len(text), max_length)]

async def setup(bot, client):
    bot.tree.add_command(AICommands(client))