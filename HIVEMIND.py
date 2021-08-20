import discord
import random
import sourcerandom
import sys
import traceback
import threading
from sourcerandom import OnlineRandomnessSource
from discord_slash import SlashCommand, SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from discord_slash.context import MenuContext
from discord_slash.model import ContextMenuType

#Defines

client = discord.Client(intents=discord.Intents.all()) #The bot itself
slash = SlashCommand(client, sync_commands=True) #Implements slash commands. sync_commands=True means it will sync the programmed commands with discord's developer section, so they do not need to be manually updated.

#Globals

MAX_VALUE = 4294967296
MAX_DICE = 1000

#Initialize Generator
try:
    GENERATOR = sourcerandom.SourceRandom(source=OnlineRandomnessSource.QRNG_ANU, cache_size=1024, preload=True)
except:
    print(traceback.format_exc())
    GENERATOR = None

#Functions

#Begin, initialize bot.
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    
    
    
    
#The default dice rolling function. 
#This function includes two options: The number of dice to be rolled (pool) and the number of sides on each die (sides).
#This function also includes an optional modifier, to add or subtract to the function.
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
    if sides > MAX_VALUE:
        if pool == 1:
            await ctx.send(content = "Die exceeds size limit. Maybe you should roll a smaller die.")
        else:
            await ctx.send(content = "Dice exceed size limit. Maybe you should roll smaller dice.")
        raise ValueError(f"Die has too many sides! {sides}")
    if pool == 1:
        try:
            result = await numberGen(1, 1, sides, modifier)
            await ctx.send(content = f"Rolled {pool} die with {sides} sides, with a modifier of {modifier}.\nYour result is {result}.")
        except:
            print(traceback.format_exc())
    else:
        await ctx.defer()
        result = await numberGen(pool, 1, sides, modifier)
        message = f"Rolled {pool} dice with {sides} sides, with a modifier of {modifier}.\nYour result is {result}"
        if len(message) > 2000:
            message = f"Rolled {pool} dice with {sides} sides, with a modifier of {modifier}.\nYour total is {result[0]}."
        await ctx.send(content = message)




#Roll dice for the Shadowrun system.
#Roll a pool of d6's, with each 5 or 6 being a "hit".
#You cannot exceed your limit on hits; also, if half of your rolls were ones, you GLITCH. If you got no rolls and glitch, you CRITICAL GLITCH.
@slash.slash(name="rollshadowrun",
                description="Roll dice for the Shadowrun system",
                options = [
                    create_option(
                        name="pool",
                        description="Number of dice in your pool",
                        option_type=4,
                        required=True
                    ),
                    create_option(
                        name="limit",
                        description="Limit for your roll",
                        option_type=4,
                        required=True
                    )
                ]
            )
async def rollshadowrun(ctx, pool:int, limit: int):
    ones = 0
    hits = 0
    try:
        result = await numberGen(pool, 1, 6, 0)
        result = result[1]
        for val in result:
            if val == 1:
                ones += 1
            if val >= 5:
                hits += 1
        if ones >= pool/2:
            if hits == 0:
                await ctx.send(f"**!!Critical Glitch!!** Rolled **0** hits and **Glitched!** (Dice: **{pool}**, Limit: **{limit}** Ones: **{ones}**)\n```{result}```")
            else:
                await ctx.send(f"Rolled **{min(hits,limit)}** hits and **Glitched!** (Dice: **{pool}**, Limit: **{limit}** Ones: **{ones}**)\n```{result}```")
        else:
            await ctx.send(f"Rolled **{min(hits,limit)}** hits. (Dice: **{pool}**, Limit: **{limit}** Ones: **{ones}**)\n```{result}```")
    except:
        print(traceback.format_exc())
    




#Roll dice for the Sword Chronicle system.
#Roll a pool of d6's, and add them together. You must beat a given threshold.
#Additionally, you have a set of bonus dice you could add OPTIONALLY.
@slash.slash(name="rollswordchronicle",
                description = "Roll dice for the Sword Chronicle system",
                options = [
                    create_option(
                        name = "pool",
                        description = "Number of dice in your pool",
                        option_type = 4,
                        required = True
                    ),
                    create_option(
                        name = "bonus",
                        description = "Number of bonus dice to add",
                        option_type = 4,
                        required = False
                    ),
                    create_option(
                        name = "difficulty",
                        description = "Threshold you're trying to beat - for Degrees of Success/Failure",
                        option_type = 4,
                        required = False
                    ),
                    create_option(
                        name = "modifier",
                        description = "Modifier to add to your roll",
                        option_type = 4,
                        required = False
                    )
                ]
            )
