import os
import discord
import flask_app
import leveling_sys as lvl
import asyncio
import yt_dlp
from threading import Thread
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv 
from playlist import Playlist
from song import Song


# Token stuff
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise ValueError("No Token Found.")

# TODO: We need to make this more portable. 
GUILD_ID = 1415377687526248582

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

client = commands.Bot(command_prefix="/", intents=intents)


# initialize database on startup
@client.event
async def on_ready():
    print("Bot connecting...")

    # initialize database on startup
    await lvl.init_db()

    # Multithreading for Flask
    flask_thread = Thread(target=flask_app.run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # This creates a file guilds.txt that stores all the servers that the bot is in. 
    file = open('guilds.txt', 'w+')
    guilds = client.guilds
    
    for guild in guilds:
        file.write(f'{guild.id}:{guild.name}\n')
    file.close()

    # Load cogs
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            cog_name = f'cogs.{filename[:-3]}'
            try:
                await client.load_extension(cog_name)
                print(f'Loaded cog: {cog_name}')
            except Exception as e:
                print(f'Failed to load {cog_name}: {e}')

    # Sync slash commands
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await client.tree.sync(guild=guild)
        print(f'Synced {len(synced)} commands to guild {guild.id}')
    except Exception as e:
        print(f'Error syncing commands: {e}')

    # Prints if the bot is running
    print(f"✅ Bot is live. Logged in as {client.user}")

async def on_message(self, message):
        if message.author == self.user:
            return
            
        if message.content.startswith('hello'):
            await message.channel.send(f'Hi there {message.author}')
            await self.process_commands(message)

@client.command()
async def test(ctx):
    await ctx.send("Test")


# ========================================
# Leveling system
# ======================================
# /level command to print XP and Level
@client.command()
async def level(ctx):
    user_id = str(ctx.author.id)
    xp, level = await lvl.print_level(user_id)

    # creating a embed
    embed = discord.Embed(title = f"{ctx.author.display_name}'s Level Info", color=discord.Color.blue())

    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="XP", value=xp, inline=True)

    # adding a footer
    embed.set_footer(text="Keep chatting to earn more XP!")

    await ctx.send(f"Hello, {ctx.author.mention}!\nYour current Level is {level} and Xp is at {xp}")

@client.command()
async def leaderboard(ctx):
    top_users = await lvl.Leaderboard(limit=10)  # fetch top 10

    if not top_users:
        await ctx.send("No users found in the leaderboard.")
        return

    embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.gold())

    for i, (user_id, level, xp) in enumerate(top_users, start=1):
        # get the Member object from the guild
        member = ctx.guild.get_member(int(user_id))
        name = member.display_name if member else f"User ID {user_id}"  # fallback if not in server
        embed.add_field(name=f"{i}. {name}", value=f"Level {level} | XP {xp}", inline=False)

    await ctx.send(embed=embed)



# /reset command to reset user
@client.command()
@has_permissions(administrator=True)
async def reset(ctx, member: discord.Member):
    await lvl.reset_level(member.id)
    await ctx.send(f"{member.mention}'s level has been reset!")

@reset.error
async def reset_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("❌ You do not have permission to reset levels.")


# used to detect messages for adding XP to data base
@client.event
async def on_message(message):
    # ignore the bots own messages
    if message.author == client.user:
        return
    
    # ignore / commands otherwise gives XP still
    if message.content.startswith("/"):
        await client.process_commands(message)
        return

    # fetch the user's id 
    UserId = str(message.author.id)
    await lvl.add_xp(UserId, 10)

    # Allow other bot commands (like /level or /test) to still work after this event
    await client.process_commands(message)


# Detects when someone joins the server.
# Kevin this might be useful to keep metrics on when someone joins the server. 
@client.event
async def on_member_join(member):
    # add user_id to the datbase on join
    user_id = str(member.id)
    await lvl.auto_user(user_id)
    await member.send()

# When auto delete user from DB upon leaving server
@client.event
async def on_member_remove(member):
    user_id = str(member.id)
    await lvl.auto_delete(user_id)
    print(f"{member.display_name} has left the server.")
    await member.send()

