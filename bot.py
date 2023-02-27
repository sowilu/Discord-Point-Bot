import discord
import os
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv
import asyncio
from datetime import datetime


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.members = True
intents.typing = True
intents.presences = True
bot = commands.Bot(command_prefix='plz ', intents=intents)


# EVENTS
@bot.event
async def on_ready():
    print(f"I'm in {bot.user}")


@bot.command(brief='waits for specified time and notifies when done',description='waits for specified time and notifies when done. Enter time in seconds, minutes, hours by adding s, m, h after the number. Example: plz wait 5m 20s. Can also be used to wait for a specific time. Example: plz wait 16:30')
async def timer(ctx: Context, *time_args):
    if len(time_args) == 0:
        await ctx.send("Please specify a time")
        return

    seconds, minutes, hours = 0, 0, 0
    for arg in time_args:
        if arg[-1] == 's':
            seconds += int(arg[:-1])
        elif arg[-1] == 'm':
            minutes += int(arg[:-1])
        elif arg[-1] == 'h':
            hours += int(arg[:-1])

    if ":" in time_args[0]:
        now = datetime.now()
        values = time_args[0].split(":")
        target_hours = int(values[0])
        target_minutes = int(values[1])
        hours = target_hours - now.hour
        minutes = target_minutes - now.minute - 1
        seconds = 60 - now.second

    time = seconds + minutes * 60 + hours * 3600
    if time <= 0:
        await ctx.message.add_reaction('👎')
        return

    await ctx.message.add_reaction('👌')
    await asyncio.sleep(time)
    await ctx.send(f'Time is up!🔔', reference=ctx.message)

bot.run(TOKEN)