async def rollswordchronicle(ctx, pool:int, bonus:int = 0, difficulty:int = 0, modifier:int = 0):
    try:
        result = await numberGen(pool, 1, 6, 0)
        if bonus !=0:
            try:
                bonusList = await numberGen(bonus, 1, 6, 0)
                bonusList = bonusList[1]
                workList = result[1]
                workList.extend(bonusList)
                workList.sort()
                bonusList = workList[0:bonus-1]
                result[1] = workList[bonus:]
                result[0] = sum(worklist[bonus:]) + modifier
                if (difficulty > 0 and difficulty < result[0]):
                    DoS = (result[0]-difficulty)//5 + 1
                    if DoS >= 4:
                        DoS = 4
                    await ctx.send(f"Rolled a total of **{result[0]} for {DoS} Degrees of Success.**\n```{result[1]} + {modifier}```\n**Discarded:**\n```{bonusList}```")
                elif (difficulty > 0 and difficulty < result[0]):
                    DoF = (difficulty - result[0])//5 + 1
                    if DoF >= 2:
                        DoF = 2
                    await ctx.send(f"Rolled a total of **{result[0]} for {DoF} Degrees of Failure.**\n```{result[1]} + {modifier}```\n**Discarded:**\n```{bonusList}```")
                else:
                    await ctx.send(f"Rolled a total of **{result[0]}.\n```{result[1]} + {modifier}```\n**Discarded:**\n```{bonusList}```")
            except:
                print(traceback.format_exc())
        else:
            if (difficulty > 0 and difficulty < result[0]):
                DoS = (result[0]-difficulty)//5 + 1
                if DoS >= 4:
                    DoS = 4
                await ctx.send(f"Rolled a total of **{result[0]} for {DoS} Degrees of Success.**\n```{result[1]} + {modifier}```")
            elif (difficulty > 0 and difficulty < result[0]):
                DoF = (difficulty - result[0])//5 + 1
                if DoF >= 2:
                    DoF = 2
                await ctx.send(f"Rolled a total of **{result[0]} for {DoF} Degrees of Failure.**\n```{result[1]} + {modifier}```")
            else:
                await ctx.send(f"Rolled a total of **{result[0]}.\n```{result[1]} + {modifier}```")
    except:
        print(traceback.format_exc())

        

#Random test command, please ignore. Testing menus functions.
@slash.context_menu(target=ContextMenuType.MESSAGE,
                    name="testfunction")
async def testfunction(ctx: MenuContext):
    await ctx.send(
        content =f"Responded! The content of the message targeted: {ctx.target_message.content}",
        hidden=True
    )
    
    
    

#The rolling itself! This function generates random numbers. 
#Count is the quantity of numbers.
#Min is the minimum value (usually 1)
#Max is the maximum value, i.e. dice size
#Mod is the modifier, you just add or subtract a number.
async def numberGen(count, min, max, mod):
    global GENERATOR
    print(f"Roll {count} dice with {max} sides with {mod} added")
    result = mod
    rollList = [0];
    for x in range(count):
        try:
            dieRoll = GENERATOR.randint(min,max)
        except:                                 #Look up: If this messes up, it'll default back to Python's default pseudorandomness.
            print('Using Pseudorandomness...')
            result = random.randint(min,max)
            if not GENERATOR:
                try:
                    GENERATOR = sourcerandom.SourceRandom(source=OnlineRandomnessSource.QRNG_ANU, cache_size=1024, preload=True) #Try to re-initialize the random number generator.
                except:
                    print(traceback.format_exc())
                    GENERATOR = None
        rollList.append(dieRoll)
        result = result + dieRoll
    del rollList[0];
    return result, rollList

client.run(str(sys.argv[1])) #Use token as argument when running script from console.