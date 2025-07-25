import discord
from discord.ext import commands
import pyttsx3
import asyncio
import os

from discord import FFmpegPCMAudio

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.tts_engine = pyttsx3.init()
        self.text_queue = asyncio.Queue()

    @commands.command(name="ttsjoin")
    async def join_vc(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            vc = await channel.connect()
            self.voice_clients[ctx.guild.id] = vc
            await ctx.send("🔊 Joined the voice channel!")
            self.bot.loop.create_task(self.process_queue(ctx.guild.id))
        else:
            await ctx.send("❌ You must be in a voice channel to use this.")

    @commands.command(name="ttsleave")
    async def leave_vc(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Left the voice channel.")
        else:
            await ctx.send("❌ I'm not in a voice channel.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Optional: Only process messages from a specific text channel
        # if message.channel.id != YOUR_TEXT_CHANNEL_ID:
        #     return

        guild_id = message.guild.id if message.guild else None
        if guild_id in self.voice_clients:
            await self.text_queue.put((guild_id, f"{message.author.display_name} said {message.content}"))

    async def process_queue(self, guild_id):
        while True:
            guild_id_from_queue, text = await self.text_queue.get()

            if guild_id_from_queue != guild_id:
                continue

            # Save TTS output to audio file
            filename = f"tts_{guild_id}.mp3"
            self.tts_engine.save_to_file(text, filename)
            self.tts_engine.runAndWait()

            vc = self.voice_clients.get(guild_id)
            if vc and vc.is_connected():
                vc.play(FFmpegPCMAudio(source=filename))
                while vc.is_playing():
                    await asyncio.sleep(5)
                os.remove(filename)
            else:
                break

async def setup(bot):
    await bot.add_cog(TTS(bot))
