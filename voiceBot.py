import discord
from discord.ext import commands
import ffmpeg
from ytdl import YTDLSource
import os
from dotenv import load_dotenv
load_dotenv()

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def debug(self, ctx):
        print(ctx.voice_client)
    
    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def local(self, ctx, *, query):
        """Play a file from local filesystem passing the path file as query"""
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: {}'.format(e)) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    @commands.command()
    async def play(self, ctx, *, url):
        """Play youtube song using youtube_dl (with download strategy)"""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: {}'.format(e)) if e else None)
        
        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Play youtube song using youtube_dl (stream strategy, without donwload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: {}'.format(e)) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))


    @commands.command()
    async def pause(self, ctx):
        """Pause currently song playing"""
        voice = ctx.voice_client

        if voice and voice.is_playing():
            voice.pause()
        else:
            await ctx.send('Currently no audio playing')

    @commands.command()
    async def resume(self, ctx):
        voice = ctx.voice_client

        if voice and voice.is_paused():
            voice.resume()
        else:
            await ctx.send('There is no audio paused')

    @commands.command()
    async def stop(self, ctx):
        """Stop and disconnects the bot"""
        await ctx.voice_client.disconnect()

    @commands.command()
    async def leave(self, ctx):
        """Stop and disconnects the bot"""
        await ctx.voice_client.disconnect()


    @commands.command()
    async def rojao(self, ctx):
        source = discord.FFmpegPCMAudio("./local/rojer.mp3")
        ctx.voice_client.play(source, after=lambda e: print('Player error: {}'.format(e)) if e else None)
        await ctx.send('Now playing: Roger')

    @play.before_invoke
    @local.before_invoke
    @stream.before_invoke
    @rojao.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send('You are not connected to a voice channel.')
                raise commands.CommandError('Author not connected to a voice channel.')

        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'))

@bot.event
async def on_ready():
    print('Logged in as')
    print('{}:{}'.format(bot.user, bot.user.id))
    print('------')

bot.add_cog(Music(bot))
bot.run(os.getenv('TOKEN'))
