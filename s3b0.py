#!/usr/bin/env python3
import discord
import re
import logging
import asyncio
from dotenv import dotenv_values
from random import randint

logging.basicConfig(level=logging.INFO)

client = discord.Client()
discord.opus.load_opus
roll_command = "/sd"
img_base="https://raw.githubusercontent.com/Erik-Krieger/s3b0-reloaded/master/images/alpha/"

Advantage="Advantage"
Despair="Despair"
Failure="Failure"
Success="Success"
Threat="Threat"
Triumph="Triumph"
Dark="Dark"
Light="Light"

White=0xFFFFFF
Gray=0x95a5a6
Black=0x000000
Green=0x2ecc71
Gold=0xf1c40f
Red=0xe74c3c
DarkRed=0x992d22
LightPip = u"\u26AA"
DarkPip = u"\u26AB"

AssociationDict = {
    'green': 'a',
    #'grün': 'a',
    'yellow': 'p',
    'gelb': 'p',
    'red': 'c',
    'rot': 'c',
    'purple': 'd',
    'lila': 'd',
    'blue': 'b',
    'blau': 'blau',
    'black': 's',
    'schwarz': 's',
    'white': 'f',
    'weiß': 'f'
}

FirstConnect=True
LastPlayingIndex=-1
PlayingQuotes = {
        1: "with det-cord",
        2: "dejarik with a Wookiee",
        3: "in a cantina band",
        4: "with CGI 'remastering'",
        5: "with midichlorians",
        6: "the Imperial March",
        7: "Duel of the Fates"
    }

class Die:
    rollResolve = {}

    def roll(self):
        result=rollDie(min=1,max=len(self.rollResolve))
        resolve=self.rollResolve[result]
        return (str(result), resolve)

class AbilityDie(Die):
    rollResolve = {
        1: [],
        2: [Success],
        3: [Success],
        4: [Success,Success],
        5: [Advantage],
        6: [Advantage],
        7: [Success,Advantage],
        8: [Advantage,Advantage]
    }

class BoostDie(Die):
    rollResolve = {
        1: [],
        2: [],
        3: [Success],
        4: [Success, Advantage],
        5: [Advantage,Advantage],
        6: [Advantage]
    }

class ChallengeDie(Die):
    rollResolve = {
        1: [],
        2: [Failure],
        3: [Failure],
        4: [Failure,Failure],
        5: [Failure,Failure],
        6: [Threat],
        7: [Threat],
        8: [Failure,Threat],
        9: [Failure,Threat],
        10: [Threat,Threat],
        11: [Threat,Threat],
        12: [Despair]
    }

class DifficultyDie(Die):
    rollResolve = {
        1: [],
        2: [Failure],
        3: [Failure,Failure],
        4: [Threat],
        5: [Threat],
        6: [Threat],
        7: [Threat,Threat],
        8: [Failure,Threat]
    }

class ForceDie(Die):
    rollResolve = {
        1: [Dark],
        2: [Dark],
        3: [Dark],
        4: [Dark],
        5: [Dark],
        6: [Dark],
        7: [Dark,Dark],
        8: [Light],
        9: [Light],
        10: [Light,Light],
        11: [Light,Light],
        12: [Light,Light]
    }

class ProficiencyDie(Die):
    rollResolve = {
        1: [],
        2: [Success],
        3: [Success],
        4: [Success,Success],
        5: [Success,Success],
        6: [Advantage],
        7: [Success,Advantage],
        8: [Success,Advantage],
        9: [Success,Advantage],
        10: [Advantage,Advantage],
        11: [Advantage,Advantage],
        12: [Triumph]
    }

class SetbackDie(Die):
    rollResolve = {
        1: [],
        2: [],
        3: [Failure],
        4: [Failure],
        5: [Threat],
        6: [Threat]
    }

class DiceResult:
    def __init__(self):
        self.title=""
        self.desc=""
        self.colour=Green
        self.img=None

