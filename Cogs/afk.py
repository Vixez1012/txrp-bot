import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime

AFK_FILE = "afk_data.json"

def load_afk_data():
    if not os.path.exists(AFK_FILE):
        with open(AFK_FILE, "w") as f:
            json.dump({}, f)

    with open(AFK_FILE, "r") as f:
        return json.load(f)

def save_afk_data(data):
    with open(AFK_FILE, "w") as f:
        json.dump(data, f, indent=4)

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = load_afk_data()

    @commands.hybrid_command(name="afk", help="Set your AFK status.")
    @app_commands.describe(reason="Reason you're AFK")
    async def afk(self, ctx: commands.Context, *, reason: str = "AFK"):
        user_id = str(ctx.author.id)

        self.afk_users[user_id] = {
            "reason": reason,
            "timestamp": int(datetime.utcnow().timestamp())
        }

        save_afk_data(self.afk_users)

        await ctx.send(f"✅ **{ctx.author.name}**, your AFK status has been set: **{reason}**", ephemeral=True)

        try:
            await ctx.author.send(f"You're now AFK: {reason}")
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.content.lower().startswith("/afk") or message.content.lower().startswith("-afk"):
            return

        user_id = str(message.author.id)

        if user_id in self.afk_users:
            del self.afk_users[user_id]
            save_afk_data(self.afk_users)
            await message.channel.send(f"👋 Welcome back, **{message.author.display_name}**. I removed your AFK status.")

        for mention in message.mentions:
            mention_id = str(mention.id)
            if mention_id in self.afk_users:
                afk_info = self.afk_users[mention_id]
                reason = afk_info.get("reason", "AFK")
                await message.channel.send(f"🔔 {mention.display_name} is currently AFK: **{reason}**")

async def setup(bot):
    await bot.add_cog(AFK(bot))
