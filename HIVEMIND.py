import discord
import discord_slash
import sys

from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext

client = discord.Client() #The bot itself
bot = Client(intents=Intents.default())
slash = SlashCommand(bot) #Implements slash commands

@slash.event
async def on_ready():
    print('We have logged in as {0.user}'.format(slash))

@slash.slash(name="test")
async def test(ctx: SlashContext):
    embed = Embed(title="Embed Test")
    await ctx.send(embed = embed)

@slash.event
async def on_message(message):
    if message.author == slash.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

slash.run(str(sys.argv[1])) #Use token as argument when running script from console.