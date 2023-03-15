import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import asyncio

teams = {}

class TeamWorkDreamWork(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Prepares server for team work", description="Prepares server for team work")
    async def teamwork(self, ctx: Context, title: str, *users: discord.Member):
        global teams

        if not ctx.author.guild_permissions.administrator:
            #add thumbs down reaction
            await ctx.message.add_reaction('👎')
            return

        #lower title
        title = title.lower()

        #check if category teamwork exists
        category = discord.utils.get(ctx.guild.categories, name="Teamwork")
        if category == None:
            category = await ctx.guild.create_category("Teamwork")


        #create channel for teamwork which is only accessible to users
        channel = await ctx.guild.create_text_channel(title, category=category, overwrites={
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True),
        })

        for user in users:
            await channel.set_permissions(user, read_messages=True, send_messages=True)

        #create voice channel which is only accessible to lecture and users
        voice_channel = await ctx.guild.create_voice_channel(title, category=category, overwrites={
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True)
        })
        for user in users:
            await voice_channel.set_permissions(user, view_channel=True, connect=True)


        #check if server not in teams
        if ctx.guild not in teams:
            teams[ctx.guild.id] = {}

        teams[ctx.guild.id][title] = {}
        teams[ctx.guild.id][title]["members"] = users
        teams[ctx.guild.id][title]["points"] = 0

        #add ok reaction
        await ctx.message.add_reaction('👌')

    #command that adds points to specified team
    @commands.command(brief="Adds points to specified team", description="Adds points to specified team")
    async def add_points(self, ctx: Context, channel: discord.TextChannel, points: int):
        global teams

        if not ctx.author.guild_permissions.administrator:
            #add thumbs down reaction
            await ctx.message.add_reaction('👎')
            return

        if ctx.guild.id not in teams:
            teams[ctx.guild.id] = []

        if channel.name not in teams[ctx.guild.id]:
            await ctx.send("Team not found")
            return

        teams[ctx.guild.id][channel.name]["points"] += points

        #add ok reaction
        await ctx.message.add_reaction('👌')


    #command that shows team leaderboard
    @commands.command(brief="Shows team leaderboard", description="Shows team leaderboard")
    async def teamboard(self, ctx: Context):
        global teams

        if ctx.guild.id not in teams:
            await ctx.send("No teams found")
            return

        #sort teams dictionary by points
        items = {}
        for team in teams[ctx.guild.id]:
            items[team] = teams[ctx.guild.id][team]["points"]

        #create message
        message = ""
        for team, points in items.items():
            message += f"{team} - {points} points\n"

        #create cyan discord embed that shows team leaderboard
        embed = discord.Embed(title="Team Leaderboard", description=message, color=0x00FFFF)
        await ctx.send(embed=embed)


async def setup(bot : commands.Bot):
    await bot.add_cog(TeamWorkDreamWork(bot))