import discord, os
from discord.ext import commands
from discord.ui import Button, View
from discord_slash import SlashCommand, SlashContext
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='c!', intents=intents, case_insensitive=True)
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd)
    print(f"✅ {bot.user} is online and ready!")

load_dotenv()
TOKEN = os.getenv("TOKEN")
POKETWO = 716390085896962058
P2A_ID = 854233015475109888
P2A2_ID = 1254602968938844171
PNAME = 874910942490677270

# Load Pokémon names from files
def load_pokemon_list(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        print(f"⚠️ File not found: {filename}")
        return set()

rare_pokemon = load_pokemon_list("rare.txt")
regional_pokemon = load_pokemon_list("regional.txt")
shiny_hunt_pokemon = load_pokemon_list("pokemon.txt")

@bot.event
async def on_message(message):
    if message.author.id in [PNAME, P2A_ID, P2A2_ID]:  
        content = message.content.lower()

        if any(pokemon in content for pokemon in rare_pokemon):
            await lock_channel(message.channel)
        elif any(pokemon in content for pokemon in regional_pokemon):
            await lock_channel(message.channel)
        elif any(pokemon in content for pokemon in shiny_hunt_pokemon):
            await lock_channel(message.channel)
    
    await bot.process_commands(message)

# Slash command for locking the channel
@slash.slash(name="lock", description="Lock the channel to pause Pokémon spawns.")
async def lock_slash(ctx: SlashContext):
    await lock_channel(ctx.channel)
    await ctx.send("🔒 Channel has been locked.", hidden=True)

# Slash command for unlocking the channel
@slash.slash(name="unlock", description="Unlock the channel to resume Pokémon spawns.")
async def unlock_slash(ctx: SlashContext):
    await unlock_channel(ctx.channel)
    await ctx.send("🔓 Channel has been unlocked.", hidden=True)

# Aliases for locking/unlocking (secondary commands)
@bot.command(aliases=["lock_channel", "lc", "lockchannel"])
async def lock(ctx):
    await lock_channel(ctx.channel)

@bot.command(aliases=["unlock_channel", "unc", "unlockchannel"])
async def unlock(ctx):
    await unlock_channel(ctx.channel)

async def lock_channel(channel):
    poketwo = channel.guild.get_member(POKETWO)
    if poketwo is None:
        try:
            poketwo = await channel.guild.fetch_member(POKETWO)
        except discord.NotFound:
            await channel.send("Pokétwo not found in the guild.")
            return
        except discord.Forbidden:
            await channel.send("Error: Missing permission(s)")
            return

    try:
        # Restrict only embedded messages
        await channel.set_permissions(poketwo, embed_links=False)
        embed = discord.Embed(
            title="🔒 Locked",
            description="Paused spawns",
            color=discord.Color.red()
        )
        await channel.send(embed=embed, view=LockView(channel))
    except discord.Forbidden:
        await channel.send("Error: Missing permission(s)")

async def unlock_channel(channel):
    poketwo = channel.guild.get_member(POKETWO)
    if poketwo is None:
        try:
            poketwo = await channel.guild.fetch_member(POKETWO)
        except discord.NotFound:
            await channel.send("Pokétwo not found in the guild.")
            return

    overwrites = channel.overwrites_for(poketwo)

    # Check if Pokétwo is already unrestricted
    if overwrites.embed_links is None or overwrites.embed_links is True:
        await channel.send("🔓 Pokétwo **already has permission** to send embeds.")
        return

    try:
        # Restore embed permissions
        await channel.set_permissions(poketwo, embed_links=None)  # Reset to default
        embed = discord.Embed(
            title="🔓 Unlocked",
            description="Spawns Resumed.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed, view=UnlockView(channel))
    except discord.Forbidden:
        await channel.send("Error: Missing permission(s)")

class LockView(View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.blurple)
    async def unlock_button(self, interaction: discord.Interaction, button: Button):
        try:
            await unlock_channel(self.channel)
            await interaction.response.send_message(f"🔓 Channel unlocked by {interaction.user.mention}.", ephemeral=False)
            button.disabled = True
            await interaction.message.edit(view=self)
        except discord.Forbidden:
            await interaction.response.send_message("Error: Missing permission(s)", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to unlock the channel: {e}", ephemeral=True)

class UnlockView(View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.green)
    async def lock_button(self, interaction: discord.Interaction, button: Button):
        try:
            await lock_channel(self.channel)
            await interaction.response.send_message(f"🔒 Channel locked by {interaction.user.mention}.", ephemeral=False)
            button.disabled = True
            await interaction.message.edit(view=self)
        except discord.Forbidden:
            await interaction.response.send_message("Error: Missing permission(s)", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to lock the channel: {e}", ephemeral=True)

bot.run(TOKEN)
