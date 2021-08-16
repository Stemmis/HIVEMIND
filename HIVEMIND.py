import discord
import discord_slash
import sys

from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext

client = discord.Client() #The bot itself
bot = Client(intents=Intents.default())
slash = SlashCommand(bot) #Implements slash commands

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@slash.slash(name="test")
async def test(ctx: SlashContext):
    embed = Embed(title="Embed Test")
    await ctx.send(embed = embed)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(str(sys.argv[1])) #Use token as argument when running script from console.