import discord
import random
import sourcerandom
import sys
import traceback
import math
#import numexpr
import sqlite3
import interactions
from sourcerandom import OnlineRandomnessSource

#Defines

intents = discord.Intents.default() #Includes all intents EXCEPT privileged ones. Defined separately here in case I want to disable some intents later.

client = interactions.Client(str(sys.argv[1])) #The bot itself. Pass token as argument in console.

#Globals

MAX_VALUE = 4294967296
MAX_DICE = 1000
GENERATOR = None


#Initialize Generator
try:
    GENERATOR = sourcerandom.SourceRandom(source=OnlineRandomnessSource.QRNG_ANU, cache_size=1024, preload=True)
except:
    print(traceback.format_exc())
    print('\nqrng_anu is not responding.\n')
    GENERATOR = None
    
#Initialize Database

print("Opening Initiative database")
initiative = sqlite3.connect('init.db')
print("Checking master initiative table")
initiative.execute("CREATE TABLE if not exists ENCOUNTER (EID INT PRIMARY KEY NOT NULL, MASTER INT NOT NULL, CURRENT CHAR(32));")
print("Checking init value table") 
initiative.execute("CREATE TABLE if not exists CHARACTER (EID INT NOT NULL, CHAR_NAME CHAR(32) NOT NULL, USERID INT NOT NULL, INIT INT);")
initiative.close()

#Functions

async def initGen():
    global GENERATOR
    if GENERATOR is None:
        try:
            GENERATOR = await sourcerandom.SourceRandom(source=OnlineRandomnessSource.QRNG_ANU, cache_size=1024, preload=True) #Try to re-initialize the random number generator.
        except:
            print(traceback.format_exc())
            GENERATOR = None

#Begin, initialize bot.
@client.event
async def on_ready():
    print('We have logged in as HIVEMIND')
   
    
    
#Set prefix
#@client.event
#async def on_message(message):
#    try:
#        if message.content.startswith('?'):
#            await parse_command(message.content[1:len(message.content)], message.channel)
#    except:
#        print(traceback.format_exc())
#        print("Something went wrong! Please try again.")
        
#Handle ? commands
#@client.event
#async def parse_command(message, channel):
#    try:
#        if message.startswith('roll '):
#            if message.strip() == 'roll':
#                print('Specified an invalid dice expression.')
#            else:
#                await get_roll(message[5:len(message)], channel)
#        elif message.startswith('help'):
#            help(channel)
#        elif message.startswith('roll-sr '):
#            if message.strip() == 'roll-sr':
#                print('Specified an invalid dice expression.')
#            else:
#                await get_shadowrun(message[8:len(message)], channel)
#        elif message.startswith('roll-sc '):
#            if message.strip() == 'roll-sc':
#                print('Specified an invalid dice expression.')
#            else:
#                await get_swordchronicle(message[8:len(message)], channel)
#        elif message.startswith('row'):
#            if message.strip() == 'row':
#                await get_row(None, channel)
#            else:
#                await get_row(message[4:len(message)], channel)
#        else:
#            print('Not a command')
#    except:
#        print(traceback.format_exc())
#        print("Something went wrong with the command! Please try again.")
#        await channel.send("You specified an invalid command! Please try again.")
        
#Help command - Unnecessary now that alternative syntax is no longer an option


#@client.command(name="help",
#                description="Get a list of commands, uses, and syntax"
#                )
#async def help(ctx):
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
#    await ctx.send(">>> ***HIVEMIND Commands***\n\n**Roll**\n*Description*\nThe default roll command. Rolls a user-specified number of dice with a user-specified number of sides, and adds an optional modifier.\n*Syntax*\n?roll [Number of Dice]d[Number of Sides] (+ or - [Modifier])\ne.g. ?roll 4d8+10\n\n**Roll-SR**\n*Description*\nRoll command for the Shadowrun tabletop roleplaying game. Rolls a user-specified number of d6's and counts hits, up to a user-specified limit.\n*Syntax*\n?roll-sr [Number of Dice]d[Limit]\ne.g. ?roll-sr 12d9\n\n**Roll-SC**\n*Description*\nRoll command for the Sword Chronicle tabletop roleplaying game. Rolls a user-specified number of d6's and adds them. Allows for optional bonus dice, modifiers, or difficulty.\n*Syntax*\n?roll-sc [Number of Dice]d([Number of Bonus]b[Difficulty of Test]d(+ or - [Modifier]))\ne.g. ?roll 5d2b9d+3\n\n**Roll-Warhammer**\n*Description*\nRolls a percentile dice, as used in the Warhammer 40k family of tabletop roleplaying games. Allows for an optional threshold to beat for determining degrees of success or failure, and adds an optional modifier.\n*Syntax*\n?row ([Threshold]v[Modifier])\ne.g. ?row 45v-30")



