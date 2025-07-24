import discord
from discord.ext import commands
from discord import app_commands
import time
import os
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
REQUIRED_ROLE_ID = int(os.getenv("STAFF_ID"))
STAFF_CHANNEL_ID = int(os.getenv("STAFF_CHANNEL_ID"))

# Simulate ERLC player count fetching (replace with your real function)
def get_erlc_player_count():
    return 26  # Replace with dynamic data fetching logic

# Global cooldown tracker
last_staffrequest_time = 0
timestamp = int(datetime.now().timestamp())

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="staff", with_app_command=True)
    async def staff(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a subcommand.")

    @staff.command(name="request", help="Request for staff to join the server.")
    @app_commands.describe(reason="Reason for staff.")
    async def staffrequest(self, ctx: commands.Context, *, reason: str):
        global last_staffrequest_time

        # Role check
        if REQUIRED_ROLE_ID not in [role.id for role in ctx.author.roles]:
            await ctx.send("You don't have permission to use this command.", ephemeral=True)
            return

        # Cooldown check
        current_time = time.time()
        if current_time - last_staffrequest_time < 1800:
            remaining = int((1800 - (current_time - last_staffrequest_time)) // 60)
            await ctx.send(f"This command is on cooldown. Try again in {remaining} minute(s).", ephemeral=True)
            return

        # Set cooldown
        last_staffrequest_time = current_time

        # Create embed
        player_count = get_erlc_player_count()
        embed = discord.Embed(
            title="🚨 Staff Assistance Requested",
            description=f" A new staff request has been sent by {ctx.author.mention} ({ctx.author.id})",
            color=discord.Color.blue()
        )
        embed.add_field(name="Request Information", value=f">>> **Reason:** {reason}\n **In-Game Players:** {player_count}/40\n **Requested By:** {ctx.author.mention}\n **Time:** <t:{timestamp}:F> (<t:{timestamp}:R>)")
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        await ctx.send("✅ Your request has been submitted.", ephemeral=True)
        await self.bot.get_channel(STAFF_CHANNEL_ID).send(content="<@&1308841437248360549> | <@&1308841437248360549>", embed=embed)



async def setup(bot):
    await bot.add_cog(Staff(bot))
