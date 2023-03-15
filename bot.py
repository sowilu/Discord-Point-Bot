import random
import os
from discord.ext import commands
from dotenv import load_dotenv
from utilities import *


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.members = True
intents.typing = True
intents.presences = True
bot = commands.Bot(command_prefix='dw ', intents=intents)

@bot.event
async def on_ready():
    print(f"I'm in {bot.user}")

    # import cogs
    for filename in os.listdir('modules'):
        if filename.endswith('.py'):
            await bot.load_extension(f'modules.{filename[:-3]}')

    await bot.change_presence(activity=discord.Game(random.choice(games)))

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    global monitor, test_shops, test_orders

    if payload.member == bot.user:
        return

    #if message id in test_shops keys
    if payload.message_id in test_shops:

        guild = await bot.fetch_guild(payload.guild_id)
        user = await guild.fetch_member(payload.user_id)
        id = -1

        #if emoji is 1️⃣
        if payload.emoji.name == "1️⃣":
            id = 0
        elif payload.emoji.name == "2️⃣":
            id = 1
            #, '', '4️⃣', '5️⃣', '6️⃣":
        elif payload.emoji.name == "3️⃣":
            id = 2
        elif payload.emoji.name == "4️⃣":
            id = 3
        elif payload.emoji.name == "5️⃣":
            id = 4
        elif payload.emoji.name == "6️⃣":
            id = 5

        #get channel in which message is
        channel = bot.get_channel(payload.channel_id)

        #get server name
        guild = await bot.fetch_guild(payload.guild_id)

        #send dm to a person who bought something
        await user.send(buy(guild, user, id))

        return

    if not payload.member.guild_permissions.administrator:
        return
    
    guild = await bot.fetch_guild(payload.guild_id)
    if guild.name not in monitor:
        return
    
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    
    file_name = guild.name.replace(' ', '_') + '.json'

    #add reaction to message
    await message.add_reaction("✅")

    await add_points(file_name, monitor[guild.name], [message.author])

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from bots

    if message.author.guild_permissions.administrator:

        if message.content[0:2] == "dw" or message.content[0:2] == "``":
            await bot.process_commands(message)
            return

        #lang = get_code_language(message.content)
        if message.content[0:2] == "py":
            #print(lang)
            new_content = f"```py\n{message.content[2:]}```"
            await message.channel.send(new_content)
            await message.delete()


    await bot.process_commands(message)

bot.run(TOKEN)