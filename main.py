import discord
from discord.ext import commands
import pickle
import random
from save import *
from init_files import *
from level_up import *
import datetime as date

intents = discord.Intents.default()
intents.typing = False  # Optional: Disable typing events if not needed
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix=';', intents=intents)

# Define the file where character data will be stored
CHARACTER_DATA_FILE = 'character_data.pkl'
MONSTER_DATA_FILE = 'monster_data.pkl'
SHOP_DATA_FILE = 'shop.pkl'
BOSS_DATA_FILE = 'boss_data.pkl'
QUEST_DATA_FILE = 'quest_data.pkl'
DEV_TOKEN = 'devtoken.txt'
RUN_TOKEN = 'runtoken.txt'

# Load character data from the file, if it exists
try:
    with open(CHARACTER_DATA_FILE, 'rb') as file:
        character_sheets = pickle.load(file)
except FileNotFoundError:
    character_sheets = {}

# Quest data
try:
    with open(QUEST_DATA_FILE, 'rb') as file:
        quest_data = pickle.load(file)
except FileNotFoundError:
    quest_data = []

# Moderator list
try:
    with open("moderators.pkl", "rb") as f:
        moderators = pickle.load(f)
except FileNotFoundError:
    moderators = {}

# Load shop data
try:
    with open("shop.pkl", "rb") as f:
        shop_items = pickle.load(f)
except FileNotFoundError:
    shop_items = []

# Load monster data from the file, if it exists
try:
    with open(MONSTER_DATA_FILE, 'rb') as file:
        monsters = pickle.load(file)
except FileNotFoundError:
    monsters = []

# Boss data
try:
    with open(BOSS_DATA_FILE, 'rb') as file:
        boss_data = pickle.load(file)
except FileNotFoundError:
    boss_data = []


