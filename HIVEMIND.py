import discord
from discord_slash import SlashCommand, SlashCommandOptionType
import sys

client = discord.Client(intents=discord.Intents.all()) #The bot itself
slash = SlashCommand(client, sync_commands=True) #Implements slash commands
option_type = SlashCommandOptionType.STRING

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@slash.slash(name="test", 
                description="This is a test command",
                options = [
                    create_option(
                        name="OptOne",
                        description="This is the first option",
                        option_type=3,
                        required=False
                    )
                ]
            )
async def test(ctx, optone: str):
    await ctx.send(content = f"I got you, you said {OptOne}!")

client.run(str(sys.argv[1])) #Use token as argument when running script from console.