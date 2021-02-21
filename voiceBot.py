import discord
from discord.ext import commands
import ffmpeg
from ytdl import YTDLSource
import os
from gtts import gTTS
from dotenv import load_dotenv
load_dotenv()

class Roger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rojao(self, ctx):
        filepath = "./local/roger.mp3"
        await self.play_audio(ctx, filepath, "rojão")

    @commands.command()
    async def a(self, ctx):
        filepath = "./local/aa-audio.mp3"
        await self.play_audio(ctx, filepath, "aa")

    @commands.command()
    async def barril(self, ctx):
        filepath = "./local/barril.mp3"
        await self.play_audio(ctx, filepath, "barril")
    
    @commands.command()
    async def oof(self, ctx):
        filepath = "./local/oof.mp3"
        await self.play_audio(ctx, filepath, "oof")

    @commands.command()
    async def talk(self, ctx, text: str):
        language = "pt"
        output = gTTS(text=text, lang=language, slow=False)
        output.save('output.mp3')
        await self.play_audio(ctx, 'output.mp3', text)

    async def play_audio(self, ctx, filepath: str, name: str):
        source = discord.FFmpegPCMAudio(filepath)
        ctx.voice_client.play(source, after=lambda e: print('Player error: {}'.format(e)) if e else None)
        await ctx.send('Now playing: {}'.format(name))

    @barril.before_invoke
    @a.before_invoke
    @rojao.before_invoke
    @oof.before_invoke
    @talk.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send('You are not connected to a voice channel.')
                raise commands.CommandError('Author not connected to a voice channel.')

        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.queue_list = []
        self.current_playing = ""
    
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
        player = await YTDLSource.from_url(url, loop=self.bot.loop)
        self.queue_list.append(player)

        if len(self.queue_list) == 1:
            source = self.queue_list[0]
            async with ctx.typing():
                ctx.voice_client.play(source, after=lambda e: self.play_next(ctx))
            
            await ctx.send('Now playing: {}'.format(source.title))
        else:
            await ctx.send('Added to queue.')

    def play_next(self, ctx):
        if len(self.queue_list) > 1:
            del self.queue_list[0]
            ctx.voice_client.play(self.queue_list[0], after=lambda e: self.play_next(ctx))

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
    async def skip(self, ctx):
        """Skip the current playing song"""
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send('{} skipped!'.format(self.queue_list[0].title))
            self.play_next(ctx)
        else:
            await ctx.send('There is no current playing')
         

    @commands.command()
    async def stop(self, ctx):
        """Stop and disconnects the bot"""
        self.queue_list = []
        await ctx.voice_client.disconnect()

    @commands.command()
    async def leave(self, ctx):
        """Stop and disconnects the bot"""
        self.queue_list = []
        await ctx.voice_client.stop()

    @commands.command()
    async def remove(self, ctx, position: int):
        """Remove a song from queue"""
        if position == 1:
            return

        if position >= len(self.queue_list):
            self.queue_list.pop(position - 1)
            await ctx.send('Song {} removed.'.format(position))

        else:
            await ctx.send('Invalid song position in queue.')

    @commands.command()
    async def queue(self, ctx):
        """Print que current queue list"""
        if len(self.queue_list) == 0:
            await ctx.send('The queue is empty')
            return

        current_queue = self.generate_queue_message()
        await ctx.send(current_queue)

    def generate_queue_message(self):
        """Generate the formated message with songs in queue"""
        message = "Now Playing:\n{}".format(self.queue_list[0].title)
        message += "\n\nNext Songs:\n"
        for i in range(1, len(self.queue_list)):
            song = self.queue_list[i]
            message += "{}. {}\n".format(i, song.title)
        
        return message

    @play.before_invoke
    @local.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send('You are not connected to a voice channel.')
                raise commands.CommandError('Author not connected to a voice channel.')

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'))

@bot.event
async def on_ready():
    print('Logged in as {}'.format(bot.user))
    print('------')

bot.add_cog(Roger(bot))
bot.add_cog(Music(bot))
bot.run(os.getenv('TOKEN'))
