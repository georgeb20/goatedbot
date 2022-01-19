import discord
import time
import datetime
from discord.ext import commands
from discord.utils import get
import asyncio
import json
from discord.utils import find


#allow member intents to view all guild members
intents = discord.Intents.default()
intents.members =  True

#initalize Bot
bot = commands.Bot(command_prefix='!',intents=intents)

#initalizes a server
def initalize_server(sid,current_time):
    server_json={
                "sid": sid,
                "past_time": current_time,
                "current_time": 0,
                "change": 0,
                "former_goat":0,
                "user": []
            }

    return server_json

#initalizes a user
def initalize_user(uid,time):
    user_json={
                "id": uid,
                "seconds": time
            }
    return user_json

#write back json data
def write_json_all(data,filename="db.json"):
    with open(filename,"w") as f:
        json.dump(data,f,indent=4)
        f.close()

#write back server data
def write_json_server(server_json):
    with open("db.json","r") as json_file:
        data_all = json.load(json_file)
        data_all["serverid"].append(server_json)
        write_json_all(data_all)
     
#returns the index of the guild in ["serverid"] array
def get_sid_index(ctx):
    with open("db.json") as json_file:
        data_all = json.load(json_file)
        for i in range(len(data_all["serverid"])):
            if data_all["serverid"][i]["sid"]==ctx.message.guild.id:
                return i
        return -1

#returns formatted time, times is in seconds
def format_time(times):
    return datetime.timedelta(seconds=int(times))


#wakeup bot and prepare database
@bot.event
async def on_ready():
    print("I am running on " + bot.user.name)
    print('Bot is ready to be used')
    with open('db.json',"r") as json_file:
        data_all = json.load(json_file)

        #the "past_time" is the time the bot started
        for i in data_all["serverid"]:
            i["past_time"]=time.time()
            i["current_time"]=0
            i["change"]=0
    
        write_json_all(data_all)


#adds goated role to server
#adds server to database
@bot.command()
async def initalize(ctx):
    if get(ctx.guild.roles, name="goated"):
        await ctx.send("Goated role already exists.")
    else:
        #goated role is created
        await ctx.guild.create_role(name="goated", colour=discord.Colour(0x1f8b4c))
        await ctx.send("Goated role added.")
    
    if(get_sid_index(ctx)==-1):
        #initalize server and append server to json
        server_json = initalize_server(sid=ctx.message.guild.id,current_time=time.time())
        write_json_server(server_json)

    await ctx.send("Server is initalized. Type !command to view available commands. Enjoy! :goat:")

#removes goated role from previous goat and gives it to message author
@bot.command()
async def goated(ctx):
    #flag to determine if no action is required
    skip_goat=0
    #goated role
    goated = discord.utils.get(ctx.guild.roles,name='goated')

    #iterate through users in guild
    async for user in ctx.guild.fetch_members(limit=None):
        #if they have goated as one of their roles
        if goated in user.roles:
            #if the message author is the same as the current goat, we pass
            if user.id == ctx.author.id:
                await ctx.send(f'{user.mention} you are already goated :goat:')
                skip_goat=1
                break

            with open("db.json") as json_file:
                db = json.load(json_file)
            
            #get the index of the server in the database
            server_index = get_sid_index(ctx)

            #if the message author is the same as the previous goat, we pass
            if ctx.author.id == db["serverid"][server_index]["former_goat"]:
                await ctx.send(f'{user.mention} former goats need a break')
                skip_goat=1
                break

            #set the current time to time.time()
            db["serverid"][server_index]["current_time"] = time.time()
            #calculate the change in time as change = current_time-past_time
            db["serverid"][server_index]["change"] = db["serverid"][server_index]["current_time"]-db["serverid"][server_index]["past_time"]
            #the new past time is the current_time
            db["serverid"][server_index]["past_time"] = db["serverid"][server_index]["current_time"]

            goated = discord.utils.get(ctx.guild.roles,name='goated')    

            #print the previous goat and their "change" which is how long they were goated
            await ctx.send(f'{user} was goated for {format_time(db["serverid"][server_index]["change"])}')
            await user.remove_roles(goated)

            #set the former goat as the previous goat
            db["serverid"][server_index]["former_goat"]=user.id

            temp = db["serverid"][server_index]["user"]

            #create flag to determine if user exists in database
            flag = 0
            for i in range(len(temp)):
                if user.id == temp[i]["id"]:
                    #if they do, add their change in time to their previous time
                    temp[i]["seconds"] = temp[i]["seconds"]+db["serverid"][server_index]["change"]
                    flag = 1
            if flag == 0:
                #if they do not, initalize the user and append to database
                temp_user = initalize_user(user.id,db["serverid"][server_index]["change"])
                temp.append(temp_user)


            write_json_all(db)
            break

    if skip_goat==1:
        pass
    else:
        #set new goat as the message author
        await ctx.send(f'{ctx.author.mention} is now the goat :goat:')
        role = discord.utils.get(ctx.author.guild.roles,name='goated')
        await ctx.author.add_roles(role)

#prints top goats in guild
@bot.command()
async def scoreboard(ctx):
    # Opening JSON file
    with open("db.json") as json_file:    
        data_all = json.load(json_file)

    #get the index of the server in the database
    server_index=get_sid_index(ctx)
    data = data_all["serverid"][server_index]

    #determine how many users to display in scoreboard, min 0, max 5
    num_scoreboard = min(len(data_all["serverid"][server_index]["user"]),5)

    if num_scoreboard==0:
        #if nobody is in user array, we can't display a scoreboard
        await ctx.send('Nobody has been goated yet!')
    else:
        #sort json by seconds
        def sort_by_key(list):
            return list['seconds']
        
        sorted_version=sorted(data["user"], key=sort_by_key,reverse=True)[0:num_scoreboard]
        
        #initalize scoreboard message
        msg='```'
        for i in range(num_scoreboard):
            name = await bot.fetch_user(sorted_version[i]["id"])
            time = format_time(sorted_version[i]["seconds"])
            #create a format string containg the top users and their times, append to msg
            msg=msg+ f'#{i+1} is {name} with {time}\n'
        msg=msg+'```'
        #send message
        await ctx.send(msg)

#prints the time of a specific user, can be used as !gtime or !gtime @user
@bot.command()
async def gtime(ctx,member:discord.Member=None):
    if member is None:
        #if member isn't provided, set member to the message author
        member = ctx.message.author
    with open('db.json') as json_file:
        _data=json.load(json_file)
    
    #get the index of the server in the database
    server_index=get_sid_index(ctx)
    usr_list = _data["serverid"][server_index]["user"]
    #flag to determine if user exists in database
    flag = 0
    for i in range(len(usr_list)):
        if member.id == usr_list[i]["id"]:
            flag=1
            time=format_time(usr_list[i]["seconds"])
            #print name and their time
            await ctx.send(f'{member.mention} has been goated for {time} seconds.')
    #if user doesn't exist
    if flag == 0:
        await ctx.send(f'{member.mention} has never been goated! :x: :goat:')

#contains all available commands
@bot.command()
async def command(ctx):
    await ctx.send("```!initalize -> sets up the server \n!goated -> remove the goated role from the last user and gives it to you \n!scoreboard -> shows top 5 goats \n!gtime @user -> displays the user's total goated time```")

#place token to run bot
bot.run('place_client_id_here')
