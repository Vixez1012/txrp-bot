import discord
from discord.ext import commands
from gtts import gTTS
import asyncio
import os

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tts_active = {}  # {guild_id: bool}
        self.voice_clients = {}  # {guild_id: VoiceClient}
        self.tts_channels = {}  # {guild_id: text_channel_id}

    @commands.command(name='ttsjoin')
    async def tts_join(self, ctx):
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("You must be in a voice channel to start TTS.")
            return

        voice_channel = ctx.author.voice.channel
        vc = await voice_channel.connect()
        self.voice_clients[ctx.guild.id] = vc
        self.tts_active[ctx.guild.id] = True
        self.tts_channels[ctx.guild.id] = ctx.channel.id  # Save the text channel here
        await ctx.send(f"TTS activated in {voice_channel.name}, listening to {ctx.channel.mention}.")

    @commands.command(name='ttsleave')
    async def tts_leave(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients:
            vc = self.voice_clients[guild_id]
            await vc.disconnect()
            del self.voice_clients[guild_id]
            self.tts_active[guild_id] = False
            self.tts_channels.pop(guild_id, None)  # Clear saved channel
            await ctx.send("TTS deactivated and left the voice channel.")
        else:
            await ctx.send("I'm not in a voice channel.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # Ignore bots

        if not message.guild:
            return  # Ignore DMs

        guild_id = message.guild.id

        # Only speak messages if TTS is active and in the correct channel
        if (self.tts_active.get(guild_id)
            and guild_id in self.voice_clients
            and self.tts_channels.get(guild_id) == message.channel.id):

            vc = self.voice_clients[guild_id]
            if not vc.is_playing():
                try:
                    tts = gTTS(text=f"{message.author.display_name} says {message.content}")
                    filename = f"tts_{guild_id}.mp3"
                    tts.save(filename)

                    vc.play(discord.FFmpegPCMAudio(filename))
                    while vc.is_playing():
                        await asyncio.sleep(1)

                    os.remove(filename)
                except Exception as e:
                    print(f"TTS error: {e}")

                    print("🔊 Opus loaded:", discord.opus.is_loaded())

async def setup(bot):
    await bot.add_cog(TTS(bot))
