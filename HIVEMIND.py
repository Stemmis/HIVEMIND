import discord
from discord_slash import SlashCommand, SlashContext
import sys

client = discord.Client(intents=discord.Intents.all()) #The bot itself
slash = SlashCommand(client, sync_commands=True) #Implements slash commands

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