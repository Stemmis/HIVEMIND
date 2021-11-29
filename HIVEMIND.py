import discord
import random
import sourcerandom
import sys
import traceback
import threading
import numexpr
from sourcerandom import OnlineRandomnessSource
from discord_slash import SlashCommand, SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, wait_for_component
from discord_slash.context import MenuContext, ComponentContext
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
    
    
#Set prefix
@client.event
async def on_message(message):
    try:
        if message.content.startswith('?'):
            await parse_command(message.content[1:len(message.content)], message.channel)
    except:
        print(traceback.format_exc())
        print("Something went wrong! Please try again.")
        
#Handle ? commands
@client.event
async def parse_command(message, channel):
    try:
        if message.startswith('roll '):
            if message.strip() == 'roll':
                print('Specified an invalid dice expression.')
            else:
                await get_roll(message[5:len(message)], channel)
        elif message.startswith('roll-sr '):
            if message.strip() == 'roll-sr':
                print('Specified an invalid dice expression.')
            else:
                await get_shadowrun(message[8:len(message)], channel)
        else:
            print('Not a command')
    except:
        print(traceback.format_exc())
        print("Something went wrong with the command! Please try again.")
        channel.send("You specified an invalid command! Please try again.")
        
#Help command - Necessary now that alternative syntax is an option


@slash.slash(name="help",
                description="Get a list of commands, uses, and syntax"
                )
async def help(ctx):
#    helpmenu = create_select(
#        options = [
#            create_select_option("?roll", value="roll"),
#            create_select_option("?roll-sr", value="roll-sr")
#        ],
#        placeholder="Choose a command",
#        min_values=1,
##        max_values=1
#    )
#    try:
#        await ctx.send("Remember to use the **?** prefix for all HIVEMIND commands.", components = [create_actionrow(helpmenu)])
#        select_ctx: ComponentContext = await wait_for_component(client, components=helpmenu)
#        await ctx.edit_origin(content=ctx.selected_options[0])
#    except:
#        print(traceback.format_exc())
    await ctx.send(">>> ***HIVEMIND Commands***\n\n**Roll**\n*Description*\nThe default roll command. Rolls a user-specified number of dice with a user-specified number of sides, and adds an optional modifier.\n*Syntax*\n?roll [Number of Dice]d[Number of Sides] (+ or - [Modifier])\ne.g. ?roll 4d8+10\n\n**Roll-SR**\n*Description*\nRoll command for the Shadowrun tabletop roleplaying game. Rolls a user-specified number of d6's and counts hits, up to a user-specified limit.\n*Syntax*\n?roll-sr [Number of Dice]d[Limit]\ne.g. ?roll-sr 12d9")



#async def helpMessages(ctx, selected_options)
#    if(selected_options[0] = '?roll':
        
    
#@client.event
#async def on_component(ctx: ComponentContext):
#    await ctx.edit_origin(content=ctx.selected_options[0])



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
                    ),
                    create_option(
                        name="comment",
                        description="Optional comment - say what the roll is for",
                        option_type=3,
                        required=False
                    )
                ]
            )
async def roll(ctx, pool: int, sides: int, modifier: int = 0, comment:str = ""):
    if sides > MAX_VALUE:
        if pool == 1:
            await ctx.send(content = "Die exceeds size limit. Maybe you should roll a smaller die.")
        else:
            await ctx.send(content = "Dice exceed size limit. Maybe you should roll smaller dice.")
        raise ValueError(f"Die has too many sides! {sides}")
    if pool == 1:
        try:
            result = await numberGen(1, 1, sides, modifier)
            if(comment != ""):
                await ctx.send(content = f"```diff\n+{comment}\n```Rolled **{pool}** die with **{sides}** sides, with a modifier of **{modifier}**.\nYour result is **{result[0]}**.\n```{result[1]}```")
            else:
                await ctx.send(content = f"Rolled **{pool}** die with **{sides}** sides, with a modifier of **{modifier}**.\nYour result is **{result[0]}**.\n```{result[1]}```")
        except:
            print(traceback.format_exc())
    else:
        if(comment != ""):
            await ctx.defer()
            result = await numberGen(pool, 1, sides, modifier)
            message = f"```diff\n+{comment}\n```Rolled **{pool}** dice with **{sides}** sides, with a modifier of **{modifier}**.\nYour result is **{result[0]}**.\n```{result[1]}```"
            if len(message) > 2000:
                message = f"```diff\n+{comment}\n```Rolled **{pool}** dice with **{sides}** sides, with a modifier of **{modifier}**.\nYour total is **{result[0]}**."
            await ctx.send(content = message)
        else:
            await ctx.defer()
            result = await numberGen(pool, 1, sides, modifier)
            message = f"Rolled **{pool}** dice with **{sides}** sides, with a modifier of **{modifier}**.\nYour result is **{result[0]}**.\n```{result[1]}```"
            if len(message) > 2000:
                message = f"Rolled **{pool}** dice with **{sides}** sides, with a modifier of **{modifier}**.\nYour total is **{result[0]}**."
            await ctx.send(content = message)

