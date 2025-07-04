import BotAssistant, BotObscura, BotNerd, BotAmethyst, asyncio, secret

async def main():
    await asyncio.gather(
        BotAssistant.bot.start(secret.ASSISTANTTOKEN),
        BotObscura.bot.start(secret.MODTOKEN),
        BotNerd.bot.start(secret.NERDTOKEN),
        BotAmethyst.bot.start(secret.AMETHYSTTOKEN),
    )

if __name__ == "__main__":
    asyncio.run(main())