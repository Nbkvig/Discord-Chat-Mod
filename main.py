import os
import discord
import flask_app
import leveling_sys as lvl
from threading import Thread
from flask import Flask, request, jsonify, render_template
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv 


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

client.run(TOKEN)