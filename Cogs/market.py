import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import requests


load_dotenv()

GROUP_ID = int(os.getenv("GROUP_ID"))
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
API_KEY = os.getenv("API_KEY")

class Market(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="sales", help="Get current group sales data.")
    async def sales(self, ctx):
        url = f'https://api.cookie-api.com/api/group/group-sales?workspace_id={WORKSPACE_ID}'
        headers = {
            'Authorization': API_KEY
        }
        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            # Check if data is an empty list
            if not data == []:
                embed1 = discord.Embed(
                    title="TexR | Recent Transactions",
                    description=f"**No recent transactions found for [Texas State Roleplay](https://www.roblox.com/communities/35525387/Texas-State-Roleplay-TexR#!/about)**",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed1)
                return

            if 'sales' in data:
                sales_count = data['sales']
                embed = discord.Embed(
                    title="CSRP | Recent Transactions",
                    description=f"**Recent transactions for [Texas State Roleplay](https://www.roblox.com/communities/35525387/Texas-State-Roleplay-TexR#!/about)**\n {sales_count}",
                    color=discord.Color.blue()
                )

                await ctx.send(embed=embed)
            else:
                await ctx.send("Unexpected data structure.")

        except Exception as e:
            await ctx.send(f"Error getting sales data: {e}")

async def setup(bot):
    await bot.add_cog(Market(bot))
