import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os

GROUP_ID = int(os.getenv("GROUP_ID"))
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
API_KEY = os.getenv("API_KEY")

class Accept(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_username_from_user_id(self, user_id):
        url = f"https://users.roblox.com/v1/users/{user_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("name")
                return None

    async def accept_join_request(self, user_id):
        url = f"https://api.cookie-api.com/api/roblox/group/join-requests/accept?workspace_id=248970"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{API_KEY}"
        }
        payload = {
            "user_id": int(user_id)
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "error": f"Status code: {response.status}",
                        "details": await response.text()
                    }

    @commands.hybrid_command(name="accept", description="Accept a Roblox join request")
    @app_commands.describe(user_id="The Roblox user ID")
    async def accept(self, ctx: commands.Context, user_id: int):
        await ctx.defer()

        username = await self.get_username_from_user_id(user_id)
        result = await self.accept_join_request(user_id)

        if "error" in result:
            embed = discord.Embed(
                title="❌ Failed to Accept Request",
                color=discord.Color.red()
            )
            embed.add_field(name="Error", value=result["error"], inline=False)
            embed.add_field(name="Details", value=result.get("details", "No details"), inline=False)
        else:
            embed = discord.Embed(
                title="✅ Join Request Accepted",
                color=discord.Color.green()
            )
            embed.add_field(name="Username", value=f"[{username}](https://www.roblox.com/users/{user_id}/profile)" or "Unknown", inline=True)
            embed.add_field(name="Group ID", value=str(GROUP_ID), inline=True)
            embed.add_field(name="Status", value="Request accepted successfully", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Accept(bot))
