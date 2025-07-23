import discord
from discord.ext import commands
from jishaku.cog import Jishaku
from datetime import datetime
import os
import sentry_sdk
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))
SENTRY_DSN = os.getenv("SENTRY_DSN")


sentry_sdk.init(
    dsn=SENTRY_DSN,
    send_default_pii=True,
)

# Allowed user IDs for Jishaku
ALLOWED_USERS = {
    USER_IDS_HERE 
}


intents = discord.Intents.all()
intents.message_content = True


class CustomJishaku(Jishaku):
    def __init__(self, bot):
        super().__init__(bot=bot)

    async def cog_check(self, ctx):
        return ctx.author.id in ALLOWED_USERS


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id=None
        )
        self.synced = False

    async def setup_hook(self):
        cogs = [
            "cogs.accept",
            "cogs.market",
            "cogs.error",
            "cogs.erlc",
            "cogs.session"
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded cog: {cog}")
            except Exception as e:
                print(f"❌ Failed to load cog: {cog}")
                print(f"↪️ {type(e).__name__}: {e}")

       
        await self.add_cog(CustomJishaku(self))

        if not self.synced:
            await self.tree.sync()
            self.synced = True


bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

   
    try:
        channel = await bot.fetch_channel(CHANNEL_ID)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await channel.send(f"Online as of `{now}`")
    except discord.NotFound:
        print(f"❌ Channel with ID {CHANNEL_ID} not found.")
    except discord.Forbidden:
        print(f"🚫 Bot lacks permission to access the channel.")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")


if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ TOKEN not found in environment variables.")
