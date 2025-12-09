# reaction_roles.py
# 
# Allows for users to configure emoji reactions to allow for roles to be added.
# Can use either the bot to message via embed or an existing user message.
#
import discord
from discord import app_commands
from discord.ext import commands
import json
import os


class reaction_roles(commands.Cog):
    def __init__(self, client):
        self.client = client

        if not hasattr(self.client, 'reaction_role_messages'):
            self.client.reaction_role_messages = {}

        self.load_reaction_roles()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[reaction_roles.py] Reaction Roles initiated.")


# =================================
# Storing Reaction Messages
# =================================

    # save_reaction_roles
    def save_reaction_roles(self):

        try:

            with open('data/reaction_roles.json', 'w') as f:
                json.dump(self.client.reaction_role_messages, f, indent=4)
            
            print(f"[reaction_roles.py] Storing Reaction Roles")
        

        except Exception as e:
            print(f"[reaction_roles.py] Error storing reaction roles: {e}")

    def load_reaction_roles(self):

        if os.path.exists('data/reaction_roles.json'):
            try:
                with open('data/reaction_roles.json', 'r') as f:
                    data = json.load(f)

                    # Not at all familiar with json and how it works. Copied this from stack overflow. 
                    self.client.reaction_role_messages = {int(k): v for k, v in data.items()}
                print(f"[reaction_roles.py] Loaded {len(self.client.reaction_role_messages)} reaction role messages")
            
            except Exception as e:
                print(f"[reaction_roles.py] Error loading reaction roles: {e}")
                self.client.reaction_role_messages = {}
        else:
            print("[reaction_roles.py] No reaction_roles.json")


# =================================
# Creating Embed + Adding Reactions
# =================================    

    # reaction_role()
    # 
    # embeds a message and stores reaction emojis in a json file. 
    #
    @app_commands.command(name="reactionrole", description="Create a custom roles embed")
    @app_commands.describe(
        title="Title of the embed",
        description="Description text for the embed"
    )
    async def reaction_role(self, interaction: discord.Interaction, title: str, description: str):
        # Check if the user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("This command requires admin permissions.", ephemeral=True)
            return
        
        # Discord requires something to respond within three seconds of it being called. 
        # There's not really a way to make any of this quicker. This ephermeral stops discord
        # from stopping a function before it completes
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(title=title, description=description, color=discord.Color.blurple())
        message = await interaction.channel.send(embed=embed)

        self.client.reaction_role_messages[message.id] = {}
        self.save_reaction_roles()

        await interaction.followup.send(
            f"Reaction role message created!\n"
            f"Message ID: `{message.id}`\n\n"
            f"Now use `/addrole {message.id}` to add emoji-role pairs.",
            ephemeral=True
        )

    # add_role
    #
    # I configured this so that you can add and remove reactions from both bot and user messages. 
    # You can use either the bot embed, or a user message. Use a bot embed for something permanent (i.e. colors)
    # and use this one for something temporary (games, attending events, etc.)
    #
    @app_commands.command(name="addrole", description="Add an emoji-role pair to a reaction role message")
    @app_commands.describe(
        message_id="The ID of the reaction role message",
        emoji="The emoji to use",
        role="The role to assign"
    )
    async def add_role(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        
        # Checks if the user is an admin 
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("This command requires admin permissions.", ephemeral=True)
            return
        
        try:
            msg_id = int(message_id)

            try:            
                message = await interaction.channel.fetch_message(msg_id)
            
            # Wrong channel 
            except discord.NotFound:
                await interaction.response.send_message("Message could not be found in this channel. Ensure that you are running this comamnd in the same channel as your reaction roles message.", ephemeral=True)
                return
            
            await message.add_reaction(emoji)

            if msg_id not in self.client.reaction_role_messages:
                self.client.reaction_role_messages[msg_id] = {}

            self.client.reaction_role_messages[msg_id][emoji] = role.name
            self.save_reaction_roles()

            await interaction.response.send_message(f"Successfully added {emoji} -> {role.mention}", ephemeral=True)

        # Wrong message ID
        except ValueError:
            await interaction.response.send_message("Message ID invalid. Check the message ID of your reaction message and try again.", ephemeral=True)
        
        # Permissions Error ( This should never run on my bot. If you are using this source code, make sure your bot has admin priveleges in the discord dev portal. )
        except discord.Forbidden:
            await interaction.response.send_message("ERROR: Bot does not have permissions to add reactions.", ephemeral=True)
        
        # Unknown
        except Exception as e:
            await interaction.response.send_message(f"ERROR: Unknown error occured: {str(e)}", ephemeral=True)

# =================================
# Add / Remove Roles
# =================================    
    #
    # Had to switch to raw reactions to make this work when the bot turns off and on again. 
    # 
    # In order to use the raw reactions, I have to use the payload data type.
    # Documentation of the data structure is here
    # https://discord.com/developers/docs/topics/rpc#payloads
    #
    
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        
        # Checks if the user is a bot or itself
        if payload.user_id == self.client.user.id:
            return
        
        # Checks if the message is a dm
        guild = self.client.get_guild(payload.guild_id)
        if not guild:
            return
        
        # Checks to see if this object has this method. If not, it'll escape early. 
        # this shouldn't trigger unless you're messing with the file. 
        if not hasattr(self.client, "reaction_role_messages"):
            print(f"[reaction_roles.py] hasattr failed in on_raw_reaction_add(). Check program for logic errors and/or restart the bot")
            return
        
        if payload.message_id not in self.client.reaction_role_messages:
            return
            
        emoji = str(payload.emoji)
        reaction_role_map = self.client.reaction_role_messages[payload.message_id]

        if emoji in reaction_role_map:
            role_name = reaction_role_map[emoji]
            role = discord.utils.get(guild.roles, name=role_name)
            member = guild.get_member(payload.user_id)

            if role and member:
                await member.add_roles(role)
                print(f'[reaction_roles.py] Assigned {role.name} to {member}')

    #
    # on_raw_reaction_remomve
    #   
    # All the early escapes are the exact same as on_raw_reaction_add
    # 

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        
        if payload.user_id == self.client.user.id:
            return
            
        guild = self.client.get_guild(payload.guild_id)
        if not guild:
            return
        
        if not hasattr(self.client, 'reaction_role_messages'):
            print(f"[reaction_roles.py] hasattr failed in on_raw_reaction_remove(). Check program for logic errors and/or restart the bot")
            return 
        
        if payload.message_id not in self.client.reaction_role_messages:
            return
            
        emoji = str(payload.emoji)
        reaction_role_map = self.client.reaction_role_messages[payload.message_id]

        if emoji in reaction_role_map:
            role_name = reaction_role_map[emoji]
            role = discord.utils.get(guild.roles, name=role_name)
            member = guild.get_member(payload.user_id)
            
            if role and member:
                await member.remove_roles(role)
                print(f"[reaction_roles.py] Removed {role_name} from {member}")

async def setup(client):
    await client.add_cog(reaction_roles(client))
