from discord.ext import commands
from discord.ext.commands.context import Context
import asyncio
import requests
import random
import math

class FunAndGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="gives a funny joke", description="gives a funny joke")
    async def joke(self, ctx: Context):
        result = requests.get("https://v2.jokeapi.dev/joke/Any?safe-mode")

        if result.status_code != 200:
            await ctx.reply("Sorry, I'm not feeling very funny today")
            return

        result = result.json()

        # check if type is two part
        if result["type"] == "twopart":
            # send setup
            joke = await ctx.reply(result["setup"])

            # simulate typing
            async with ctx.typing():
                await asyncio.sleep(3)

            # send delivery
            await joke.reply(result["delivery"])
        else:
            await ctx.reply(result["joke"])

    @commands.command(brief="gives a dad joke", description="gives a dad joke")
    async def dadjoke(self, ctx):
        api_url = 'https://icanhazdadjoke.com/'
        response = requests.get(api_url, headers={'Accept': 'application/json'})

        if response.status_code != 200:
            await ctx.reply("Sorry, I'm not feeling very funny today")
            return

        result = response.json()

        await ctx.send(result['joke'])

    @commands.command(brief="Roll a game die", description="Returns a random die roll dependent on given count of sides")
    async def roll(self, ctx: Context, die_sides=6):
        await ctx.reply(f":game_die: {random.randint(1, die_sides)} ")

    @commands.command(brief="Gets random activity", description="Gets random activity from boredapi")
    async def activity(self, ctx: Context):
        api_url = f'https://www.boredapi.com/api/activity/'
        price = []
        response = requests.get(api_url, headers={'Accept': 'application/json'})

        if response.status_code != 200:
            await ctx.reply("Sorry, I don't know what to do today")
            return

        result = response.json()

        text = f"**{result['activity']}**\n*Participants:* {result['participants']}\n"

        if result['price'] == 0:
            text += f"*Price:* :free:\n"
        else:
            emoji = ":coin: "
            price = math.ceil(result['price'] * 10)
            text += f"*Price:* {emoji * price}\n"
        if result['link'] != "":
            text += f"*Link:* {result['link']}"

        await ctx.send(text)
async def setup(bot : commands.Bot):
    await bot.add_cog(FunAndGames(bot))