#The default dice rolling function. 
#This function includes two options: The number of dice to be rolled (pool) and the number of sides on each die (sides).
#This function also includes an optional modifier, to add or subtract to the function.
@client.command(name="roll", 
                description="Roll dice",
                options = [
                    interactions.Option(
                        name="pool", 
                        description="Number of dice in your pool",
                        type=4,
                        required=True
                    ),
                    interactions.Option(
                        name="sides",
                        description="Number of sides on each die",
                        type=4,
                        required=True
                    ),
                    interactions.Option(
                        name="modifier",
                        description="Modifier to roll",
                        type=4,
                        required=False
                    ),
                    interactions.Option(
                        name="comment",
                        description="Optional comment - say what the roll is for",
                        type=3,
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
    if pool > MAX_DICE:
        await ctx.send(content = "Please don't roll so many dice at once.")
        raise ValueError(f"Too many dice in pool! {pool}")
    if pool == 1:
        await ctx.defer()
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
        await initGen()

#Regular ? implementation of above
#async def get_roll(edited_message, channel):
#    pool,size = edited_message.split("d")
#    pool = int(pool)
#    add = size.find('+')
#    sub = size.find('-')
#    if (sub != -1 and add == -1):
#        mod = size.split("-",1)
#        size = mod[0]
#        mod = mod[1]
#        if (mod.find("-") != -1):
#            mod = "-" + mod
#            numexpr.evaluate(mod)
#        else:
#            mod = "-" + mod
#            mod = int(mod)
#    elif (sub == -1 and add != -1):
#        mod = size.split("+",1)
 #       size = mod[0]
#        mod = mod[1]
#        if (mod.find("+") != -1):
#            mod = numexpr.evaluate(mod)
#        mod = int(mod)
#    elif (sub < add and sub > -1 and add > -1): #if subtraction comes first
#        mod = size.split("-",1)
#        size = mod[0]
#        mod = "-" + mod[1]
#        mod = numexpr.evaluate(mod)
#    elif (add < sub and add > -1 and sub >-1): #if addition comes first
#        mod = size.split("+",1)
#        size = mod[0]
 #       mod = numexpr.evaluate(mod[1])
#    else:
 #       mod = 0
#    size = int(size)
#    result = await numberGen(pool, 1, size, mod)
#    message = f"Rolled **{pool}** dice with **{size}** sides, with a modifier of **{mod}**.\nYour result is **{result[0]}**.\n```{result[1]}```"
#    if len(message) > 2000:
##        message = f"Rolled **{pool}** dice with **{size}** sides, with a modifier of **{mod}**.\nYour total is **{result[0]}**."
#    await channel.send(content = message)
    


@client.command(name="repeatroll", 
                description="Roll the same dice repeatedly.",
                options = [
                    interactions.Option(
                        name="pool",
                        description="Number of dice in your pool",
                        type=4,
                        required=True
                    ),
                    interactions.Option(
                        name="sides",
                        description="Number of sides on each die",
                        type=4,
                        required=True
                    ),
                    interactions.Option(
                        name="repetition",
                        description="How many times you'd like to roll",
                        type=4,
                        required=True
                    ),
                    interactions.Option(
                        name="modifier",
                        description="Modifier to roll",
                        type=4,
                        required=False
                    ),
                    interactions.Option(
                        name="comment",
                        description="Optional comment - say what the roll is for",
                        type=3,
                        required=False
                    )
                ]
            )
async def repeatroll(ctx, pool: int, sides: int, repetition: int, modifier: int = 0, comment:str = ""):
    if sides > MAX_VALUE:
        if pool == 1:
            await ctx.send(content = "Die exceeds size limit. Maybe you should roll a smaller die.")
        else:
            await ctx.send(content = "Dice exceed size limit. Maybe you should roll smaller dice.")
        raise ValueError(f"Die has too many sides! {sides}")
    if pool > MAX_DICE:
        await ctx.send(content = "Please don't roll so many dice at once.")
        raise ValueError(f"Too many dice in pool! {pool}")
    if pool == 1:
        try:
            await ctx.defer()
            result = await numberGen(repetition, 1, sides, 0)
            for index in result[1]:
                index += modifier
            total = int(result[0])
            total += (modifier*repetition)
            if(comment != ""):
                await ctx.send(content = f"```diff\n+{comment}\n```Rolled **1** die with **{sides}** sides **{repetition}** times, each with a modifier of **{modifier}**.\nYour result is **{total}**.\n```{result[1]}```")
            else:
                await ctx.send(content = f"Rolled **1** die with **{sides}** sides **{repetition}** times, each with a modifier of **{modifier}**.\nYour result is **{total}**.\n```{result[1]}```")
            message = f"Your individual pool totals are:```"
            for x in range(0,repetition):
                message += (f"\nPool {x+1}: {result[1][x]+modifier}")
            message += ("```")
            if len(message) < 2000:
                await ctx.send(content = message)
        except:
            print(traceback.format_exc())
    else:
        if(comment != ""):
            try:
                newPool = pool * repetition
                await ctx.defer()
                result = await numberGen(newPool, 1, sides, 0)
                for index in result[1]:
                    index += modifier
                total = int(result[0])
                total += (newPool*pool)
                message = f"```diff\n+{comment}\n```Rolled **{pool}** dice with **{sides}** sides **{repetition}** times, each with a modifier of **{modifier}**.\nYour result is **{total}**.\n```{result[1]}```"
                if len(message) > 2000:
                    message = f"```diff\n+{comment}\n```Rolled **{pool}** dice with **{sides}** sides **{repetition}** times, each with a modifier of **{modifier}**.\nYour total is **{total}**."
                await ctx.send(content = message)
                message = f"Your individual pool totals are:```"
                currentPoolSum = 0
                iter = 0
                for x in range(0,repetition):
                    for index in range(0, pool):
                        currentPoolSum += result[1][iter]
                        iter += 1
                    currentPoolSum += modifier
                    message += (f"\nPool {x+1}: {currentPoolSum}")
                    currentPoolSum = 0
                message += ("```")
                if len(message) < 2000:
                    await ctx.send(content = message)
            except:
                print(traceback.format_exc())
        else:
            await ctx.defer()
            try:
                newPool = pool * repetition
                result = await numberGen(newPool, 1, sides, 0)
                for index in result[1]:
                    index += modifier
                total = int(result[0])
                total += (newPool*pool)
                message = f"Rolled **{pool}** dice with **{sides}** sides **{repetition}** times, each with a modifier of **{modifier}**.\nYour result is **{total}**.\n```{result[1]}```"
                if len(message) > 2000:
                    message = f"Rolled **{pool}** dice with **{sides}** sides **{repetition}** times, each with a modifier of **{modifier}**.\nYour total is **{total}**."
                await ctx.send(content = message)
                message = f"Your individual pool totals are:```"
                currentPoolSum = 0
                iter = 0
                for x in range(0,repetition):
                    for index in range(0, pool):
                        currentPoolSum += result[1][iter]
                        iter += 1
                    currentPoolSum += modifier
                    message += (f"\nPool {x+1}: {currentPoolSum}")
                    currentPoolSum = 0
                message += ("```")
                if len(message) < 2000:
                    await ctx.send(content = message)
            except:
                print(traceback.format_exc())
    await initGen()
#Roll dice for the Shadowrun system.
#Roll a pool of d6's, with each 5 or 6 being a "hit".
#You cannot exceed your limit on hits; also, if half of your rolls were ones, you GLITCH. If you got no rolls and glitch, you CRITICAL GLITCH.
@client.command(name="rollshadowrun",
                description="Roll dice for the Shadowrun system",
                options = [
                    interactions.Option(
                        name="pool",
                        description="Number of dice in your pool",
                        type=4,
                        required=True
                    ),
                    interactions.Option(
                        name="limit",
                        description="Limit for your roll",
                        type=4,
                        required=True
                    ),
                    interactions.Option(
                        name="modifier",
                        description="Modifier to roll",
                        type=4,
                        required=False
                    ),
                    interactions.Option(
                        name="comment",
                        description="Optional comment - say what the roll is for",
                        type=3,
                        required=False
                    ),
                    interactions.Option(
                        name="edge",
                        description="Optional comment - say what the roll is for",
                        type=5,
                        required=False
                    )
                ]
            )
async def rollshadowrun(ctx, pool:int, limit:int, edge:bool=False, modifier:int=0, comment:str=""):
    if pool > MAX_DICE:
        await ctx.send(content = "Please don't roll so many dice at once.")
        raise ValueError(f"Too many dice in pool! {pool}")
    ones = 0
    hits = modifier
    sixes = 0 #Here for the Rule of Sixes, edge and all
    try:
        await ctx.defer()
        result = await numberGen(pool, 1, 6, 0)
        result = sorted(result[1])
        for val in result:
            if(val == 1):
                ones += 1
            if(val >= 5):
                hits += 1
            if(edge and (val == 6)):
                sixes += 1
        if(edge and (sixes > 0)):
            await ctx.defer()
            edgeResult = await numberGen(sixes, 1, 6, 0)
            edgeResult = sorted(edgeResult[1])
            for val in edgeResult:
                if(val == 1):
                    ones += 1
                if(val >= 5):
                    hits += 1
        else:
            edgeResult = ""
        if(comment != ""):
            message = f"```diff\n+{comment}\n```"
        else:
            message = ""
        if edge:
            if ones >= pool/2:
                if hits == 0:
                        await ctx.send(message + f"**!!Critical Glitch!!** Rolled **0** hits and **Glitched!** (Dice: **{pool}**, Ones: **{ones}**, Exploding Sixes: **{sixes}**, Modifier: **{modifier}**)\n```{result}```")
                else:
                    if hits == 1:
                        await ctx.send(message + f"Rolled **{hits}** hit and **Glitched!** (Dice: **{pool}**, Ones: **{ones}**, Exploding Sixes: **{sixes}**, Modifier: **{modifier}**)\n```{result}```\nRerolled Sixes:```{edgeResult}```")
                    else:
                        await ctx.send(message + f"Rolled **{hits}** hits and **Glitched!** (Dice: **{pool}**, Ones: **{ones}**, Exploding Sixes: **{sixes}**, Modifier: **{modifier}**)\n```{result}```\nRerolled Sixes:```{edgeResult}```")
            else:
                if hits == 1:
                    await ctx.send(message + f"Rolled **{hits}** hit. (Dice: **{pool}**, Ones: **{ones}**, Exploding Sixes: **{sixes}**, Modifier: **{modifier}**)\n```{result}```\nRerolled Sixes:```{edgeResult}```")
                else:
                    await ctx.send(message + f"Rolled **{hits}** hits. (Dice: **{pool}**, Ones: **{ones}**, Exploding Sixes: **{sixes}**, Modifier: **{modifier}**)\n```{result}```\nRerolled Sixes:```{edgeResult}```")
        else:
            if ones >= pool/2:
                if hits == 0:
                    await ctx.send(message + f"**!!Critical Glitch!!** Rolled **0** hits and **Glitched!** (Dice: **{pool}**, Limit: **{limit}** Ones: **{ones}**, Modifier: **{modifier}**)\n```{result}```")
                else:
                    if hits == 1:
                        await ctx.send(message + f"Rolled **{min(hits,limit)}** hit and **Glitched!** (Dice: **{pool}**, Limit: **{limit}** Ones: **{ones}**, Modifier: **{modifier}**)\n```{result}```")
                    else:
                        await ctx.send(message + f"Rolled **{min(hits,limit)}** hits and **Glitched!** (Dice: **{pool}**, Limit: **{limit}** Ones: **{ones}**, Modifier: **{modifier}**)\n```{result}```")
            else:
                if hits == 1:
                    await ctx.send(message + f"Rolled **{min(hits,limit)}** hit. (Dice: **{pool}**, Limit: **{limit}** Ones: **{ones}**, Modifier: **{modifier}**)\n```{result}```")
                else:
                    await ctx.send(message + f"Rolled **{min(hits,limit)}** hits. (Dice: **{pool}**, Limit: **{limit}** Ones: **{ones}**, Modifier: **{modifier}**)\n```{result}```")
    except:
        print(traceback.format_exc())
    await initGen()
        
#Shadowrun non-slash workaround
#async def get_shadowrun(edited_message, ctx):
#    pool,limit = edited_message.split("d")
#    pool = int(pool)
#    limit = int(limit)
#    ones = 0
#    hits = 0
#    try: 
#        result = await numberGen(pool, 1, 6, 0)
#        result = result[1]
#        for val in result:
#            if val == 1:
#                ones += 1
 #           if val >= 5:
#                hits += 1
#        if ones >= pool/2:
#            if hits == 0:
#                await ctx.send(f"**!!Critical Glitch!!** Rolled **0** hits and **Glitched!** (Dice: **{pool}**, Limit: **{limit}** Ones: **{ones}**)\n```{result}```")
#            else:
#                await ctx.send(f"Rolled **{min(hits,limit)}** hits and **Glitched!** (Dice: **{pool}**, Limit: **{limit}** Ones: **{ones}**)\n```{result}```")
 #       else:
 #           await ctx.send(f"Rolled **{min(hits,limit)}** hits. (Dice: **{pool}**, Limit: **{limit}** Ones: **{ones}**)\n```{result}```")
#    except:
#        print(traceback.format_exc())




#Roll dice for the Sword Chronicle system.
#Roll a pool of d6's, and add them together. You must beat a given threshold.
#Additionally, you have a set of bonus dice you could add OPTIONALLY.
@client.command(name="rollswordchronicle",
                description = "Roll dice for the Sword Chronicle system",
                options = [
                    interactions.Option(
                        name = "pool",
                        description = "Number of dice in your pool",
                        type = 4,
                        required = True
                    ),
                    interactions.Option(
                        name = "bonus",
                        description = "Number of bonus dice to add",
                        type = 4,
                        required = False
                    ),
                    interactions.Option(
                        name = "difficulty",
                        description = "Threshold you're trying to beat - for Degrees of Success/Failure",
                        type = 4,
                        required = False
                    ),
                    interactions.Option(
                        name = "modifier",
                        description = "Modifier to add to your roll",
                        type = 4,
                        required = False
                    )
                ]
            )
async def rollswordchronicle(ctx, pool:int, bonus:int = 0, difficulty:int = 0, modifier:int = 0):
    try:
        if pool > MAX_DICE:
            await ctx.send(content = "Please don't roll so many dice at once.")
            raise ValueError(f"Too many dice in pool! {pool}")
        await ctx.defer()
        result = await numberGen(pool, 1, 6, 0)
        if bonus !=0:
            try:
                await ctx.defer()
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
    await initGen()


#Sword Chronicle non-slash workaround
#async def get_swordchronicle(edited_message, ctx):
#    if edited_message.find("d") != edited_message.rfind("d"):#
#        pool,otherBit,mod = edited_message.split("d")#
#        hasDif = True
#    else:
#        pool,otherBit = edited_message.split("d")
 #       hasDif = False
#    pool = int(pool)
#    modifier = 0
#    bonus = 0
#    difficulty = 0#
#    if otherBit!=None:
#        if otherBit.find("b") != -1:
#            bonus,otherBit = otherBit.split("b")
#            bonus = int(bonus)
#        if (otherBit.find("+") != -1) or (otherBit.find("-") != -1):
#            modifier = "0"+otherBit
#            modifier = numexpr.evaluate(modifier)
#        if hasDif:
#            difficulty = int(otherBit)
 #   if hasDif:
#        modifier = "0"+mod
#        modifier = numexpr.evaluate(modifier)
#    try: 
#        result = await numberGen(pool, 1, 6, 0)
#        if bonus!=0:
#            try:
#                bonusList = await numberGen(bonus, 1, 6, 0)
#                bonusList = bonusList[1]
#                workList = result[1]
#                workList.extend(bonusList)
#                workList.sort()
#                bonusList = workList[0:bonus]
#                workList = workList[bonus:]
#                sumTotal = sum(workList) + modifier
#                if (difficulty > 0 and difficulty < sumTotal):
#                    DoS = (sumTotal-difficulty)//5 + 1
#                    if DoS >= 4:
#                        DoS = 4
#                    await ctx.send(f"Rolled a total of **{sumTotal}** for **{DoS}** Degrees of Success.\n```{workList} + {modifier}```Discarded:\n```{bonusList}```")
#                elif (difficulty > 0 and difficulty > sumTotal):
#                    DoF = (difficulty - sumTotal)//5 + 1
#                    if DoF >= 2:
#                        DoF = 2
#                    await ctx.send(f"Rolled a total of **{sumTotal}** for **{DoF}** Degrees of Failure.\n```{workList} + {modifier}```Discarded:\n```{bonusList}```")
#                else:
#                    await ctx.send(f"Rolled a total of **{sumTotal}**.\n```{workList} + {modifier}```Discarded:\n```{bonusList}```")
 #           except:
#                print(traceback.format_exc())
#        else:
#            if (difficulty > 0 and difficulty < result[0]):
#                DoS = (result[0]-difficulty)//5 + 1
#                if DoS >= 4:
#                    DoS = 4
#                await ctx.send(f"Rolled a total of **{result[0]}** for **{DoS}** Degrees of Success.\n```{result[1]} + {modifier}```")
#            elif (difficulty > 0 and difficulty > result[0]):
 #               DoF = (difficulty - result[0])//5 + 1
 #               if DoF >= 2:
 #                   DoF = 2
 #               await ctx.send(f"Rolled a total of **{result[0]}** for **{DoF}** Degrees of Failure.\n```{result[1]} + {modifier}```")
#            else:
#                await ctx.send(f"Rolled a total of **{result[0]}**.\n```{result[1]} + {modifier}```")
#    except:
#        print(traceback.format_exc())

#Random test command, please ignore. Testing menus functions.
#@client.command(
#    type = interactions.ApplicationCommandType.USER,
#    name = "testFunction"
#)
#async def testfunction(ctx):
#    await ctx.send(
#        content =f"Responded! The content of the message targeted: {ctx.target_message.content}",
#        hidden=True
#    )
    

#Roll dice for the Warhammer 40k percentile dice systems.
#Roll a d100. Optionally include a number you're trying to beat for degrees of success/failure, or modifiers.
@client.command(name="row",
                description = "Roll dice for percentile dice systems, such as the Warhammer 40k family",
                options = [
                    interactions.Option(
                        name = "threshold",
                        description = "The number you are trying to beat",
                        type = 4,
                        required = False
                    ),
                    interactions.Option(
                        name = "modifier",
                        description = "Modifier to add to your roll",
                        type = 4,
                        required = False
                    )
                ]
            )
async def row(ctx, threshold:int = 0, modifier:int = 0):
    try:
        await ctx.defer()
        result = await numberGen(1, 1, 100, modifier)
        roll = result[1][0]
        result = result[0]
        if threshold != 0:
            DoS = (result-threshold)//10
            if modifier != 0:
                if result <= threshold:
                    DoS = -DoS
                    await ctx.send(f"Rolled a *{roll}* with a modifier of *{modifier}* for **{result}** vs **{threshold}**.\n**Succeeded** with **{DoS}** Degrees of Success!")
                if result > threshold:
                    await ctx.send(f"Rolled a *{roll}* with a modifier of *{modifier}* for **{result}** vs **{threshold}**.\n**Failed** with **{DoS}** Degrees of Failure!")
            else:
                if result <= threshold:
                    DoS = -DoS
                    await ctx.send(f"Rolled a **{result}** vs **{threshold}**.\n**Succeeded** with **{DoS}** Degrees of Success!")
                if result > threshold:
                    await ctx.send(f"Rolled a **{result}** vs **{threshold}**.\n**Failed** with **{DoS}** Degrees of Failure!")
        else:
            if modifier != 0:
                await ctx.send(f"Rolled a *{roll}* with a modifier of *{modifier}* for **{result}**.")
            else:
                await ctx.send(f"Rolled a **{result}**.")
    except:
        print(traceback.format_exc())
    await initGen()
        
#Roll dice for the World of Darkness family of systems.
#Roll a pool of d10's, with each 6+ being a "hit".
@client.command(name="rollwod",
                description="Roll dice for the World of Darkness family of systems",
                options = [
                    interactions.Option(
                        name="pool",
                        description="Number of dice in your pool",
                        type=4,
                        required=True
                    ),
                    interactions.Option(
                        name="modifier",
                        description="Modifier (free hits) to roll",
                        type=4,
                        required=False
                    ),
                    interactions.Option(
                        name="comment",
                        description="Optional comment - say what the roll is for",
                        type=3,
                        required=False
                    )
                ]
            )
async def rollwod(ctx, pool:int, modifier:int=0, comment:str=""):
    if pool > MAX_DICE:
        await ctx.send(content = "Please don't roll so many dice at once.")
        raise ValueError(f"Too many dice in pool! {pool}")
    hits = modifier
    try:
        await ctx.defer()
        result = await numberGen(pool, 1, 10, 0)
        result = result[1]
        tens = 0
        for val in result:
            if(val >= 6):
                hits += 1
            if(val == 10):
                tens += 1
        tens = math.floor(tens / 2) #WoD makes crits only apply to pairs of tens. Weird but them's the rules.
        hits = hits + (tens * 2)
        if(comment != ""):
            message = f"```diff\n+{comment}\n```"
        else:
            message = ""
        if(hits == 1):
            await ctx.send(message + f"Rolled **1** hit. (Dice: **{pool}**, Modifier: **{modifier}**)\n```{result}```")
        else:
            await ctx.send(message + f"Rolled **{hits}** hits. (Dice: **{pool}**, Modifier: **{modifier}**), Critical Successes: **{tens}**\n```{result}```")
    except:
        print(traceback.format_exc())
    await initGen()
        
#Row non-slash workaround
#async def get_row(edited_message, ctx):
#    if edited_message == None:
#        try:
#            result = await numberGen(1, 1, 100, 0)
#            result = result[0]
#            await ctx.send(f"Rolled a **{result}**.")
#        except:
#            print(traceback.format_exc())
#    else:
#        modifier = 0
#        threshold = None
#        if edited_message.find("v") != -1:
#            threshold,modifier = edited_message.split("v")
#            threshold = int(threshold)
#            modifier = "0" + modifier
#            modifier = numexpr.evaluate(modifier)
#            try:
#                result = await numberGen(1, 1, 100, modifier)
#                roll = result[1][0]
#                result = result[0]
#                DoS = (result-threshold)//10 + 1
#                if modifier != 0:
#                    if result <= threshold:
#                        DoS = -DoS
#                        await ctx.send(f"Rolled a *{roll}* with a modifier of *{modifier}* for **{result}** vs **{threshold}**.\n**Succeeded** with **{DoS}** Degrees of Success!")
#                    if result > threshold:
#                        await ctx.send(f"Rolled a *{roll}* with a modifier of *{modifier}* for **{result}** vs **{threshold}**.\n**Failed** with **{DoS}** Degrees of Failure!")
#                else:
#                    if result <= threshold:
#                        DoS = -DoS
#                        await ctx.send(f"Rolled a **{result}** vs **{threshold}**.\n**Succeeded** with **{DoS}** Degrees of Success!")
#                    if result > threshold:
#                        await ctx.send(f"Rolled a **{result}** vs **{threshold}**.\n**Failed** with **{DoS}** Degrees of Failure!")
#            except:
#                print(traceback.format_exc())
#        else:
#            modifier = numexpr.evaluate(modifier)
#            try:
#                result = await numberGen(1, 1, 100, modifier)
#                roll = result[1][0]
#                result = result[0]
#                await ctx.send(f"Rolled a *{roll}* with a modifier of *{modifier}* for **{result}**.")
#            except:
#                print(traceback.format_exc())
                

#Create an initiative encounter within the initiative database
#Adds a new entry to the initiative database
#Says the encounter ID in chat
@client.command(name = "init")
async def init(ctx: interactions.CommandContext):
    "Initiative family of commands"
    pass
@init.subcommand(name="start",
                description = "Start a new initiative encounter.",
)
async def start(ctx):
    initiative = sqlite3.connect('init.db')
    cursor = initiative.execute("SELECT MAX (EID) FROM ENCOUNTER;")
    highestID = cursor.fetchone()[0]
    if highestID == None:
        highestID = 0
    ID = highestID + 1
    initiative.execute(f"INSERT INTO ENCOUNTER VALUES ({ID}, {ctx.member.id}, 'Undefined');")
    await ctx.send(f"Your encounter ID is {ID}.\nRoll initiative!")
    initiative.commit()
    initiative.close()
    
#Remove an initiative encounter from the initiative database
#Removes an entry from the initiative database based on supplied ID
#Says the encounter ID in chat
@init.subcommand(name="end",
                description = "End an old initiative encounter.", 
                options = [
                    interactions.Option(
                        name = "encounterid",
                        description = "The ID of your encounter",
                        type = 4,
                        required = True
                    )
                ]
            )
async def initend(ctx, encounterid):
    initiative = sqlite3.connect('init.db')
    cursor = initiative.execute(f"SELECT MASTER FROM ENCOUNTER WHERE EID = {encounterid};")
    masterID = cursor.fetchone()[0]
    if (ctx.member.id) == masterID:
        initiative.execute(f"DELETE FROM ENCOUNTER WHERE EID = {encounterid};")
        initiative.execute(f"DELETE FROM CHARACTER WHERE EID = {encounterid};")
        await ctx.send(f"Encounter over.")
    else:
        try:
            owner = await interactions.get(client, interactions.Member, parent_id=ctx.guild_id, object_id=masterID)
            await ctx.send(
            content =f"Only the master of an initiative encounter can end it. Ask {owner.user}!",
            ephemeral=True)
        except:
            await ctx.send(
            content=f"Only the master of an initiative encounter can end it. The master of the specified initiative encounter does not appear to be in this server.", 
            ephemeral=True)
            print(traceback.format_exc())
    initiative.commit()
    initiative.close()

#Print all EIDs into console
@init.subcommand(name="view",
                description = "Debug command. Prints all initiative information into console."
            )
async def initview(ctx):
    initiative = sqlite3.connect('init.db')
    cursor = initiative.execute("SELECT * FROM ENCOUNTER;")
    for row in cursor:
        print(f"ID: {row[0]}; Master: {row[1]}; Current: {row[2]}")
    cursor = initiative.execute("SELECT * FROM CHARACTER;")
    for row in cursor:
        print(f"EID: {row[0]}; Character Name: {row[1]}; Player ID: {row[2]}; Initiative: {row[3]}")
    await ctx.send(
        content =f"This is a debug command.",
        ephemeral=True
    )
    initiative.commit()
    initiative.close()

#Roll random initiative for a specified character
#Rolls dice of specified size and quantity with optional modifier, updates initiative table using specified encounter value with specified charactername and result
#Outputs roll result in chat
@init.subcommand(name="roll",
                description = "Roll initiative.",
                options = [
                    interactions.Option(
                        name = "encounterid",
                        description = "The ID of your encounter",
                        type = 3,
                        required = True
                    ),
                    interactions.Option(
                        name = "charactername",
                        description = "Your character's name",
                        type = 3,
                        required = True
                    ),
                    interactions.Option(
                        name="pool",
                        description="Number of dice in your pool",
                        type=4,
                        required=True
                    ),
                    interactions.Option(
                        name="sides",
                        description="Number of sides on each die",
                        type=4,
                        required=True
                    ),
                    interactions.Option(
                        name="modifier",
                        description="Modifier to roll",
                        type=4,
                        required=False
                    )
                ]
            )
async def initroll(ctx, encounterid, charactername, pool, sides, modifier:int = 0):
    if sides > MAX_VALUE:
        if pool == 1:
            await ctx.send(content = "Die exceeds size limit. Maybe you should roll a smaller die.")
        else:
            await ctx.send(content = "Dice exceed size limit. Maybe you should roll smaller dice.")
        raise ValueError(f"Die has too many sides! {sides}")
    if pool > MAX_DICE:
        await ctx.send(content = "Please don't roll so many dice at once.")
        raise ValueError(f"Too many dice in pool! {pool}")
    valid = True
    initiative = sqlite3.connect('init.db')
    cursor = initiative.execute(f"SELECT EID FROM ENCOUNTER WHERE EID = {encounterid};")
    if cursor.fetchone() == None: #Failed to select based on supplied ID
        await ctx.send(content = f"Specified an invalid Encounter ID. Please try again.", ephemeral = True)
    else:
        cursor = initiative.execute(f"SELECT USERID FROM CHARACTER WHERE EID = {encounterid} AND CHAR_NAME = '{charactername}';") #Specifically searches for this character within this encounter in database
        UID = cursor.fetchone()
        if UID != None:
            if UID[0] != ctx.member.id:
                await ctx.send(content = f"Someone else already rolled initiative for this character.", ephemeral = True)
                valid = False  
        if valid == True:
            initiative.execute(f"DELETE FROM CHARACTER WHERE EID = {encounterid} AND CHAR_NAME = '{charactername}';") #Updates old initiative value for newly rolled one IF the user owns this character.
            await ctx.defer()
            initVal = await numberGen(pool, 1, sides, modifier)
            initVal = initVal[0]
            initiative.execute(f"INSERT INTO CHARACTER VALUES ({encounterid},'{charactername}',{ctx.member.id},{initVal});")
            await ctx.send(f"{charactername}'s initiative is **{initVal}**.")
            cursor = initiative.execute(f"SELECT MAX(INIT) FROM CHARACTER WHERE EID = {encounterid};") #Find highest initiative
            highest = cursor.fetchone()[0]
            print(highest)
            if highest != None:
                if initVal >= highest:
                    initiative.execute(f"UPDATE ENCOUNTER SET CURRENT = '{charactername}' WHERE EID = {encounterid};") #If it's the highest, it should be the new current player
            else:
                initiative.execute(f"UPDATE ENCOUNTER SET CURRENT = '{charactername}' WHERE EID = {encounterid};") #If there's nothing else, this is the highest.
            initiative.commit()
    initiative.close()
    await initGen()

#Sets initiative value within initiative database
#Manually edits initiative value of specified character within specified encounter to specified number.
#If character does not belong to command user, bot will throw an exception and stop.
#Outputs new initiative and updates database
@init.subcommand(name="set",
                description = "Set a character's initiative value.", 
                options = [
                    interactions.Option(
                        name = "encounterid",
                        description = "The ID of your encounter",
                        type = 4,
                        required = True
                    ),
                    interactions.Option(
                        name = "charactername",
                        description = "The name of your character",
                        type = 3,
                        required = True
                    ),
                    interactions.Option(
                        name = "newinit",
                        description = "Your new initiative value",
                        type = 4,
                        required = True
                    )
                ]
            )
async def initset(ctx, encounterid, charactername, newinit):
    initiative = sqlite3.connect('init.db')
    cursor = initiative.execute(f"SELECT EID FROM ENCOUNTER WHERE EID = {encounterid};")
    if cursor.fetchone() == None:
        await ctx.send(content = f"Specified an invalid Encounter ID. Please try again.", hidden = True)
    else:
        cursor = initiative.execute(f"SELECT CHAR_NAME FROM CHARACTER WHERE EID = {encounterid} AND CHAR_NAME = '{charactername}';")
        if cursor.fetchone() == None:
            await ctx.send(content = f"Specified an invalid character name for the specified encounter. Please try again.", hidden = True)
        else:
            cursor = initiative.execute(f"SELECT USERID FROM CHARACTER WHERE EID = {encounterid} AND CHAR_NAME = '{charactername}';")
            if ctx.member.id != cursor.fetchone()[0]: #Cursor comes to a 2-dimensional array; the first array returned's first value is the UUID.
                await ctx.send(content = f"You may only modify your own characters' initiative values.", hidden = True)
            else:
                initiative.execute(f"UPDATE CHARACTER SET INIT = {newinit} WHERE EID = {encounterid} AND CHAR_NAME = '{charactername}';")
                initiative.commit()
                await ctx.send(f"{charactername}'s initiative is now **{newinit}**.")
    initiative.close()

#Moves the initiative tracker up by 1 or loops back at end

@init.subcommand(name="next",
                description = "Move the initiative tracker up by one.", 
                options = [
                    interactions.Option(
                        name = "encounterid",
                        description = "The ID of your encounter",
                        type = 4,
                        required = True
                    )
                ]
            )
async def initnext(ctx, encounterid):
    initiative = sqlite3.connect('init.db')
    current = initiative.execute(f"SELECT CURRENT FROM ENCOUNTER WHERE EID = {encounterid};")
    current = current.fetchone()
    if current == None:
        await ctx.send(f"Specified encounter does not exist. Please try again!")
    else:
        current = current[0] #The sql query is a 2-dimensional array. This takes the top row of the table. Based on the table ENCOUNTER, which is updated last. This is whoever just went.
        track = initiative.execute(f"SELECT * FROM CHARACTER WHERE EID = {encounterid} ORDER BY INIT DESC;")
        top = track.fetchone() #This also takes the top row of the new table, with different behavior: deletes the row from track. This is whoever has the highest initiative, not whoever's next.
        topName = top[1] #Character Name is the second value in table CHARACTER. This is their name.
        if topName != current: #Case: the person who just went did not have the highest initiative. This means we have to iterate through the table until we find the character with that name.
            currTrack = track.fetchone() #Who's next in the table, after "top" (aka the person who just went)? currTrack = current character the iterator is looking at.
            if currTrack != None: #Once it's None, we've reached the end of the table and must loop back to the top.
                currName = currTrack[1] #Once again, Character Name is the second value.
            while (currName != current) and (currTrack != None): #Scroll through until we find whoever just went.
                currTrack = track.fetchone()
                if currTrack != None:
                    currName = currTrack[1]
        currTrack = track.fetchone() #Once we've found who's currently up, we just head up to the next person in line. Finally! And if the last person to go was top, we already know who's next. No need for a while loop.
        if currTrack == None:
            currTrack = top
        try:
            owner = await interactions.get(client, interactions.Member, parent_id=ctx.guild_id, object_id=currTrack[2])
            if currTrack != None:
                await ctx.send(f"It is {owner.mention}'s turn as {currTrack[1]}.")
                initiative.execute(f"UPDATE ENCOUNTER SET CURRENT = '{currTrack[1]}' WHERE EID = {encounterid};")
            else:
                await ctx.send(f"It is {owner.mention}'s turn as {topName}.")
                initiative.execute(f"UPDATE ENCOUNTER SET CURRENT = '{top[1]}' WHERE EID = {encounterid};")
            initiative.commit()
        except: 
            await ctx.send(f"Could not find {currTrack[1]}'s owner in this server. Are you sure you're in the right place?", ephemeral = True)
            print(traceback.format_exc())
    initiative.close()
            
#Moves the initiative tracker up by 1
@init.subcommand(name="order",
                description = "View an encounter's initiative order.", 
                options = [
                    interactions.Option(
                        name = "encounterid",
                        description = "The ID of your encounter",
                        type = 4,
                        required = True
                    )
                ]
            )
async def initorder(ctx, encounterid):
    initiative = sqlite3.connect('init.db')
    current = initiative.execute(f"SELECT * FROM ENCOUNTER WHERE EID = {encounterid};")
    current = current.fetchone()
    if current == None:
        await ctx.send(f"Specified encounter does not exist. Please try again!")
    else:
        track = initiative.execute(f"SELECT * FROM CHARACTER WHERE EID = {encounterid} ORDER BY INIT DESC;")
        msgContent = f"**Initiative Order** `{encounterid}`\n```"
        try:
            for row in track:
                if row[1] == current[2]:
                    msgContent = msgContent + f"-↓-↓-↓-This character's turn-↓-↓-↓-\n"
                owner = await interactions.get(client, interactions.Member, parent_id=ctx.guild_id, object_id=row[2])
                msgContent = msgContent + f"{row[3]}: {row[1]}, played by {owner.name}\n"
            msgContent = msgContent + f"```"
            await ctx.send(content = msgContent)
        except:
            await ctx.send(f"Could not find at least one player in this encounter within the current server. Is this the right place?", ephemeral=True)
            print(traceback.format_exc())
    initiative.close()
     

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
            dieRoll = random.randint(min,max)
        rollList.append(dieRoll)
        result = result + dieRoll
    del rollList[0];
    return result, rollList

while True:
    try:
        client.start()
    except:
        print("Bot crashed. Did we lose connection?")
        print(traceback.format_exc())