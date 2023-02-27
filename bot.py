import discord
import os
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.members = True
intents.typing = True
intents.presences = True
bot = commands.Bot(command_prefix='plz ', intents=intents)

#EVENTS
@bot.event
async def on_ready():
    print(f"I'm in {bot.user}")

bot.run(TOKEN)