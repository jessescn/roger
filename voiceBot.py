import discord
from discord.ext import commands
import ffmpeg
import youtube_dl
import os
from utils import donwload_video
from dotenv import load_dotenv
load_dotenv()

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.command()
async def debug(ctx):
    # print('connected to ' + ctx.author.voice.channel.name)
    print(client.voice_clients)

@client.command()
async def play(ctx, url: str):

    if ctx.author.voice is None:
        return await ctx.send('User must be in a voice channel to request the bot.')
    
    local_song = os.path.isfile('song.mp3')

    try:
        if local_song:
            os.remove('song.mp3')
    
    except PermissionError:
        await ctx.send('Wait for the current playing music to end')
        return

    voice_channel = ctx.author.voice.channel

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    try:
        if voice == None:
            await voice_channel.connect()
            print('Bot connected to {} channel'.format(voice_channel.name))

    except discord.errors.ClientException:
        print('Already connected, passing this step..')
    
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    donwload_video(url)
    print('Song downloaded')

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: handle_song_ended(ctx))

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

    if voice:
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

client.run(os.getenv('TOKEN'))