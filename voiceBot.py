import discord
import asyncio
from discord.ext import commands
from decouple import config
import ffmpeg
import youtube_dl
import os
from time import sleep
from utils import donwload_video

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

client = commands.Bot(command_prefix='!')

permission_role = "DJ"

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.command()
async def debug(ctx):
    # print('connected to ' + ctx.author.voice.channel.name)
    print([role.name for role in ctx.author.roles])

@client.command()
async def play(ctx, url: str):

    if ctx.author.voice is None:
        return await ctx.send('User must be in a voice channel to request the bot.')
    
    local_song = os.path.isfile('song.mp3')

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    try:
        if local_song:
            os.remove('song.mp3')
    
    except PermissionError:
        await ctx.send('Wait for the current playing music to end')
        return

    voice_channel = ctx.author.voice.channel

    if is_connected(ctx):
        await voice.disconnect()

    try:
        await voice_channel.connect()
        print('Bot connected to {} channel'.format(voice_channel.name))

    except discord.errors.ClientException:
        print('Already connected, passing this step..')
    
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    # if permission_role in [role.name for role in ctx.author.roles]:

    donwload_video(url)
    print('Song downloaded')

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: handle_song_ended(ctx))


@client.command
async def stream(ctx, url: str):
    """Streams from a url (same as yt, but doesn't predownload)"""
    player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
    ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.send('Now playing: {}'.format(player.title))

def is_connected(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()

def handle_song_ended(ctx):
    print('Song ended, removing local files...')

    local_song = os.path.isfile('song.mp3')

    if local_song:
        os.remove('song.mp3')
        print('song.mp3 deleted')
    
@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send('The bot is not connected to a voice channel.')

@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.pause()
    else:
        await ctx.send('Currently no audio playing')

@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
    else:
        await ctx.send('Currently no audio paused') 

@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        voice.stop()
    else:
        await ctx.send('Current no audio playing')

client.run(config('TOKEN'))