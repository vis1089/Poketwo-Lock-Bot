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
    await tree.sync()
    print(f"Logged in as {bot.user}")

load_dotenv()
TOKEN = os.getenv("TOKEN")

PNAME = 123456789012345678  # Replace with actual user ID
P2A_ID = 987654321098765432  # Replace with actual user ID

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

    await bot.process_commands(message)

# 🔒 LOCK COMMAND (prefix & slash)
@commands.command(aliases=["lc", "lockchannel"])
async def lock(ctx):
    await BotLockView(ctx.channel).lock_channel()
    await ctx.send("Channel locked.")
bot.add_command(lock)

@tree.command(name="lock", description="Lock the channel")
async def slash_lock(interaction: discord.Interaction):
    await BotLockView(interaction.channel).lock_channel()
    await interaction.response.send_message("Channel locked.")

# 🔓 UNLOCK COMMAND (prefix & slash)
@commands.command(aliases=["unc", "unlockchannel"])
async def unlock(ctx):
    await BotLockView(ctx.channel).do_unlock()
    await ctx.send("Channel unlocked.")
bot.add_command(unlock)

@tree.command(name="unlock", description="Unlock the channel")
async def slash_unlock(interaction: discord.Interaction):
    await BotLockView(interaction.channel).do_unlock()
    await interaction.response.send_message("Channel unlocked.")

# 🔐 BotLockView with interactive button
class BotLockView(View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.bot = bot
        self.channel = channel

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.gray)
    async def unlock_button(self, interaction: discord.Interaction, button: Button):
        try:
            await interaction.response.defer()
            await self.do_unlock()
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
        poketwo = self.channel.guild.get_member(716390085896962058)
        if poketwo is None:
            try:
                poketwo = await self.channel.guild.fetch_member(716390085896962058)
            except discord.NotFound:
                await self.channel.send("Pokétwo not found in the guild.")
                return
            except discord.Forbidden:
                await self.channel.send("Error: Missing permission(s)")
                return

        async for msg in self.channel.history(limit=10):
            if msg.author == bot.user and msg.components:
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

    async def do_unlock(self):
        poketwo = self.channel.guild.get_member(716390085896962058)
        if poketwo is None:
            try:
                poketwo = await self.channel.guild.fetch_member(716390085896962058)
            except discord.NotFound:
                await self.channel.send("Pokétwo not found in the guild.")
                return

        try:
            await self.channel.set_permissions(poketwo, view_channel=True, send_messages=True)
            embed = discord.Embed(description="This channel has been unlocked.", color=discord.Color.green())
            await self.channel.send(embed=embed)
        except discord.Forbidden:
            await self.channel.send("Error: Missing permission(s)")

bot.run(TOKEN)
