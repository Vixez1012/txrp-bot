import discord
from discord.ext import commands
from discord import app_commands
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
REQUIRED_ROLE_ID = int(os.getenv("DIRECTIVE"))
STAFF_CHANNEL_ID = int(os.getenv("AD_CHANNEL"))

class Ad(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="paidad", description="Send a paid advertisement.")
    @app_commands.describe(
        ping="Who to ping (None, Here, Everyone)",
        advertisement="The advertisement text.",
        representative="The user who is the server representative."
    )
    @app_commands.choices(ping=[
        app_commands.Choice(name="None", value="none"),
        app_commands.Choice(name="Here", value="here"),
        app_commands.Choice(name="Everyone", value="everyone")
    ])
    async def paidad(self, interaction: discord.Interaction, ping: app_commands.Choice[str], advertisement: str, representative: discord.User):
        if REQUIRED_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        timestamp = int(time.time())
        embed = discord.Embed(
            title="📢 Paid Advertisement",
            description=advertisement,
            color=discord.Color.green()
        )
        embed.add_field(name="Server Representative", value=representative.mention, inline=False)
        embed.add_field(name="Sent By", value=interaction.user.mention, inline=False)
        embed.add_field(name="Time", value=f"<t:{timestamp}:F> (<t:{timestamp}:R>)", inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        ping_text = ""
        if ping.value == "here":
            ping_text = "@here"
        elif ping.value == "everyone":
            ping_text = "@everyone"

        await self.bot.get_channel(STAFF_CHANNEL_ID).send(content=ping_text, embed=embed)

        await interaction.user.send("✅ Your paid advertisement was sent successfully.")
        await interaction.response.send_message("Advertisement sent!", ephemeral=True)

        print(f"[PAID AD LOG] {interaction.user} sent an ad at {datetime.now().isoformat()}:")
        print(advertisement)

async def setup(bot):
    await bot.add_cog(Ad(bot))
