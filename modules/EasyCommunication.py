from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import asyncio

class EasyCommunication(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.command(brief='waits for specified time and notifies when done',
                 description='waits for specified time and notifies when done. Enter time in seconds, minutes, hours by adding s, m, h after the number. Example: plz wait 5m 20s. Can also be used to wait for a specific time. Example: plz wait 16:30')
    async def timer(this, ctx: Context, *time_args):
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


    @commands.command(brief="Creates a poll", description="Creates a poll")
    async def poll(self, ctx: Context, question, *options):
        await ctx.message.delete()
        yes_no = ['👍', '👎']
        more = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        description = []
        emojis = []

        if (len(options) == 0):
            emojis = yes_no
            embed = discord.Embed(title=question, description='\n'.join(description), color=0xFF5733)
        else:
            emojis = more[:len(options)]

            for index in range(len(options)):
                description.append(f'{emojis[index]} {options[index]}')

            embed = discord.Embed(title=question, description='\n'.join(description), color=0xFF5733)

        message = await ctx.send(embed=embed)

        for emoji in emojis:
            await message.add_reaction(emoji)

    @commands.command(brief="Creates a rate this lecture message", description="Creates a rate this lecture message")
    async def rate(self, ctx: Context, title: str = ""):
        if not ctx.author.guild_permissions.administrator:
            await ctx.message.add_reaction('👎')
            return

        await ctx.message.delete()

        if title == "":
            # get channel name
            title = ctx.channel.name

        title = title.upper()

        emojis = ['😥', '😐', '🙂', '😎']

        embed = discord.Embed(title=f"Was {title} easy?", color=0xffff00)
        message = await ctx.send(embed=embed)

        for emoji in emojis:
            await message.add_reaction(emoji)

        embed.title = f"Was {title} interesting?"
        message = await ctx.send(embed=embed)

        for emoji in emojis:
            await message.add_reaction(emoji)

async def setup(bot : commands.Bot):
    await bot.add_cog(EasyCommunication(bot))