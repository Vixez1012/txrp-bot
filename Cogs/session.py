import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import os
from dotenv import load_dotenv
from discord import ui, ButtonStyle

load_dotenv()
REQUIRED_ROLE_ID = int(os.getenv("REQUIRED_ROLE_ID"))
VOTE_LOG_CHANNEL_ID = int(os.getenv("VOTE_LOG_CHANNEL_ID"))
ROLE_TO_PING = int(os.getenv("ROLE_TO_PING"))

SESSION_STATUS = {
    "status": "Offline",
    "timestamp": int(datetime.now().timestamp()),
}

IMAGE_URLS = {
    "SSU": "https://cdn.discordapp.com/attachments/1354836588332580904/1397629793654276197/image.png?ex=68826bad&is=68811a2d&hm=8998bd9d5422afca165b58ab0133ce8c9db9ca8d9dacf4d0acb3b937d9fc93e0&",
    "SSD": "https://cdn.discordapp.com/attachments/1325968421405327530/1369452076232478760/Shutdown_Banner.png?ex=68821562&is=6880c3e2&hm=a7f7dc776dc57bc5ec592586f8ce6604685a9e80e0c07d106b7f9411a7426b5e&",
    "Full": "https://cdn.discordapp.com/attachments/1354836588332580904/1397715625836675193/image.png?ex=6882bb9d&is=68816a1d&hm=7a9605527857a4b203a699627af2b61ad5d6be25261d710aca457ed146d04013&",
    "Boost": "https://cdn.discordapp.com/attachments/1325968421405327530/1389843722207756338/image.png?ex=6881c7d5&is=68807655&hm=f3652aad165b13cee1c4637fbf007968c520492c095bac889544ae55d67c8a9d&",
    "Vote": "https://cdn.discordapp.com/attachments/1354836588332580904/1397627853058609253/image.png?ex=688269de&is=6881185e&hm=ba762b10346e5feed399b4c1d768c8ed88c4f2e500a53a9730bc76f55c696d5b&"
}

class SSULinkView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # or a custom timeout
        self.add_item(discord.ui.Button(
            label="Quick Join",
            style=ButtonStyle.link,
            url="https://policeroleplay.community/join/TexR"
        ))


class VoteView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, message: discord.Message):
        super().__init__(timeout=None)
        self.voters = set()
        self.message = message
        self.interaction = interaction

    def get_embed(self):
        now = int(datetime.now().timestamp())
        vote_count = len(self.voters)
        voters_list = "\n".join([f"<@{uid}>" for uid in self.voters]) or "No votes yet."
        embed = discord.Embed(
            title="TexR | Session Vote",
            description=f"A server vote has been started! Click the **Vote** button below to support starting a session!",
            color=discord.Color.from_rgb(240,167,15)
        )
        embed.set_image(url=IMAGE_URLS["Vote"])
        embed.add_field(name="Vote Information", value=f">>> **Votes:** {vote_count}/10\n **Voters:** {voters_list}", inline=False)
        embed.add_field(name="Additional Information", value=f">>> **Started At:** <t:{now}:F>\n **Started By:** {SESSION_STATUS['vote_started_by'].mention}", inline=False)
        return embed

    @discord.ui.button(label="\u2705 Vote", style=discord.ButtonStyle.success, custom_id="vote_button")
    async def vote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voters:
            self.voters.remove(interaction.user.id)
        else:
            self.voters.add(interaction.user.id)

        await self.message.edit(embed=self.get_embed(), view=self)
        await interaction.response.send_message("Your vote has been updated.", ephemeral=True)

class SessionDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Server Startup", value="SSU", emoji="\U0001F7E2"),
            discord.SelectOption(label="Server Shutdown", value="SSD", emoji="\u26D4"),
            discord.SelectOption(label="Server Full", value="Full", emoji="\U0001F5D3"),
            discord.SelectOption(label="Server Boost", value="Boost", emoji="\U0001F680"),
            discord.SelectOption(label="Server Vote", value="Vote", emoji="\U0001F5F3\uFE0F")
        ]
        super().__init__(placeholder="Choose an action", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        now = int(datetime.now().timestamp())
        channel = interaction.client.get_channel(VOTE_LOG_CHANNEL_ID)

        if choice == "SSU" and SESSION_STATUS["status"] in ("Offline", "Voting"):
            SESSION_STATUS["status"] = "Online"
            SESSION_STATUS["timestamp"] = now

            embed = discord.Embed(
                title="TexR | Session Startup",
                description="If you voted you will be required to join failure to do so will mean you can and will be infracted have fun in this session!!\n ***Server Details***\n >>> Server Name: **Texas State Roleplay | Realistic | Strict**\n Server Code: [**TexR**](https://policeroleplay.community/join/TexR)\n Server Owner: **Wouthuis**",
                color=discord.Color.from_rgb(240, 167, 15)
            )
            embed.set_image(url=IMAGE_URLS["SSU"])

        elif choice == "SSD" and SESSION_STATUS["status"] == "Online":
            SESSION_STATUS["status"] = "Offline"
            SESSION_STATUS["timestamp"] = now
            embed = discord.Embed(
                title="TexR | Server Shutdown",
                description="Unfortunately our session has come to an end. If you attended we hope you enjoyed yourself!",
                color=discord.Color.red()
            )
            embed.set_image(url=IMAGE_URLS["SSD"])

            await interaction.response.edit_message(content="SSD has been selected.", embed=None, view=None)
            await channel.send(embed=embed)  # No role ping here
            return


        elif choice == "Full" and SESSION_STATUS["status"] == "Online":
            embed = discord.Embed(
                title="TexR | Session Full",
                description="Our server is full! Join for amazing roleplays as spots will open!",
                color=discord.Color.from_rgb(240, 167, 15)
            )
            embed.set_image(url=IMAGE_URLS["Full"])

            await interaction.response.edit_message(content="Full has been selected.", embed=None, view=None)
            await channel.send(embed=embed)  # No role ping here
            return

        elif choice == "Boost" and SESSION_STATUS["status"] == "Online":
            embed = discord.Embed(
                title="TexR | Server Boost",
                description="Our server is low on players. Join to help us get full and participate in engaging roleplays!",
                color=discord.Color.from_rgb(240, 167, 15)
            )
            embed.set_image(url=IMAGE_URLS["Boost"])


        elif choice == "Vote" and SESSION_STATUS["status"] == "Offline":
            SESSION_STATUS["status"] = "Voting"
            SESSION_STATUS["timestamp"] = now
            SESSION_STATUS["vote_started_by"] = interaction.user
            dummy_embed = discord.Embed(
                title="Loading...",
                description="Creating vote panel...",
                color=discord.Color.greyple()
            )

            vote_message = await channel.send(embed=dummy_embed)
            vote_view = VoteView(interaction, vote_message)
            embed = vote_view.get_embed()

            await vote_message.channel.send(content=f"<@&{ROLE_TO_PING}>", embed=embed, view=vote_view)
            await vote_message.delete()

            await interaction.response.send_message("Vote started and posted in the vote log channel.", ephemeral=True)

            return

        else:
            await interaction.response.send_message("Invalid action based on current session status.", ephemeral=True)
            return

        await interaction.response.edit_message(content=f"{choice} has been selected.", embed=None, view=None)
        await channel.send(content=f"<@&{ROLE_TO_PING}>", embed=embed)

class SessionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SessionDropdown())

class Session(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="session", description="Manage or view the current server session.")
    async def session(self, interaction: discord.Interaction):
        if REQUIRED_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        status = SESSION_STATUS["status"]
        timestamp = SESSION_STATUS["timestamp"]

        embed = discord.Embed(
            title="\U0001F4CB Session Panel",
            description=f"**Current Status:** {status}\n**Since:** <t:{timestamp}:R>",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=SessionView(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Session(bot))
