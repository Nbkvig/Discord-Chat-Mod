# moderation.py
#
# provides spam tools, mention spam tools, and bad word checks. 
#
import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

GUILD_ID = discord.Object(id=1415377687526248582)


class moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        # SPAM: Allow 5 messages per 15 seconds per member
        self.anti_spam = commands.CooldownMapping.from_cooldown(5, 15, commands.BucketType.member)
        # SPAM Track violations: 3 violations in 60 seconds triggers action
        self.too_many_violations = commands.CooldownMapping.from_cooldown(3, 60, commands.BucketType.member)

        # MENTIONS Track violations: 3 violations in 5 seconds
        self.anti_mention_spam = commands.CooldownMapping.from_cooldown(3, 10, commands.BucketType.member)
        # MENTIONS Track violations, 3 violations in 120 seconds triggers a cooldown. 
        self.mention_violations = commands.CooldownMapping.from_cooldown(2, 120, commands.BucketType.member)
        
        # data structure for bad words
        self.bad_words = None
        
        # init on start
        self.load_bad_words()
        
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[moderation.py] Moderation cog initiated.')


# =================================
# Bad language check
# =================================    


    # load_bad_words()
    #
    # This will take a txt document in /data and will check messages to see if something bad is being said.
    # Its not really important for me to write a whole bunch of bad words into a document, so instead I am 
    # just going to link repos that have already done this. 
    #
    # https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words
    # https://github.com/MauriceButler/badwords
    #
    # Using a .txt file due to time constraints. Ideally would use SQL, but then would have to add protections
    # against SQL injections and other methods of attack. Using a txt file should be fine for the small scale of
    # the project. 
    #
    def load_bad_words(self):
        try:
            bad_words = []
            with open('data/bad_words.txt', 'r', encoding='utf-8') as f:
                bad_words = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith('#')
                ]

            if bad_words:
                self.bad_words = [word.lower() for word in bad_words]
                print(f"[moderation.py] loaded {len(self.bad_words)} from bad_words.txt")
            else:
                self.bad_words = []
                print(f"[moderation.py] Warning: /data/bad_words.txt is empty.")
        
        except FileNotFoundError: 
            print(f"[moderation.py] Warning: /data/bad_words.txt not found. Creating a new file in /data/.")
            self.bad_words = []
            template = "# List"

            with open('data/bad_words.txt', 'w', encoding='utf-8') as f:
                f.write(template)
    

    # check_bad_words
    #
    # Cecks if a certain phrase is used.
    #
    async def check_bad_words(self, message):
        if not self.bad_words:
            return
        
        msglower = message.content.lower()

        # checks for substrings containing the bad word. 
        for bad_word in self.bad_words:
            if bad_word in msglower:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, please use kinder language.", delete_after=10)
                return
            

    # mkword()
    #
    # Make word. Adds a word to the dictionary.
    #
    @app_commands.command(name="mkword", description="Add a bad word to the dictionary")
    @app_commands.guilds(GUILD_ID)
    async def mkword(self, interaction: discord.Interaction, word: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("This command requires admin permissions.", ephemeral=True)
            return
        
        if not self.bad_words: 
            self.bad_words = []

        word_lower = word.lower()
        if word_lower not in self.bad_words:
            self.bad_words.append(word_lower)

        with open('data/bad_words.txt', 'a', encoding='utf-8') as f:
            f.write(f"{word}\n")

        await interaction.response.send_message(f"Success! Your bad word has been added to the dictionary!", ephemeral=True)


    # rmword()
    #
    # removes a word from the dictionary
    #
    @app_commands.command(name="rmword", description="Remove a bad word from the dictionary")
    @app_commands.guilds(GUILD_ID)
    async def rmword(self, interaction: discord.Interaction, word: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("This command requires admin permissions.", ephemeral=True)
            return
        
        if not self.bad_words:
            await  interaction.response.send_message("Uh oh! The dictionary is empty!", ephemeral=True)
            return
        
        word_lower = word.lower()

        if word_lower not in self.bad_words:
            await interaction.response.send_message(f"Uh oh! This word isn't in the dictionary!", ephemeral=True)
            return
        
        self.bad_words.remove(word_lower)
        
        with open('data/bad_words.txt', 'w', encoding='utf-8') as f:
            f.write("# Bad words\n")
            for w in self.bad_words:
                f.write(f"{w}\n")
            
        await interaction.response.send_message(f"Success! Your bad word has been removed from the dictionary!", ephemeral=True)


# =================================
# Spam Checks
# =================================    

    # check_rate_spam()
    #
    # checks how often someone is sending messages, and tells them to slow down in chat. 
    # after exceeding enough warnings, they are timed out for a bit. 
    #
    async def check_rate_spam(self, message):
        # Check if message exceeds rate limit
        bucket = self.anti_spam.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        
        if retry_after:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, stop spamming!", delete_after=5)
            
            # Track violations
            violations_bucket = self.too_many_violations.get_bucket(message)
            violations_check = violations_bucket.update_rate_limit()
            
            if violations_check:

                await message.author.timeout(timedelta(minutes = 1), reason = "Spamming")

                # Too many violations - could timeout/kick/ban here
                await message.channel.send(
                    f"{message.author.mention} has been warned for excessive spam violations!", delete_after=10)


    # check_mention_spam()
    #
    # this checks how often someone is sending @everyone or @here. 
    # its pretty common for discord accounts to be hijacked and spamming mentions to get people
    # to click on fishy links. This function aims to prevent that from happening. 
    #
    async def check_mention_spam(self, message):
        # Check how many times someone sends @everyone
        if not (message.mention_everyone or '@everyone' in message.content or '@here' in message.content):
            return
        
        mention_bucket = self.anti_mention_spam.get_bucket(message)
        retry_after = mention_bucket.update_rate_limit()

        if retry_after:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, stop spamming @everyone/@here!", delete_after=5)

            violations_bucket = self.mention_violations.get_bucket(message)
            violations_check = violations_bucket.update_rate_limit()


            # muting a hijacked account prevents people from using it to scam people.
            if violations_check:
               for channel in message.guild.text_channels:
                   await channel.set_permissions(message.author, send_messages=False, reason="Spamming @everyone/@here, possible compromised account?")
            await message.channel.send(f"{message.author.mention} has been muted for spamming mass mentions. Contact an admin for reinstatement.")
    

    # check_spam()
    #
    # I just call all the individual functions here in order. 
    # Each function should be able to work independently if called elsewhere too.
    #
    # on_message can be called multiple times in the discord file. I've written it here
    # to keep it modular. This can be removed and reimplemented in main.py so that we can 
    # check spam BEFORE entering things into the leveling database. 
    #
    @commands.Cog.listener('on_message')
    async def check_if_message_is_bad(self, message):
        # Ignore DMs and bot messages
        if not isinstance(message.channel, discord.TextChannel) or message.author.bot:
            return
        
        await self.check_rate_spam(message)

        await self.check_mention_spam(message)

        await self.check_bad_words(message)


async def setup(client):
    await client.add_cog(moderation(client))
