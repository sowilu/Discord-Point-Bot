import statistics

import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import roles
from utilities import *

class PointSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Shows all tears and scores needed to reach them",
                 description="Shows all tears and scores needed to reach them")
    async def tiers(self, ctx: Context):
        # combine tier name and score into string
        text = ""
        for role in roles:
            text += f"{role} - {roles[role]['score']} points\n"

        # send text as discord embed
        embed = discord.Embed(title="Tiers", description=text, color=0x00ff00)
        await ctx.reply(embed=embed)

    @commands.command(brief="Shows order", description="Shows orders")
    async def orders(self, ctx: Context):
        global test_orders

        if not ctx.author.guild_permissions.administrator:
            await ctx.message.add_reaction('👎')
            return

        # get orders for current server
        orders = test_orders[ctx.guild.id]

        # combine orders into string
        text = ""
        for user, ids in orders.items():
            print(ids)
            text += f"**{user}**:\n"
            sum = 0
            for id in ids:
                sum += shop[id]['server_scores'][ctx.guild.id]
                text += f"\t{shop[id]['title']} - {shop[id]['server_scores'][ctx.guild.id]} points\n"
            text += f"*Total: {sum} points*\n"

        # send text as discord embed
        embed = discord.Embed(title="Orders", description=text, color=0x00ff00)
        await ctx.reply(embed=embed)

    @commands.command(brief="Shows shop", description="Shows shop")
    async def shop(self, ctx: Context):
        global shop, test_shops

        file_name = ctx.guild.name.replace(' ', '_') + '.json';
        students = read(file_name)

        # find min, max and median score
        scores = [student['score'] for student in students.values()]
        min_score = min(scores)
        max_score = max(scores)
        median_score = statistics.median(scores)

        # send message with min, max median info
        embed = discord.Embed(title='Shop')


        #calculate server prices
        shop[0]['server_scores'][ctx.guild.id] = max(scores[-3], shop[0]["score_min"])
        shop[1]['server_scores'][ctx.guild.id] =  max(median_score, shop[0]["score_min"])
        shop[2]['server_scores'][ctx.guild.id] =  max(median_score + 20, shop[0]["score_min"])
        shop[3]['server_scores'][ctx.guild.id] =  max(median_score + 60, shop[0]["score_min"])
        shop[4]['server_scores'][ctx.guild.id] =  max(median_score * 2, shop[0]["score_min"])
        shop[5]['server_scores'][ctx.guild.id] =  max((max_score - min_score) // 2, shop[0]["score_min"])


        #add fields from shop: title & server price
        for i in range(len(shop)):
            embed.add_field(name= f"{i+1}. {shop[i]['title']}", value=f"{shop[i]['server_scores'][ctx.guild.id]} points", inline=False)

        #send message
        message = await ctx.reply(embed=embed)

        # if user who called is admin
        if not ctx.author.guild_permissions.administrator:
            return

        #add message id to test shops
        test_shops.append(message.id)

        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']

        for emoji in emojis:
            await message.add_reaction(emoji)

    @commands.command(brief="Start monitoring for admin reactions",
                 description="Start monitoring process, every post with reaction from admin gets points")
    async def start(self, ctx: Context, score: int = 10):
        global monitor

        if not ctx.author.guild_permissions.administrator:
            await ctx.message.add_reaction('👎')
            return

        monitor[ctx.guild.name] = score
        await ctx.message.add_reaction('👌')

    @commands.command(bried="Stop monitoring for admin reactions", description="Stop monitoring process")
    async def stop(self, ctx: Context):
        global monitor

        if not ctx.author.guild_permissions.administrator:
            await ctx.message.add_reaction('👎')
            return

        monitor.pop(ctx.guild.name)
        await ctx.message.add_reaction('👌')

    @commands.command(brief="Adds points to user(s)", description="Adds points to user(s)")
    async def add(self, ctx: Context, score: int, *accounts: discord.Member):
        if not ctx.author.guild_permissions.administrator:
            await ctx.message.add_reaction('👎')
            return

        file_name = ctx.guild.name.replace(' ', '_') + '.json';
        try:
            if len(accounts) == 0:
                print("Tried to get accounts")
                accounts = ctx.guild.members

                #skip accounts that have roles named lecture, admin, administrator or administator or bot roles
                accounts = [account for account in accounts if
                            not any(role.name.lower() in ["lecture", "admin", "administrator", "administator"] for role in
                                    account.roles) and not account.bot and not account.guild_permissions.administrator]

                # remove accounts that are admin or bot
                accounts = [account for account in accounts if
                            not account.guild_permissions.administrator and not account.bot]

            await add_points(file_name, score, accounts)
            await ctx.message.add_reaction('👌')



        except Exception as e:
            await ctx.message.add_reaction('👎')
            print(e)
            await ctx.reply("Sorry boss no can do, check my log :(")

    @commands.command(brief="Gets point history of a user", description="Gets point history of a user")
    async def score(self, ctx: Context, user: discord.User):
        file_name = ctx.guild.name.replace(' ', '_') + '.json';
        students = read(file_name)

        if user.name in students:
            embed = discord.Embed()
            embed.title = "Score log"
            embed.description = "\n".join(students[user.name]["entries"])

            await ctx.reply(embed=embed)
        else:
            await ctx.reply(f"I don't know anyone named {user.name}")

    @commands.command(brief="Shows leaderboard", description="Shows leaderboard")
    async def leaderboard(self, ctx: Context, _global=False):
        file_name = ctx.guild.name.replace(' ', '_') + '.json';
        students = {}

        if not _global:
            students = read(file_name)
        else:
            for file_name in Path('').glob('*.json'):
                students.update(read(file_name))

        if students == {}:
            await ctx.reply("No data for leaderboard yet")
            return

        tearlist = []
        for name, data in students.items():
            if data['nick'] != None:
                tearlist.append({'name': data['nick'], 'total': data['total'], 'current': data['score']})
            else:
                tearlist.append({'name': name, 'total': data['total'], 'current': data['score']})

        tearlist = sorted(tearlist, key=lambda d: d['total'])
        tearlist.reverse()
        # print(tearlist)

        #create embed
        embed = discord.Embed()
        #go thru tier list add and students place, name, total score and current score
        for i, student in enumerate(tearlist):
            embed.add_field(name=f"{i + 1}. {student['name']}", value=f"Total: {student['total']}, Current: {student['current']}", inline=False)


        try:

            #check if channel named leaderboard exists
            leaderboard_channel = discord.utils.get(ctx.guild.channels, name='leaderboard')
            if leaderboard_channel == None:
                #create leaderboard channel where users can see messages but cant write anything
                leaderboard_channel = await ctx.guild.create_text_channel('leaderboard', overwrites={
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                })


            #delete all messages in channel
            await leaderboard_channel.purge(limit=100)

            #send leaderboard
            await leaderboard_channel.send(embed=embed)

            #tag person who called command in leaderboard channel
            tag = await leaderboard_channel.send(ctx.author.mention)

            #add ok emoji
            await ctx.message.add_reaction('👌')

            #delete tag in 5 seconds
            await asyncio.sleep(5)
            await tag.delete()

            #delete command message
            if ctx.channel != leaderboard_channel:
                await ctx.message.delete()

        except Exception as e:
            print(e)

            #add thumbs down emoji
            await ctx.message.add_reaction('👎')

            await asyncio.sleep(5)
            await ctx.message.delete()

async def setup(bot : commands.Bot):
    await bot.add_cog(PointSystem(bot))