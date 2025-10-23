# reaction_roles.py
import discord
from discord import app_commands
from discord.ext import commands

GUILD_ID = discord.Object(id=1415377687526248582)

class reaction_roles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Reaction Roles initiated.")
    

    @app_commands.command(name="colourroles", description="custom roles")
    @app_commands.guilds(1415377687526248582)
    async def colour_roles(self, interaction: discord.Interaction):
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

        interaction.client.colour_role_message_id = message.id

        await interaction.followup.send("Colour role message created!", ephemeral=True)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        
        guild = reaction.message.guild
        if not guild:
            return
            
        if hasattr(self.client, "colour_role_message_id") and reaction.message.id != self.client.colour_role_message_id:
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

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
            
        guild = reaction.message.guild
        if not guild:
            return
            
        if hasattr(self.client, "colour_role_message_id") and reaction.message.id != self.client.colour_role_message_id:
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

async def setup(client):
    await client.add_cog(reaction_roles(client), guild=GUILD_ID)