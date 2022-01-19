import discord
import time
import datetime
from discord.ext import commands
from discord.utils import get
import asyncio
import json


intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.',intents=intents)

def initalize_server(sid,current_time):
    server_json={
                "sid": sid,
                "past_time": current_time,
                "current_time": 0,
                "change": 0,
                "former_goat":133226230730611769,
                "user": []
            }

    return server_json

def initalize_user(uid,time):
    user_json={
                "id": uid,
                "seconds": time
            }
    return user_json

def write_json_all(data,filename="dbb.json"):
    with open(filename,"w") as f:
        json.dump(data,f,indent=4)
        f.close()


def write_json_server(server_json):
    with open("dbb.json","r") as json_file:
        data_all = json.load(json_file)
        data_all["serverid"].append(server_json)
        write_json_all(data_all)
     

def get_sid_index(ctx):
    with open("dbb.json") as json_file:
        data_all = json.load(json_file)
        for i in range(len(data_all["serverid"])):
            if data_all["serverid"][i]["sid"]==ctx.message.guild.id:
                return i
        return -1

def format_time(times):
    return datetime.timedelta(seconds=int(times))


@bot.event
async def on_ready():
    print("I am running on " + bot.user.name)
    print('Bot is ready to be used')
    with open('dbb.json',"r") as json_file:
        data_all = json.load(json_file)

        for i in data_all["serverid"]:
            i["past_time"]=0
            i["current_time"]=time.time()
            i["change"]=0
    
        write_json_all(data_all)



@bot.command()
async def initalize(ctx):
    if get(ctx.guild.roles, name="goatedd"):
        await ctx.send("Goated role already exists.")
    else:
        await ctx.guild.create_role(name="goatedd", colour=discord.Colour(0xf807c6))
        await ctx.send("Goated role added.")
    
    if(get_sid_index(ctx)==-1):
        server_json = initalize_server(sid=ctx.message.guild.id,current_time=time.time())
        write_json_server(server_json)

    await ctx.send("Server is initalized. Type !command to view available commands. Enjoy! :goat:")

@bot.command()
async def goated(ctx):
    skip_goat=0
    goated = discord.utils.get(ctx.guild.roles,name='goatedd')
    async for user in ctx.guild.fetch_members(limit=None):
        if goated in user.roles:
            if user.id == ctx.author.id:
                await ctx.send(f'{user.mention} you are already goated :goat:')
                skip_goat=1
                break

            with open("dbb.json") as json_file:
                db = json.load(json_file)
                
            server_index = get_sid_index(ctx)

            if ctx.author.id == db["serverid"][server_index]["former_goat"]:
                await ctx.send(f'{user.mention} former goats need a break')
                skip_goat=1
                break

            db["serverid"][server_index]["current_time"] = time.time()
            db["serverid"][server_index]["change"] = db["serverid"][server_index]["current_time"]-db["serverid"][server_index]["past_time"]
            db["serverid"][server_index]["past_time"] = db["serverid"][server_index]["current_time"]

            goated = discord.utils.get(ctx.guild.roles,name='goatedd')    

            await ctx.send(f'{user} was goated for {format_time(db["serverid"][server_index]["change"])}')
            await user.remove_roles(goated)

            db["serverid"][server_index]["former_goat"]=user.id

            temp = db["serverid"][server_index]["user"]

            flag = 0
            for i in range(len(temp)):
                if user.id == temp[i]["id"]:
                    temp[i]["seconds"] = temp[i]["seconds"]+db["serverid"][server_index]["change"]
                    flag = 1
            if flag == 0:
                temp_user = initalize_user(user.id,db["serverid"][server_index]["change"])
                temp.append(temp_user)


            write_json_all(db)
            break

    if skip_goat==1:
        pass
    else:
        await ctx.send(f'{ctx.author.mention} is now the goat :goat:')
        role = discord.utils.get(ctx.author.guild.roles,name='goatedd')
        await ctx.author.add_roles(role)

@bot.command()
async def scoreboard(ctx):
    # Opening JSON file
    with open("dbb.json") as json_file:    
        data_all = json.load(json_file)


    server_index=get_sid_index(ctx)
    data = data_all["serverid"][server_index]

    num_scoreboard = min(len(data_all["serverid"][server_index]["user"]),5)

    if num_scoreboard==0:
        await ctx.send('Nobody has been goated yet!')
    else:
        def sort_by_key(list):
            return list['seconds']
        
        sorted_version=sorted(data["user"], key=sort_by_key,reverse=True)[0:num_scoreboard]
        msg='```'
        for i in range(num_scoreboard):
            name = await bot.fetch_user(sorted_version[i]["id"])
            time = format_time(sorted_version[i]["seconds"])
            msg=msg+ f'{i+1}) is {name} with {time}\n'
        msg=msg+'```'

        await ctx.send(msg)

@bot.command()
async def gtime(ctx,member:discord.Member=None):
    if member is None:
        member = ctx.message.author
    with open('dbb.json') as json_file:
        _data=json.load(json_file)
    

    server_index=get_sid_index(ctx)
    usr_list = _data["serverid"][server_index]["user"]
    flag = 0
    for i in range(len(usr_list)):
        if member.id == usr_list[i]["id"]:
            flag=1
            time=format_time(usr_list[i]["seconds"])
            await ctx.send(f'{member.mention} has been goated for {time} seconds.')
            
    if flag == 0:
        await ctx.send(f'{member.mention} has never been goated! :x: :goat:')

bot.run('place_client_id_here')