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

    update_stats()

    # Prints if the bot is running
    print(f"✅ Bot is live. Logged in as {client.user}")


# ======================================
# Flask Stats
# ======================================
# This just sends things to flask_app to send to the front end. 

def update_stats():
    guilds = [guild.name for guild in client.guilds]
    user_count = sum(guild.member_count for guild in client.guilds)
    
    # might remove this. The front end won't run if the bot isn't running. 
    status = str(client.status)

    voice_channels = []
    for guild in client.guilds:
        for channel in guild.voice_channels:
            voice_channels.append(f"{guild.name}: {channel.name}")

    text_channels = []
    for guild in client.guilds:
        for channel in guild.text_channels:
            text_channels.append(f"{guild.name}: {channel.name}")
    
    roles = []
    for guild in client.guilds:
        for role in guild.roles:
            if role.name != "@everyone":
                roles.append(f"{guild.name}: {role.name}")
    
    # Send to flask_app
    flask_app.update_bot_stats(guilds, user_count, status, voice_channels, text_channels, roles)


# ========================================
# Leveling system
# ======================================
# /level command to print XP and Level
@client.command()
async def level(ctx):
    user_id = str(ctx.author.id)
    xp, level = await lvl.print_level(user_id)
    req_xp = await lvl.req_xp(user_id)

    # creating a embed
    embed = discord.Embed(title = f"{ctx.author.display_name}'s Level Info", color=discord.Color.blue())

    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="XP", value=f"{xp} / {req_xp}", inline=True)

    # adding a footer
    embed.set_footer(text="💬 Keep chatting to earn more XP! 💬")

    await ctx.send(embed=embed)



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
    prev_lvl, curr_lvl = await lvl.add_xp(UserId, 10)

    # sends a notification to user once leveled up
    await lvl.check_levelup(message, prev_lvl, curr_lvl)

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



# =======================
# YOUTUBE PLAYER
# =======================

# FFmpeg options for streaming
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -c:a libopus -f opus'
}

# YTDL options to get playable audio URLs
ytdl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch',
    'noplaylist': True,
}
ytdl = yt_dlp.YoutubeDL(ytdl_opts)

# Playlist instance
playlist = Playlist()


# =======================
# HELPER FUNCTIONS
# =======================
@client.command()
async def play_next(ctx):
    next_song = playlist.play_next()
    vc = ctx.voice_client

    if not vc or not next_song:
        await ctx.send("✅ Playlist ended.")
        return

    try:
        # Fetch fresh stream URL from the original YouTube page
        info = ytdl.extract_info(next_song.page_url, download=False)
        source_url = info['url']
        next_song.base_url = source_url  # store current playable URL

        # Play the audio
        vc.play(
            discord.FFmpegOpusAudio(source_url, **FFMPEG_OPTIONS),
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), ctx.bot.loop)
        )

        await ctx.send(embed=next_song.info.format_output("Now Playing 🎵"))

    except Exception as e:
        await ctx.send(f"❌ Error playing {next_song.info.title}: {e}")
        print(f"Error in play_next: {e}")
        await play_next(ctx)  # skip to next song if current fails


# =======================
# MUSIC COMMANDS
# =======================
@client.command()
async def play(ctx, *, query):
    """Add a song to the playlist and play it."""
    vc = ctx.voice_client
    if not vc:
        if ctx.author.voice:
            vc = await ctx.author.voice.channel.connect()
        else:
            await ctx.send("❌ You need to be in a voice channel.")
            return

    try:
        # Extract info from YouTube (or search)
        info = ytdl.extract_info(query, download=False)
        if 'entries' in info:  # search result
            info = info['entries'][0]

        # Create Song instance
        song = Song(
            origin="YouTube",
            host=ctx.author.name,
            base_url=None,
            uploader=info.get('uploader', 'Unknown'),
            title=info.get('title', 'Unknown'),
            duration=info.get('duration'),
            page_url=info.get('webpage_url'),
            thumbnail=info.get('thumbnail')
        )

        # Add song to playlist
        playlist.add_track(song)
        await ctx.send(embed=song.info.format_output("Added to Queue"))

        # Start playback if nothing is playing
        if not vc.is_playing() and playlist.get_len() > 0:
            await play_next(ctx)

    except Exception as e:
        await ctx.send(f"❌ Failed to add/play song: {e}")
        print(f"Error in play command: {e}")

@client.command()
async def pause(ctx):
    """Pause the current song."""
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("⏸ Paused playback")
    else:
        await ctx.send("❌ Nothing is currently playing.")
        
@client.command()
async def resume(ctx):
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("▶ Resumed playback")
    else:
        await ctx.send("❌ Nothing is paused.")


@client.command()
async def queue(ctx):
    if playlist.get_len() == 0 and not playlist.playlist_history:
        await ctx.send("❌ The playlist is empty")
        return

    lines = []
    if playlist.playlist_history:
        current = playlist.playlist_history[-1]
        lines.append(f"🎵 Now playing: {current.info.title}")
    for i, song in enumerate(playlist.playlist):
        lines.append(f"{i+1}. {song.info.title}")

    await ctx.send("\n".join(lines))


@client.command()
async def clear(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()
    playlist.clear_playlist()
    await ctx.send("✅ Cleared the playlist")

@client.command()
async def skip(ctx):
    """Skip the current song and play the next one."""
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("⏭️ Skipped the current song.")
    else:
        await ctx.send("❌ No song is currently playing.")


client.run(TOKEN)