class DicePool:
    def __init__(self):
        self.Advantages=0
        self.Despairs=0
        self.Failures=0
        self.Successes=0
        self.Threats=0
        self.Triumphs=0
        self.Dice=[]

    def roll(self):
        for die in self.Dice:
            result=die.roll()
            resultNum=result[0]
            resultResolved=result[1]
            for resolved in resultResolved:
                if resolved==Advantage:
                    self.Advantages+=1
                if resolved==Despair:
                    self.Despairs+=1
                if resolved==Failure:
                    self.Failures+=1
                if resolved==Success:
                    self.Successes+=1
                if resolved==Threat:
                    self.Threats+=1
                if resolved==Triumph:
                    self.Triumphs+=1

    def resolveForce(self):
        result = ""
        nLight = 0
        nDark = 0
        retResult = DiceResult()
        for die in self.Dice:
            result=die.roll()
            resultNum=result[0]
            resultResolved=result[1]
            retResult.desc = retResult.desc + "["
            for resolved in resultResolved:
                if resolved==Light:
                    retResult.desc = retResult.desc + LightPip
                    nLight+=1
                if resolved==Dark:
                    retResult.desc = retResult.desc + DarkPip
                    nDark+=1
            retResult.desc = retResult.desc + "] "

        retResult.colour=Gray
        if (nLight > 0):
            retResult.title = retResult.title + "Light (" + str(nLight) + ") "
            if (nDark == 0):
                retResult.colour=White
        if (nDark > 0):
            retResult.title = retResult.title + "Dark (" + str(nDark) + ")"
            if (nLight == 0):
                retResult.colour=Black

        return retResult

    def resolve(self):
        for die in self.Dice:
            if type(die).__name__ == "ForceDie":
                return self.resolveForce()
        
        self.roll()
        result = ""
        retResult = DiceResult()
        retImg=""
        
        if self.Triumphs > 0:
            result = result + "Triumph ("+ str(self.Triumphs) +")! "
            retImg = retImg + "Tr"
        if self.Despairs > 0:
            result = result + "Despair ("+ str(self.Despairs) +")! "
            retImg = retImg + "D"
        if (self.Advantages > self.Threats):
            result = result + "Advantage ("+ str(self.Advantages - self.Threats) +")! "
            retImg = retImg + "A"
        if (self.Advantages < self.Threats):
            result = result + "Threat ("+ str(self.Threats - self.Advantages) +")! "
            retImg = retImg + "Th"
        if (self.Successes + self.Triumphs) > (self.Failures + self.Despairs):
            i = (self.Successes + self.Triumphs) - (self.Failures + self.Despairs)
            result = result + "Success ("+ str(i) +")! "
            retImg = retImg + "S"
        if (self.Successes + self.Triumphs) < (self.Failures + self.Despairs):
            i = (self.Failures + self.Despairs) - (self.Successes + self.Triumphs)
            result = result + "Failure ("+ str(i) +")! "
            retImg = retImg + "F"
        if (self.Successes + self.Triumphs) == (self.Failures + self.Despairs):
            result = result + "Failure (0)! "
            retImg = retImg + "F"                

        retImg = retImg + ".png"
        retResult.title=result
        retResult.img=retImg
        result=""

        if self.Triumphs > 0:
            result = result + str(self.Triumphs) + " Triumph, "
        if self.Successes > 0:
            result = result + str(self.Successes) + " Success, "
        if self.Despairs > 0:
            result = result + str(self.Despairs) + " Despair, "
        if self.Failures > 0:
            result = result + str(self.Failures) + " Failure, "
        if self.Advantages > 0:
            result = result + str(self.Advantages) + " Advantage, "
        if self.Threats > 0:
            result = result + str(self.Threats) + " Threat, "
        if result.endswith(', '):
            result=result[:-2]
        retResult.desc=result

        # colour stuff
        if (self.Successes + self.Triumphs) < (self.Failures + self.Despairs):
            retResult.colour=Green
            if (self.Triumphs > 0) and (self.Despairs == 0) and (self.Advantages - self.Threats >= 0):
                retResult.colour=Gold
        if (self.Successes + self.Triumphs) < (self.Failures + self.Despairs):
            retResult.colour=Red
            if (self.Despairs > 0) and (self.Triumphs == 0) and (self.Threats - self.Advantages >= 0):
                retResult.colour=DarkRed
        if (self.Successes + self.Triumphs) == (self.Failures + self.Despairs):
            retResult.colour=Red
            if (self.Despairs > 0) and (self.Triumphs == 0) and (self.Threats - self.Advantages >= 0):
                retResult.colour=DarkRed
        
        return retResult

def checkForAlternateDieNames(diename: str) -> str:
    shortcode = ""
    try:
        shortcode = AssociationDict[diename]
    except KeyError:
        shortcode = diename
    except:
        print("Something went horribly wrong.")
    return shortcode

