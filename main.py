import os
import discord
import flask_app
import leveling_sys as lvl
import asyncio
import yt_dlp
from threading import Thread
#from flask import Flask, request, jsonify, render_template
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

class Client(commands.Bot):
    async def on_ready(self):
        print(f'logged in as {self.user}')

        try:
            guild = discord.Object(id=GUILD_ID)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')

        except Exception as e:
            print(f'Error syncing commands: {e}')

    async def on_message(self, message):
        if message.author == self.user:
            return
            
        if message.content.startswith('hello'):
            await message.channel.send(f'Hi there {message.author}')
            await self.process_commands(message)


    """async def on_reaction_add(self, reaction, user):
        if user.bot:
                return
            
        guild = reaction.message.guild

        if not guild:
            return
            
        if hasattr(self, "colour_role_message_id") and reaction.message.id != self.colour_role_message_id:
            return 
            
        emoji = str(reaction.emoji)
            
        reaction_role_map = {
            '❤️': 'Red',
            '💙': 'Blue',
            '💚': 'Green',
            '💛': 'Yellow',
            '🧡': 'Orange'
        }

        if emoji in reaction_role_map:
            role_name = reaction_role_map[emoji]
            role = discord.utils.get(guild.roles, name=role_name)

            if role and user:
                    await user.add_roles(role)
                    print(f"Assigned {role_name} to {user}")
        
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
            
        guild = reaction.message.guild

        if not guild:
            return
            
        if hasattr(self, "colour_role_message_id") and reaction.message.id != self.colour_role_message_id:
            return 
            
        emoji = str(reaction.emoji)
            
        reaction_role_map = {
            '❤️': 'Red',
            '💙': 'Blue',
            '💚': 'Green',
            '💛': 'Yellow',
            '🧡': 'Orange'
        }

        if emoji in reaction_role_map:
            role_name = reaction_role_map[emoji]
            role = discord.utils.get(guild.roles, name=role_name)

            if role and user:
                    await user.remove_roles(role)
                    print(f"Remove {role_name} from {user}") """






intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

client = commands.Bot(command_prefix="/", intents=intents)


# initialize database on startup
@client.event
async def on_ready():
    await lvl.init_db()

    await client.tree.sync(guild=GUILD_ID)
    print("Ready")

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

@client.command()
async def test(ctx):
    await ctx.send("Test")


# ========================================
# Reaction Roles
# ========================================

# React to a message to get certain roles

# TODO: Change ID so that it gets it from guilds.txt 
GUILD_ID = discord.Object(id=1415377687526248582)

@client.tree.command(name="colourroles", description="Create a message that lets users pick a colour role", guild=GUILD_ID)
async def colour_roles(interaction: discord.Interaction):
    # Check admin
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("This command requires admin permissions.", ephemeral=True)
        return
    
    # Discord requires something to respond within three seconds of it being called. 
    # There's not really a way to make any of this quicker. This ephermeral stops discord
    # from stopping a function before it completes
    await interaction.response.defer(ephemeral=True)
    
    description = (
        "React to this message to get your color role!\n\n"
        "❤️ Red\n"
        "💙 Blue\n"
        "💚 Green\n"
        "💛 Yellow\n"
        "🧡 Orange\n"
    )
    
    embed = discord.Embed(title="Pick your color", description=description, color=discord.Color.blurple())
    message = await interaction.channel.send(embed=embed)

    emojis = ['❤️', '💙', '💚', '💛', '🧡']
    for emoji in emojis: 
        await message.add_reaction(emoji)

    client.colour_role_message_id = message.id

    await interaction.followup.send("Colour role message created!", ephemeral=True)

@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    
    guild = reaction.message.guild
    if not guild:
        return
        
    if hasattr(client, "colour_role_message_id") and reaction.message.id != client.colour_role_message_id:
        return 
        
    emoji = str(reaction.emoji)
    
    reaction_role_map = {
        '❤️': 'Red',
        '💙': 'Blue',
        '💚': 'Green',
        '💛': 'Yellow',
        '🧡': 'Orange'
    }

    if emoji in reaction_role_map:
        role_name = reaction_role_map[emoji]
        role = discord.utils.get(guild.roles, name=role_name)
        member = guild.get_member(user.id)  # Convert User to Member
        
        if role and member:
            await member.add_roles(role)
            print(f"Assigned {role_name} to {member}")

@client.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return
        
    guild = reaction.message.guild
    if not guild:
        return
        
    if hasattr(client, "colour_role_message_id") and reaction.message.id != client.colour_role_message_id:
        return 
        
    emoji = str(reaction.emoji)
    
    reaction_role_map = {
        '❤️': 'Red',
        '💙': 'Blue',
        '💚': 'Green',
        '💛': 'Yellow',
        '🧡': 'Orange'
    }

    if emoji in reaction_role_map:
        role_name = reaction_role_map[emoji]
        role = discord.utils.get(guild.roles, name=role_name)
        member = guild.get_member(user.id)  # Convert User to Member
        
        if role and member:
            await member.remove_roles(role)
            print(f"Removed {role_name} from {member}")


# ========================================
# Leveling system
# ======================================
# /level command to print XP and Level
@client.command()
async def level(ctx):
    user_id = str(ctx.author.id)
    xp, level = await lvl.print_level(user_id)
    await ctx.send(f"Hello, {ctx.author.name}!\nYour current Level is {level} and Xp is at {xp}")


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

@client.event
async def on_member_remove(member):
    await member.send()


# ==========================
# Music Playback
# ==========================

# For playing audio in voice calls. 
@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} has been kicked.')
    
@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Error: You do not have permission to kick people.")

@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
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
@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")


@client.command()
async def join(ctx):
    """Join the user's current voice channel."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Joined `{channel}`")
    else:
        await ctx.send("You must be in a voice channel to use this.")


@client.command()
async def leave(ctx):
    """Leave the current voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")
    else:
        await ctx.send("I'm not connected to a voice channel.")


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