#Regular ? implementation of above
async def get_roll(edited_message, channel):
    pool,size = edited_message.split("d")
    pool = int(pool)
    add = size.find('+')
    sub = size.find('-')
    if (sub != -1 and add == -1):
        mod = size.split("-",1)
        size = mod[0]
        mod = mod[1]
        if (mod.find("-") != -1):
            mod = "-" + mod
            numexpr.evaluate(mod)
        else:
            mod = "-" + mod
            mod = int(mod)
    elif (sub == -1 and add != -1):
        mod = size.split("+",1)
        size = mod[0]
        mod = mod[1]
        if (mod.find("+") != -1):
            mod = numexper.evaluate(mod)
    elif (sub < add and sub > -1 and add > -1): #if subtraction comes first
        mod = size.split("-",1)
        size = mod[0]
        mod = "-" + mod[1]
        mod = numexpr.evaluate(mod)
    elif (add < sub and add > -1 and sub >-1): #if addition comes first
        mod = size.split("+",1)
        size = mod[0]
        mod = numexpr.evaluate(mod[1])
    else:
        mod = 0
    size = int(size)
    result = await numberGen(pool, 1, size, mod)
    message = f"Rolled **{pool}** dice with **{size}** sides, with a modifier of **{mod}**.\nYour result is **{result[0]}**.\n```{result[1]}```"
    if len(message) > 2000:
        message = f"Rolled **{pool}** dice with **{size}** sides, with a modifier of **{mod}**.\nYour total is **{result[0]}**."
    await channel.send(content = message)
    




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
        
#Shadowrun non-slash workaround
async def get_shadowrun(edited_message, ctx):
    pool,limit = edited_message.split("d")
    pool = int(pool)
    limit = int(limit)
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
                bonusList = workList[0:bonus]
                workList = workList[bonus:]
                sumTotal = sum(workList) + modifier
                if (difficulty > 0 and difficulty < sumTotal):
                    DoS = (sumTotal-difficulty)//5 + 1
                    if DoS >= 4:
                        DoS = 4
                    await ctx.send(f"Rolled a total of **{sumTotal}** for **{DoS}** Degrees of Success.\n```{workList} + {modifier}```Discarded:\n```{bonusList}```")
                elif (difficulty > 0 and difficulty > sumTotal):
                    DoF = (difficulty - sumTotal)//5 + 1
                    if DoF >= 2:
                        DoF = 2
                    await ctx.send(f"Rolled a total of **{sumTotal}** for **{DoF}** Degrees of Failure.\n```{workList} + {modifier}```Discarded:\n```{bonusList}```")
                else:
                    await ctx.send(f"Rolled a total of **{sumTotal}**.\n```{workList} + {modifier}```Discarded:\n```{bonusList}```")
            except:
                print(traceback.format_exc())
        else:
            if (difficulty > 0 and difficulty < result[0]):
                DoS = (result[0]-difficulty)//5 + 1
                if DoS >= 4:
                    DoS = 4
                await ctx.send(f"Rolled a total of **{result[0]}** for **{DoS}** Degrees of Success.\n```{result[1]} + {modifier}```")
            elif (difficulty > 0 and difficulty > result[0]):
                DoF = (difficulty - result[0])//5 + 1
                if DoF >= 2:
                    DoF = 2
                await ctx.send(f"Rolled a total of **{result[0]}** for **{DoF}** Degrees of Failure.\n```{result[1]} + {modifier}```")
            else:
                await ctx.send(f"Rolled a total of **{result[0]}**.\n```{result[1]} + {modifier}```")
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