# cogs/infractions.py
import discord
from discord.ext import commands
from discord import app_commands
import json, os, uuid
from datetime import datetime

INFRACTION_FILE = "data/infractions.json"
STAFF_ROLE_ID = int(os.getenv("IA"))
LOG_CHANNEL_ID = int(os.getenv("INFRACTION_LOG_CHANNEL"))


# Load or create the infractions file
def load_infractions():
    if not os.path.exists(INFRACTION_FILE):
        with open(INFRACTION_FILE, "w") as f:
            json.dump({}, f)
    with open(INFRACTION_FILE, "r") as f:
        return json.load(f)

def save_infractions(data):
    with open(INFRACTION_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Infractions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="infract", description="Issue an infraction to a user.")
    @app_commands.describe(member="User to infract", action="Type of infraction", reason="Reason for the infraction")
    async def infract(self, ctx, member: discord.Member, action: str, *, reason: str):
        # Check if the user has the required role
        if not any(role.id == STAFF_ROLE_ID for role in ctx.author.roles):
            return await ctx.reply("You do not have permission to use this command.", ephemeral=True)

        infraction_id = str(uuid.uuid4())[:8]
        date = int(datetime.now().timestamp())

        entry = {
            "user": f"<@{member.id}> ({member.id})",
            "action": action,
            "reason": reason,
            "date": f"<t:{date}:F>",
            "handler": f"{ctx.author.name} ({ctx.author.id})"
        }

        infractions = load_infractions()
        infractions[infraction_id] = entry
        save_infractions(infractions)

        # DM the user
        try:
            embed_dm = discord.Embed(
                title="⚠️ You have received an infraction",
                color=discord.Color.red()
            )
            embed_dm.add_field(name="Action", value=action, inline=False)
            embed_dm.add_field(name="Reason", value=reason, inline=False)
            embed_dm.add_field(name="Infraction ID", value=infraction_id, inline=False)
            embed_dm.add_field(name="Date", value=f"<t:{date}:F>", inline=False)
            await member.send(embed=embed_dm)
        except discord.Forbidden:
            await ctx.send("User could not be DMed.", ephemeral=True)

        await ctx.send(f"Infraction issued to {member.mention} with ID `{infraction_id}` ✅", ephemeral=True)
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed_log = discord.Embed(
                title="Texas State Roleplay Infraction",
                description=f"━━━━━━━━━━━━━━━━━━━━━\n\n ➥ **User:** <@{member.id}>\n\n━━━━━━━━━━━━━━━━━━━━━\n\n ➥ **Punishment:** {action}\n\n━━━━━━━━━━━━━━━━━━━━━\n\n ➥ **Reason:** {reason}",
                color=discord.Color.from_rgb(240, 167, 15)
            )
            embed_log.set_footer(text=f"Signed by: {ctx.author} | Infraction ID: {infraction_id}", icon_url=ctx.author.display_avatar.url)

            await log_channel.send(content=f"{member.mention}" ,embed=embed_log)

    @commands.hybrid_command(name="lookup", description="Lookup an infraction by ID.")
    @app_commands.describe(code="The infraction ID to lookup")
    async def lookup(self, ctx, code: str):
        if not any(role.id == STAFF_ROLE_ID for role in ctx.author.roles):
            return await ctx.reply("You do not have permission to use this command.", ephemeral=True)

        infractions = load_infractions()
        if code not in infractions:
            return await ctx.reply("❌ Infraction not found.", ephemeral=True)

        entry = infractions[code]
        embed = discord.Embed(title=f"🔍 Infraction `{code}`", color=discord.Color.orange())
        for key, value in entry.items():
            embed.add_field(name=key.capitalize(), value=value, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Infractions(bot))
