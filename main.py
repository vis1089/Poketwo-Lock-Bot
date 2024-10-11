import discord, os, random
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='c!', intents=intents, case_insensitive=True)
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd)
load_dotenv()
TOKEN = os.getenv("TOKEN")
POKETWO = 716390085896962058
P2A_ID = 854233015475109888 
PNAME = 874910942490677270

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

@bot.command(aliases=["lock_channel", "lc", "lockchannel"])
async def lock(ctx):
    await BotLockView(ctx.channel).lock_channel()

@bot.command(aliases=["unlock_channel", "unc", "unlockchannel"])
async def unlock(ctx):
    await BotLockView(ctx.channel).unlock_channel()

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
        poketwo = self.channel.guild.get_member(POKETWO)
        if poketwo is None:
            try:
                poketwo = await self.channel.guild.fetch_member(POKETWO)
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
    poketwo = channel.guild.get_member(POKETWO)
    if poketwo is None:
        try:
            poketwo = await channel.guild.fetch_member(POKETWO)
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