@bot.event
async def on_ready():
    print(f"We are rolling under the name of: {bot.user.name}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command is on cooldown, you can use it in {round(error.retry_after, 2)} seconds')


sessh_create_char = 0
# COMMANDS START:
@bot.command(name="createcharacter")
async def create_character(ctx):
    sessh_create_char += 1
    print(f'Created character for {ctx.author.name} #{sessh_create_char} this session')
    user = ctx.author
    if user.id in character_sheets:
        await ctx.send("You have already created a character")
        return
    restart(character_sheets, user.id)
    await ctx.send(f"Welcome to this world little one {user.mention}")
    save_character_data(CHARACTER_DATA_FILE, character_sheets)


@bot.command(name="info")
async def info(ctx):
    user = ctx.author
    if user.id not in character_sheets:
        await ctx.send("Create a character with the command ``createcharacter``")
        return
    
    character = character_sheets[user.id]
    # hp level xp dmg kill_list inventory quests

    

    hp = character['hp']
    level = character['level']
    xp = character['xp']
    dmg = character['dmg']
    balance = character['balance']
    farming = character['farming']
    kill_list = character['kill_list']
    inventory = character['inventory']

    embed = discord.Embed(
        title=f"{user.display_name}'s Character Info",
        color=0x00ff00
    )

    list_kills = ""
    for i in kill_list:
        list_kills += i + ", "
    
    inventory_list = ""
    for item in inventory:
        if item['count'] > 0:
            inventory_list += f"{item['count']} {item['name']} with level {item['level']}\n"


    embed.add_field(name="Health", value=f"{hp}")
    embed.add_field(name="Level", value=f"{level}")
    embed.add_field(name="Experience", value=f"{xp}/{character['level'] * 250 * character['level']/10}")
    embed.add_field(name="Farming", value=f"{farming}")
    embed.add_field(name="Dmg (max)", value=f"{dmg}")
    embed.add_field(name="Balance", value=f"{balance}$")
    if not inventory_list == "":
        embed.add_field(name="Inventory", value=f"{inventory_list}", inline=False)

    await ctx.send(embed=embed)

@bot.command(name="shop")
@commands.cooldown(1, 3, commands.BucketType.user)
async def shop(ctx):
    embed = discord.Embed(
        title=f"Server's Shop",
        color=0x002313
    )

    for item in shop_items:
        embed.add_field(name=f"{item['name']}", value=f"buy price: {item['price']} \nsell price: {item['sell']}")

    await ctx.send(embed=embed)

# planting:
# > date_planted: date, when_grown: date, name: str, count: int
@bot.command(name="plant")
async def plant(ctx, plant_name: str = None, n: int = 1):
    if plant_name == None:
        await ctx.send("Correct command usage: plant <plant name> <count (optional)> (without the <>)")
        return
    user = ctx.author
    character = character_sheets[user.id]

    a = 0
    plantable_items = [
        "carrot",
        "apple",
        "potato",
        "orange",
        "pumpkin"
    ]

    for item in character['inventory']:
        if item['name'] == plant_name:
            if item['count'] < n:
                await ctx.send('Invalid number of plant')
                return
            if not plant_name in plantable_items:
                await ctx.send(f"You can not plant {plant_name} or you do not own the item!")
                return
            item['count'] -= n
            a = item
            break


    m = False
    for plnt in character['farm']:
        if plnt['name'] == plant_name:
            m = True
            plnt['count'] += n
            plnt['harvest'] = date.datetime.now() + date.timedelta(hours=a['level'])
            await ctx.send(f"You have right now {plnt['count']} {plnt['name']}'s in your farm")
            break
    
    if not m:
        plnt = {
            'planted': date.datetime.now(), 
            'harvest': date.datetime.now() + date.timedelta(hours=a['level']),
            'name': plant_name,
            'count': n
            }
        character['farm'].append(plnt)
        await ctx.send(f"You have planted {plnt['name']} which can be harvested in {plnt['harvest']}")
    save_character_data(CHARACTER_DATA_FILE, character_sheets)

@bot.command(name="farm")
async def farm(ctx):
    user = ctx.author
    character = character_sheets[user.id]
    embed = discord.Embed(
        title=f"{user.display_name}'s Farm",
        color=0x00ff00
    )
    m = False 
    for plants in character['farm']:
       harvest_in = plants['harvest'] - date.datetime.now()
       embed.add_field(name=f"{plants['count']} {plants['name']}", value=f"Can be harvested in {harvest_in}", inline=False)
       m = True
    if not m:
        await ctx.send(f'Oops, something went wrong')
    
    await ctx.send(embed=embed)

@bot.command(name="harvest")
async def harvest(ctx, item: str = None):
    user = ctx.author
    character = character_sheets[user.id]

    found = False
    for plant in character['farm']:
        if plant['name'] == item:
            found = True
            if plant['harvest'] <= date.datetime.now():
                n = 0
                for i in range(plant['count']):
                    n += random.randint(0,character['farming']+1)
                
                character['inventory'] = await add_to_inventory(plant['name'], character, n, character['farming'])
                character['farm'].remove(plant)
                await ctx.send(f"You have harvested the {n} {plant['name']}")

            else:
                await ctx.send(f'Cannot harvest yet, you can harvest {plant["name"]} in {plant["harvest"] - date.datetime.now()}')
    if not found:
            await ctx.send(f'Invalid plant name')
            await farm(ctx)


    save_character_data(CHARACTER_DATA_FILE, character_sheets)

@bot.command(name="hunt")
@commands.cooldown(1,30, commands.BucketType.user)
async def hunt(ctx):
    user = ctx.author
    character = character_sheets[user.id]

    rewards = ["good", "bad"]
    choice = random.choice(rewards)
    if choice == "good":
        entities = ["boar", "bug", "elf", "slime"]
        reward = random.choice(entities)
        character['inventory'] = await add_to_inventory(reward, character,1,character['level'] + random.randint(0,3))
        await ctx.send(f"You have hunted down {reward}")
        character['xp'] += 20
    else:
        n = 5 * character['level']
        character['hp'] -= n
        await ctx.send(f"You have lost {n}HP")



    save_character_data(CHARACTER_DATA_FILE, character_sheets)
        


@bot.command(name="walkaround")
@commands.cooldown(1, 30, commands.BucketType.user)
async def walkaround(ctx):
    user = ctx.author
    chance = random.choice(['item','number'])
    character = character_sheets[user.id]

    if chance == 'item':
        what = random.choice(['carrot','apple'])
        n = random.randint(1,character['farming'])
        await ctx.send(f'You have farmed {what} {n} times')
        character['inventory'] = await add_to_inventory(what,character,n,1)
                
        character['farming_xp'] += 10
        character['farming'] += farm_level_up(character)
    
    elif chance == 'number':
        what = random.choice(['level','money'])
        if what == 'level':
            n = random.randint(100,150)
            if character['level'] % 2 == 0 and character['level'] >= 20:
                n += character['level'] / 2
            character['xp'] += n

            await ctx.send(f'You have founded xp bottle, it has given you {n} experience!')
        elif what == 'money':
            n = random.randint(100,150)
            character['balance'] += n
            await ctx.send(f'You have found {n}$')

    lvl_up = level_up(character)
    if lvl_up == 1:
        character['level'] += lvl_up
        await ctx.send(f'You have leveled up you are now level {character["level"]}')
        character['xp'] = 0
    save_character_data(CHARACTER_DATA_FILE, character_sheets)

@bot.command(name="buy")
async def buy(ctx,item: str = None,n: int = 1):
    if item == None:
        await ctx.send(f'usage: ``buy <item name> <count (optional)>`` (of course without the <>)')
        return
    user = ctx.author
    character = character_sheets[user.id]
    it = ""
    m = False
    for itms in shop_items:
        if itms['name'] == item and itms['price'] * n <= character['balance']:
            it = itms
            m = True
            break

    if not m:
        await ctx.send(f'Invalid name or insuficient funds!')
        return 
    
    character['balance'] -= it['price'] * n

    # {'name': reward, 'count': 1, 'level': character['level'] + random.randint(0,2)}
    character['inventory'] = await add_to_inventory(it['name'], character, n, 1)
    await ctx.send(f'You have succesfully purchased {n} {it["name"]}s for {it["price"] * n}')

@bot.command(name="balancetop")
async def balancetop(ctx):
    user = ctx.author
    character = character_sheets[user.id]
    sorted_leaderboard = sorted(character_sheets, key=lambda character: character["balance"], reverse=True)
    embed = discord.Embed(
        title=f"Balance top",
        color=0x00ff00
    )
    for rank, character in enumerate(sorted_leaderboard, start=1):
        embed.add_field(name =f"Rank {rank}: {character['name']}", value=f"Balance: {character['balance']}")

    await ctx.send(embed=embed)



@bot.command(name='sell')
async def sell(ctx, item: str = None, n: int = 1):
    if item == None:
        await ctx.send(f'usage: ``sell <item name> <count (optional)>`` (of course without the <>)')
        return
    user = ctx.author
    character = character_sheets[user.id]

    m = False
    lvl = 0
    for a in character['inventory']:
        if a['name'] == item and a['count'] >= n and n > 0:
            a['count'] -= n
            lvl = a['level']
            m = True
    
    if m == False:
        await ctx.send(f'Invalid amount or name given')
        return

    price = int
    m = False
    for i in shop_items:
        if i['name'] == item:
            price = (i['sell']+lvl) * n 
            m = True
    if not m:
        await ctx.send('Invalid name given')
        return
    
    character['balance'] += price
    await ctx.send(f'You have made {price}$ by selling {n} {item}s')
    save_character_data(CHARACTER_DATA_FILE, character_sheets)

    
@bot.command(name='additem')
async def additem(ctx, item: str = None, buy: int = None, sell: int = None):
    if(str == None or buy == None or sell == None):
        await ctx.send(f'Invalid item info input ``<name> <buy> <sell>``')    
        return
    item_a = {'name': item, 'price': buy, 'sell': sell}
    await ctx.send(f"Added {item_a['name']} for {item_a['price']} and sell price {item_a['sell']}")
    shop_items.append(item_a)
    save_shop_data(SHOP_DATA_FILE, shop_items)


with open(DEV_TOKEN) as f:
    token = f.read()

bot.run(token)