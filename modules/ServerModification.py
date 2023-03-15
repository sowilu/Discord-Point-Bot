import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from pathlib import Path
from roles import roles


class ServerModification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Creates channels for given course", description="Creates channels for given course")
    async def prep(self, ctx: Context, course: str = commands.parameter(default="empty", description="python/cs/cpp/unity")):
        if not ctx.author.guild_permissions.administrator:
            await ctx.message.add_reaction('👎')
            return

        category = await ctx.guild.create_category("LECTURES")
        if course == "empty":
            for i in range(1, 37):
                await ctx.guild.create_text_channel(str(i), category=category)

            return

        file_name = "courses\\" + course + ".txt"
        file = Path(file_name)

        if not file.is_file():
            await ctx.message.add_reaction('👎')
            await ctx.message.reply(f"Sorry, I don't seem to have any information about {course}")
            return

        file = open(file_name)

        for index, title in enumerate(file.readlines()):
            await ctx.guild.create_text_channel(f"{index + 1} {title}", category=category)

        await ctx.message.add_reaction('👌')


    @commands.command(brief="Deletes all channels except for the ones given",
                      description="Deletes all channels except for the ones given")
    async def delete_except(self, ctx: Context, *channels: discord.TextChannel):
        if not ctx.author.guild_permissions.administrator:
            await ctx.message.add_reaction('👎')
            return

        #delete all channels except for the ones given
        for channel in ctx.guild.channels:
            if channel not in channels:
                await channel.delete()

        await ctx.message.add_reaction('👌')

    @commands.command(brief="Deletes given channels",
                      description="Deletes given channels")
    async def delete(self, ctx: Context, *channels: discord.TextChannel):
        if not ctx.author.guild_permissions.administrator:
            await ctx.message.add_reaction('👎')
            return

        for channel in ctx.guild.channels:
            if channel in channels:
                await channel.delete()

        await ctx.message.add_reaction('👌')

    @commands.command(brief="Creates private name channels for guild members",
                 description="Creates private name channels for guild members")
    async def add_channels(self, ctx: Context, *members: discord.Member):
        if not ctx.author.guild_permissions.administrator:
            await ctx.message.add_reaction('👎')
            return

        if len(members) == 0:
            members = ctx.guild.members

            # skip accounts that have roles named lecture, admin, administrator or administator or bot roles
            members = [account for account in members if
                        not any(role.name.lower() in ["lecturer", "admin", "administrator", "administator"] for role in
                                account.roles) and not account.bot and not account.guild_permissions.administrator]

        #check if category already exists
        category = discord.utils.get(ctx.guild.categories, name="WORK MONITORING")
        if category == None:
            category = await ctx.guild.create_category("WORK MONITORING")

        for member in members:

            name = member.nick
            if name == None:
                name = member.name

            name = name.lower()

            try:
                #check if name channel already exists in category
                channel = discord.utils.get(ctx.guild.channels, name=name, category=category)

                if channel != None:
                    print(f"Channel {name} already exists")
                    continue

                channel = await ctx.guild.create_text_channel(name, category=category)

                await channel.set_permissions(ctx.guild.default_role, view_channel=False)
                # await channel.set_permissions(ctx.guild.administrator, view_channel = True)
                await channel.set_permissions(member, view_channel=True)

                await channel.send(
                    f"{member.mention} hey, this channel is meant for your class work, homework and tests. Have a fun & productive course!")
            except:
                await ctx.reply(f"Couldn't do it for {member.mention} :(")

        await ctx.message.add_reaction('👌')

    @commands.command(brief="Adds tiers", description="Adds tiers")
    async def add_roles(self, ctx: Context):
        global roles
        if not ctx.author.guild_permissions.administrator:
            await ctx.message.add_reaction('👎')
            return

        for name, data in roles.items():
            await ctx.guild.create_role(name=name, hoist=True, colour=data['color'])
        await ctx.message.add_reaction('👌')

async def setup(bot : commands.Bot):
    await bot.add_cog(ServerModification(bot))