# ==========================
# Music Playback
# ==========================

# For playing audio in voice calls. 
@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    user_id = str(member.id)
    await member.kick(reason=reason)
    await lvl.auto_delete(user_id)
    await ctx.send(f'{member} has been kicked.')
    
@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Error: You do not have permission to kick people.")

@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    user_id = str(member.id)
    await lvl.auto_delete(user_id)
    await member.ban(reason=reason)
    await ctx.send(f'{member} has been banned.')

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Error: You do not have permission to ban people.")

@client.command(pass_context = True)
async def join(ctx):
    if(ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        # source = FFmpegPCMAudio( FILE NAME HERE )
        # player = voice.play(source)


@client.command(pass_context = True)
async def leave(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("left voice channel")
    else:
        await ctx.send("Not in a voice channel.")



playlist = Playlist()
# ======= HELPER FUNCTION =======
async def play_song(ctx, url):
    """Plays a YouTube song in the voice channel."""
    voice_client = ctx.voice_client
    if not voice_client:
        await ctx.send("The bot is not connected to a voice channel.")
        return

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch",
        "extract_flat": "in_playlist",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if "entries" in info:
            info = info["entries"][0]
        source_url = info["url"]
        title = info.get("title", "Unknown Title")
        uploader = info.get("uploader", "Unknown")
        duration = info.get("duration")
        webpage_url = info.get("webpage_url")
        thumbnail = info.get("thumbnail")

    # Create a Song instance
    song = Song(
        origin="YouTube",
        host=ctx.author.name,
        base_url=source_url,
        uploader=uploader,
        title=title,
        duration=duration,
        webpage_url=webpage_url,
        thumbnail=thumbnail,
    )

    # Add to playlist
    playlist.add_track(song)
    await ctx.send(embed=song.info.format_output("Added to Queue"))

    # If not already playing, start playback
    if not voice_client.is_playing():
        await start_playback(ctx)


async def start_playback(ctx):
    """Plays the next song in the playlist queue."""
    if playlist.get_len() == 0:
        await ctx.send("Queue is empty.")
        return

    current_song = playlist.play_next()
    voice_client = ctx.voice_client
    if not voice_client:
        await ctx.send("Not connected to a voice channel.")
        return

    ffmpeg_options = {"options": "-vn"}
    source = await discord.FFmpegOpusAudio.from_probe(current_song.base_url, **ffmpeg_options)
    voice_client.play(
        source,
        after=lambda e: asyncio.run_coroutine_threadsafe(start_playback(ctx), client.loop),
    )

    await ctx.send(embed=current_song.info.format_output("Now Playing 🎵"))


# ======= MUSIC COMMANDS =======

# Use the on_ready(): at the top of the file.
# Re defining the existing function broke everything else. 
# Python isn't smart enough as a language to warn you when you define a function twice, so you 
# have to be really careful. 

@client.command()
async def play(ctx, *, url):
    """Add a song to the queue and play it."""
    await play_song(ctx, url)


@client.command()
async def skip(ctx):
    """Skip the current song."""
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Skipped the current song.")
    else:
        await ctx.send("No song is currently playing.")


@client.command()
async def pause(ctx):
    """Pause the current song."""
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Paused playback.")
    else:
        await ctx.send("Nothing is playing to pause.")


@client.command()
async def resume(ctx):
    """Resume paused playback."""
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Resumed playback.")
    else:
        await ctx.send("Nothing is paused right now.")


@client.command()
async def queue(ctx):
    """Show the current playlist queue."""
    if playlist.get_len() == 0:
        await ctx.send("The queue is empty.")
        return

    queue_list = [f"{i+1}. {s.info.title}" for i, s in enumerate(playlist.playlist)]
    message = "\n".join(queue_list)
    await ctx.send(f"**Current Queue:**\n{message}")

@client.command()
async def clear(ctx):
    """Clear the playlist and history."""
    message = playlist.clear_playlist()
    await ctx.send(message)
    
client.run(TOKEN)