def getDie(diename: str) -> Die:
    shortcode = checkForAlternateDieNames(diename)
    die = None
    if shortcode == 'a':
        die = AbilityDie()
    if shortcode == 'b':
        die = BoostDie()
    if shortcode == 'c':
        die = ChallengeDie()
    if shortcode == 'd':
        die = DifficultyDie()
    if shortcode == 'f':
        die = ForceDie()
    if shortcode == 'p':
        die = ProficiencyDie()
    if shortcode == 's':
        die = SetbackDie()
    return die

def splitIntoDigitsAndLetters(string_t: tuple) -> list:
    string = string_t[0]
    l = []
    for i in range(len(string) - 1):
        if string[i + 1].isalpha():
            l = [string[:i+1], string[i+1:]]
            return l
    raise Exception("The command is invalid!")

def parseRoll(diceString: str):
    # Variable definition
    fail="Unable to parse dice command. Please see " + roll_command + " for usage"
    #dice=[x for x in re.split('(\d*?[abcdfhpst])',diceString) if x]
    dice=[x for x in re.split('([\d]+[a-zA-Z]+)',diceString) if x]
    
    # Error handling
    if len(dice) == 0:
        return fail

    if len(dice) > 1 and ('t' in diceString or 'h' in diceString):
        return "Can't chain d10 or d100 rolls!"
    
    if len(dice) > 1 and ('f' in diceString):
        return "Can't chain Force die rolls!"

    # Actual parsing
    dp = DicePool()
    for die in dice:
        #s=re.search('(\d*?)([abcdfhpst])', die)
        # if not s:
        #     die="1"+die
        # s=re.search('(\d*?)([abcdfhpst])', die)
        s=re.search('([\d]+[a-zA-Z]+)', die)
        if not s:
            return fail
        g=s.groups()
        # if len(g) != 2:
        #     return fail
        
        l = splitIntoDigitsAndLetters(g)

        try:
            num=int(l[0])
        except:
            num=1
            print(l)
        dieCode=l[1]

        # if d10 or d100 rolls:
        if dieCode == 't' or dieCode == 'h':
            total=0
            results=[]
            d=10
            if dieCode == 'h':
                d=100
            for i in range(num):
                result=rollDie(min=1,max=d)
                results.append(result)
                total=total+result
            return str(total) + " ("+ '+'.join(map(str,results))+ ")"
        # if normal star wars roll:
        for i in range(num):
            d = getDie(dieCode)
            if not d:
                return fail
            dp.Dice.append(d)
    return dp.resolve()

def rollDie(min=1, max=6):
    result = randint(min,max)
    return result

async def cyclePlaying():
    global LastPlayingIndex
    playing=PlayingQuotes[randint(1,len(PlayingQuotes))]
    while playing == LastPlayingIndex:
        playing=PlayingQuotes[randint(1,len(PlayingQuotes))]
    LastPlayingIndex=playing
    await client.change_presence(activity=discord.Game(playing))
    await asyncio.sleep(randint(60,600))

@client.event
async def on_ready():
    global FirstConnect
    print("S3B0 connected")
    if FirstConnect:
        FirstConnect = False
        while True:
            await asyncio.ensure_future(cyclePlaying())
        
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == roll_command:
        msg = """```
/sd [[number=1][die type]]...

Die Types:
    a: Ability
    p: Proficiency
    c: Challenge
    d: Difficulty
    b: Boost
    s: Setback
    f: Force (can't be chained)
    t: Ten (d10) (can't be chained)
    h: Hundred (d100) (can't be chained)

Example:
    /sd 3a1p2c1b2s
    /sd 3f
    /sd h
```"""
        await message.channel.send(msg)
        return
    if message.content.startswith(roll_command):
        result = parseRoll(message.content[len(roll_command)+1:])
        if isinstance(result, str):
            await message.channel.send(result)
        else:
            em = discord.Embed(title=result.title, description=result.desc, colour=result.colour)
            if result.img:
                em.set_image(url=img_base+result.img)
            else:
                em.set_footer(text=result.desc)
                em.description=None
            await message.channel.send(embed=em)

# Retrieve the bot key from the external file.
token = dotenv_values("secret.env")["S3B0_TOKEN"]

client.run(token)
