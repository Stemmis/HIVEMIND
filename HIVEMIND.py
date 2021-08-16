import discord
from discord_slash import SlashCommand
import sys

client = discord.Client(intents=discord.Intents.all()) #The bot itself
slash = SlashCommand(client, sync_commands=True) #Implements slash commands

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@slash.slash(name="test", description="This is a test command")
async def test(ctx):
    await ctx.send(content = "Hello World!")

client.run(str(sys.argv[1])) #Use token as argument when running script from console.