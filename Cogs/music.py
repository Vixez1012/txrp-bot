import discord
from discord.ext import commands
import yt_dlp

ytdl_opts = {
    'format': 'bestaudio',
    'noplaylist': True,
    'quiet': True,
}

ffmpeg_opts = {
    'options': '-vn'
}


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            await ctx.send("🎶 Joined the voice channel!")
        else:
            await ctx.send("❌ You're not connected to a voice channel.")

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Left the voice channel.")
        else:
            await ctx.send("❌ I'm not in a voice channel.")

    @commands.command()
    async def play(self, ctx, *, url):
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        ytdl = yt_dlp.YoutubeDL(ytdl_opts)
        info = ytdl.extract_info(url, download=False)
        audio_url = info['url']
        source = await discord.FFmpegOpusAudio.from_probe(audio_url, **ffmpeg_opts)

        ctx.voice_client.stop()
        ctx.voice_client.play(source, after=lambda e: print(f"Error: {e}" if e else None))
        await ctx.send(f"🎧 Now playing: **{info['title']}**")

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Paused playback.")
        else:
            await ctx.send("❌ Nothing is playing right now.")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resumed playback.")
        else:
            await ctx.send("❌ Nothing is paused.")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.send("⏹️ Stopped playback.")
        else:
            await ctx.send("❌ I'm not in a voice channel.")


async def setup(bot):
    await bot.add_cog(Music(bot))
