import discord, os, random
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
from discord import app_commands

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='c!', intents=intents, case_insensitive=True)
tree = bot.tree  # Slash command tree

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd)
    await tree.sync()  # Sync slash commands when the bot is ready
    print(f"Logged in as {bot.user}")

load_dotenv()
TOKEN = os.getenv("TOKEN")

PNAME = 123456789012345678  # Replace with the actual user ID
P2A_ID = 987654321098765432  # Replace with the actual user ID

# Event listener for on_message
@bot.event
async def on_message(message):
    if message.author.id == PNAME:
        keywords_p1 = ['**Rare Ping:**', '**✨ Shiny Hunt Pings:**', '**Regional Ping:**']
        if any(keyword.lower() in message.content.lower() for keyword in keywords_p1):
            await BotLockView(message.channel).lock_channel()
    elif message.author.id == P2A_ID:
        keywords_p2 = ['Rare ping:', 'Regional ping:', 'Shiny hunt pings:']
        if any(keyword.lower() in message.content.lower() for keyword in keywords_p2):
            await BotLockView(message.channel).lock_channel()

    # Process other commands
    await bot.process_commands(message)

# Slash Command for locking a channel
@tree.command(name="lock", description="Lock the channel")
async def lock(interaction: discord.Interaction):
    await BotLockView(interaction.channel).lock_channel()
    await interaction.response.send_message("Channel locked.")

# Alias slash command for lock (lc)
@tree.command(name="lc", description="Alias for lock")
async def lc(interaction: discord.Interaction):
    await lock(interaction)

# Slash Command for unlocking a channel
@tree.command(name="unlock", description="Unlock the channel")
async def unlock(interaction: discord.Interaction):
    await BotLockView(interaction.channel).unlock_channel()
    await interaction.response.send_message("Channel unlocked.")

# Alias slash command for unlock (unc)
@tree.command(name="unc", description="Alias for unlock")
async def unc(interaction: discord.Interaction):
    await unlock(interaction)

# Prefix-based command (c!) for locking a channel
@bot.command(aliases=["lc", "lockchannel"])
async def lock_channel(ctx):
    await BotLockView(ctx.channel).lock_channel()
    await ctx.send("Channel locked.")

# Prefix-based command (c!) for unlocking a channel
@bot.command(aliases=["unc", "unlockchannel"])
async def unlock_channel(ctx):
    await BotLockView(ctx.channel).unlock_channel()
    await ctx.send("Channel unlocked.")

class BotLockView(View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.bot = bot
        self.channel = channel

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.gray)
    async def unlock_button(self, interaction: discord.Interaction, button: Button):
        try:
            await interaction.response.defer()
            await self.unlock_channel()
            await interaction.followup.send(f"Channel unlocked by {interaction.user.mention}.", ephemeral=False)
            
            button.disabled = True
            await interaction.message.edit(view=self)
        except discord.errors.InteractionResponded:
            pass
        except discord.Forbidden:
            await interaction.followup.send("Error: Missing permission(s)", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Failed to unlock the channel: {e}", ephemeral=True)

    async def lock_channel(self):
        poketwo = self.channel.guild.get_member(716390085896962058)  # Replace with correct ID
        if poketwo is None:
            try:
                poketwo = await self.channel.guild.fetch_member(716390085896962058)
            except discord.NotFound:
                await self.channel.send("Pokétwo not found in the guild.")
                return
            except discord.Forbidden:
                await self.channel.send("Error: Missing permission(s)")
                return

        overwrites = self.channel.overwrites_for(poketwo)
        if overwrites.view_channel is None or overwrites.view_channel:
            try:
                await self.channel.set_permissions(poketwo, view_channel=False, send_messages=False)
                color = discord.Color(random.randint(0, 0xFFFFFF))
                embed = discord.Embed(description="This channel is locked.", color=color)
                await self.channel.send(embed=embed, view=self)
            except discord.Forbidden:
                await self.channel.send("Error: Missing permission(s)")

    async def unlock_channel(self):
        try:
            await unlock_channel(self.channel)
        except discord.Forbidden:
            await self.channel.send("Error: Missing permission(s)")

async def unlock_channel(channel):
    poketwo = channel.guild.get_member(716390085896962058)
    if poketwo is None:
        try:
            poketwo = await channel.guild.fetch_member(716390085896962058)
        except discord.NotFound:
            await channel.send("Pokétwo not found in the guild.")
            return

    overwrites = channel.overwrites_for(poketwo)
    if overwrites.view_channel is None or overwrites.view_channel:
        await channel.set_permissions(poketwo, view_channel=True, send_messages=True)
        await channel.send("Channel is already unlocked.")
    else:
        await channel.set_permissions(poketwo, view_channel=True, send_messages=True)
        await channel.send("Channel has been unlocked.")

bot.run(TOKEN)
