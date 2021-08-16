import discord
import random
import sourcerandom
import sys
from sourcerandom import OnlineRandomnessSource
from discord_slash import SlashCommand, SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from discord_slash.context import MenuContext
from discord_slash.model import ContextMenuType

#Defines
client = discord.Client(intents=discord.Intents.all()) #The bot itself
slash = SlashCommand(client, sync_commands=True) #Implements slash commands

#Globals
GENERATOR = sourcerandom.SourceRandom(source=OnlineRandomnessSource.QRNG_ANU, cache_size=1024, preload=True)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    
#The default dice rolling function. This function includes two options: The number of dice to be rolled (pool) and the number of sides on each die (sides).

@slash.slash(name="roll", 
                description="Roll dice",
                options = [
                    create_option(
                        name="pool",
                        description="Number of dice in your pool",
                        option_type=4,
                        required=True
                    ),
                    create_option(
                        name="sides",
                        description="Number of sides on each die",
                        option_type=4,
                        required=True
                    ),
                    create_option(
                        name="modifier",
                        description="Modifier to roll",
                        option_type=4,
                        required=False
                    )
                ]
            )
async def roll(ctx, pool: int, sides: int, modifier: int = 0):
    if pool == 1:
        result = await numberGen(1, 1, sides, modifier)
        await ctx.send(content = f"Rolled {pool} die with {sides} sides, with a modifier of {modifier}.\nYour result is {result}.")
    else:
        result = await numberGen(pool, 1, sides, modifier)
        await ctx.send(content = f"Rolled {pool} dice with {sides} sides, with a modifier of {modifier}.\nYour result is {result}")

@slash.context_menu(target=ContextMenuType.MESSAGE,
                    name="commandname")
async def commandname(ctx: MenuContext):
    await ctx.send(
        content =f"Responded! The content of the message targeted: {ctx.target_message.content}",
        hidden=True
    )

#The rolling itself!    
async def numberGen(count, min, max, mod):
    print(f"Roll {count} dice with {max} sides with {mod} added")
    result = mod
    rollList = [0];
    for x in range(count):
        dieRoll = GENERATOR.randint(min,max)
        rollList.append(dieRoll)
        result = result + dieRoll
    del rollList[0];
    return result, rollList

client.run(str(sys.argv[1])) #Use token as argument when running script from console.