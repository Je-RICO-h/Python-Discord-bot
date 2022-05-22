from __future__ import unicode_literals
import discord
import logging
import datetime
import os
import json
import requests
import random
import warnings
import sys
import shutil
import asyncio
import youtube_dl
import re
from bs4 import BeautifulSoup
from random import choice
from urllib import request,error
from discord.ext import commands,tasks
from discord.utils import get

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

forb = ["settings","help","ping","prefix","changeprefix","suggest","enablecommand","disablecommand","checkcommand","info","imgsaver","disablechannels","enablechannels","discominchan","encominchan"]

def CCC(gid,cid,com):
    if os.path.exists(f"Settings/Disabledcommandsinchannel/{gid}") == False:
        return False
    if os.path.getsize(f"Settings/Disabledcommandsinchannel/{gid}") < 5:
        return False
    with open(f"Settings/Disabledcommandsinchannel/{gid}","r") as f:
        x = json.load(f)
    try:
        for i in x[str(com)]:
            if cid.id == i:
                return True
    except KeyError:
        return False
    return False

def CMR(id,cid):
    with open(f"Settings/VoiceSettings/channels","r") as f:
        v = json.load(f)

    try:
        if len(v) == 0 or v[str(id)] == None or v[str(id)] == str(cid):
            return False
        else:
            return True
    except:
        return False

def CIA(command:str,id:str):
    with open(f"Settings/Commands/{id}","r") as f:
        com = json.load(f)
    return com[command]

def CDC(chn,id:str):
    path = f"Settings/Disabledchannels/{id}"
    if os.path.exists(path) == True and os.path.getsize(path) > 5:
        with open(path, "r") as f:
            l = json.load(f)
        if str(chn.name) in l:
            return False
        else:
            return True
    else:
        return True

def CP(id:str,memberid,com:str):
    guild = client.get_guild(int(id))
    memb = guild.get_member(memberid)
    membranks = memb.roles
    with open(f"Settings/Permissions/{id}","r") as f:
        perms = json.load(f)

    if perms["rankperm"] == True:
        with open(f"Settings/Permissions/permrank/{guild.id}","r") as f:
            x = json.load(f)
        try:
            y = x[str(com)]
        except:
            return True
        for i in y:
            for j in membranks:
                if i == j.name:
                    return True
        return False
    return None

def Logg(id):
    with open("Settings/logging.json","r") as f:
        x = json.load(f)
    if x[str(id)] == True:
        return True
    else:
        return False

def get_prefix(client, message):
    with open("Settings/prefixes.json","r") as f:
        prefixes = json.load(f)
        return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix = get_prefix)
client.remove_command("help")

async def loophandler():
    if checkrank.get_task() == None:
        checkrank.start()
    if checktime.get_task() == None:
        checktime.start()
    if checkalarm.get_task() == None:
        checkalarm.start()
    if checkprivate.get_task() == None:
        checkprivate.start()

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Type .help || Have fun!"))
    #await anupdate()
    await loophandler()
    print("Bot is online!")

@tasks.loop(minutes=5)
async def checkprivate():
    time = datetime.datetime.now()
    guilds = os.listdir("Private")
    for i in guilds:
        rooms = os.listdir(f"Private/{i}")
        if len(rooms) == 0:
            continue
        for j in rooms:
            with open(f"Private/{i}/{j}","r") as f:
                save = json.load(f)
            dateobj = datetime.datetime.strptime(save["removed"], '%Y-%m-%d %H:%M:%S.%f')
            if time > dateobj:
                guild = client.get_guild(int(i))
                chan = guild.get_channel(int(save["channel"]))
                vchan = guild.get_channel(int(save["vchannel"]))
                await chan.delete()
                await vchan.delete()
                os.remove(f"Private/{i}/{j}")
    return

@tasks.loop(hours=999)
async def checkafk(id):
    global players
    await asyncio.sleep(300)
    try:
        player = players[id]
    except KeyError:
        checkafk.stop()
        return
    chan = player.channel
    if player.is_playing() == False or len(chan.members) < 2:
        await player.disconnect()
        del players[id], queues[id], val[id], count[id], qu[id], curplaying[id], repeat[id]
        if os.path.exists(f"Queue/{id}"):
            shutil.rmtree(f"Queue/{id}")
    checkafk.stop()
    return


@tasks.loop(minutes=2)
async def checkalarm():
    files = os.listdir("Alarm")
    time = datetime.datetime.now()
    if len(files) == 0:
        return
    for i in files:
        with open(f"Alarm/{i}","r") as f:
            dic = json.load(f)
            dateobj = datetime.datetime.strptime(dic[0], '%Y-%m-%d %H:%M:%S.%f')
        if time >= dateobj:
            memb = discord.utils.get(client.get_all_members(),id=int(i))
            await memb.send(f"**ALARM**: {dic[1]}")
            if dic[2] == True:
                dic[0] = str(time + datetime.timedelta(minutes=int(dic[3])))
                with open(f"Alarm/{i}","w") as f:
                    json.dump(dic,f,indent=4)
            else:
                os.remove(f"Alarm/{i}")
    return

@tasks.loop(minutes=2)
async def checkrank():
    path = "Ranks/autorank"
    files = os.listdir(path)
    time = datetime.datetime.now()
    folders = []
    for i in files:
        if os.path.isdir(path+f"/{i}"):
            folders.append(i)      
    if len(folders) == 0:
        return
    for i in folders:
        fil = path + f"/{i}"
        size = 0
        for files in os.listdir(fil):
            size += os.path.getsize(f"{fil}/{files}")
        if size > 25:
            ranks = os.listdir(fil)
            for j in ranks:
                with open(f"{fil}/{j}","r") as f:
                    dic = json.load(f)
                keys = dic.keys()
                pops =[]
                for x in keys:
                    if x == "freq":
                        continue
                    dateobj = datetime.datetime.strptime(dic[x], '%Y-%m-%d %H:%M:%S.%f')
                    if time >= dateobj:
                        guild = client.get_guild(int(i))
                        memb = guild.get_member(int(x))
                        prom = discord.utils.get(guild.roles,name=j)
                        if memb.top_role.name != "Mute":
                            await memb.add_roles(prom)
                            pops.append(x)
                if len(pops) != 0:
                    for x in pops:
                        dic.pop(x)
                    with open(f"{fil}/{j}","w") as f:
                        json.dump(dic,f,indent=4)
    return

@tasks.loop(minutes=2)
async def checktime():
    if os.path.getsize("Muted/time") < 20:
        return
    else:
        with open("Muted/time","r") as f:
            dic = json.load(f)
        t = datetime.datetime.now()
        keys = dic.keys()
        delkey =[]
        for i in keys:
            dateobj = datetime.datetime.strptime(dic[i],'%Y-%m-%d %H:%M:%S.%f')
            if t >= dateobj:
                membid,guildid = i.split("/")
                guild = client.get_guild(int(guildid))
                member = guild.get_member(int(membid))

                ranks = await guild.fetch_roles()
                membranks = []
                path = f"Muted/{guildid}/"
                f = open(f"{path}{membid}", "r")
                for x in f:
                    if x.strip("\n") == "@everyone":
                        continue
                    membranks.append(x.strip("\n"))
                f.close()
                for x in membranks:
                    for j in ranks:
                        if x == j.name:
                            await member.add_roles(j)
                muterank = get(guild.roles, name="Mute")
                await member.remove_roles(muterank)
                os.remove(f"{path}{membid}")
                delkey.append(i)
        for i in delkey:
            dic.pop(i)
        with open("Muted/time","w") as f:
            json.dump(dic,f,indent=4)
    return

@client.event
async def on_guild_join(guild):
#DefaultPrefix
    with open("Settings/prefixes.json","r") as f:
        prefixes = json.load(f)
        prefixes[str(guild.id)] = "."
    with open("Settings/prefixes.json","w") as f:
        json.dump(prefixes,f, indent=4)
#Defaultjoinchannel
    with open("Settings/join.json","r") as f:
        cache = json.load(f)
    channels = guild.text_channels
    cache[str(guild.id)] = channels[0].id
    with open("Settings/join.json","w") as f:
        json.dump(cache,f, indent=4)
#Description
    with open("Settings/joindesc.json","r") as f:
        desc = json.load(f)
    desc[str(guild.id)] = ""
    with open("Settings/joindesc.json","w") as f:
        json.dump(desc,f, indent=4)
    with open("Settings/leavedesc.json","r") as f:
        desc = json.load(f)
    desc[str(guild.id)] = ""
    with open("Settings/leavedesc.json","w") as f:
        json.dump(desc,f, indent=4)
#DefaultCommands
    with open("Settings/defcoms.json","r") as f:
        comm = json.load(f)
    with open(f"Settings/Commands/{str(guild.id)}","w+") as f:
        json.dump(comm,f, indent=4)
#Logging
    log = {}
    with open("Settings/logging.json","r") as f:
        log = json.load(f)
    log[str(guild.id)] = False
    with open("Settings/logging.json","w") as f:
        json.dump(log,f,indent=4)
    del log
#Permissions
    with open("Settings/defperms.json","r") as f:
        perms = json.load(f)
    with open(f"Settings/Permissions/{guild.id}","w") as f:
        json.dump(perms,f,indent=4)
    with open(f"Settings/Permissions/permrank/{guild.id}","x"):
        pass

@client.event
async def on_guild_remove(guild):
    #prefix
    with open("Settings/prefixes.json","r") as f:
        prefixes = json.load(f)
    prefixes.pop(str(guild.id))
    with open("Settings/prefixes.json","w") as f:
        json.dump(prefixes,f, indent=4)
    #joinchannel
    with open("Settings/join.json","r") as f:
        cache = json.load(f)
    cache.pop(str(guild.id))
    with open("Settings/join.json","w") as f:
        json.dump(cache,f,indent=4)
    #joindesc
    with open("Settings/joindesc.json","r") as f:
        desc = json.load(f)
    desc.pop(str(guild.id))
    with open("Settings/joindesc.json","w") as f:
        json.dump(desc,f, indent=4)
    #leavedesc
    with open("Settings/leavedesc.json","r") as f:
        desc = json.load(f)
    desc.pop(str(guild.id))
    with open("Settings/leavedesc.json","w") as f:
        json.dump(desc,f, indent=4)
    #disabledcommands
    os.remove(f"Settings/Commands/{guild.id}")
    #Muted
    if os.path.exists(f"Muted/{guild.id}"):
        os.remove(f"Muted/{guild.id}")
    if os.path.getsize(f"Muted/time") > 5:
        pops = ""
        with open("Muted/time","r") as f:
            dic = json.load(f)
        keys = dic.keys()
        for i in keys:
            if guild.id in i:
                pops = i
        if pops != "":
            dic.pop(pops)
            with open("Muted/time","w") as f:
                json.dump(dic,f,indent=4)
    #image library
    if os.path.exists(f"Images/{guild.id}"):
        os.remove(f"Images/{guild.id}")
    #alarm
    for i in os.listdir("Alarm"):
        memb = discord.utils.get(guild.members,id=int(i))
        if memb != None:
            os.remove(f"Alarm/{i}")
    #disabledchannel
    if os.path.exists(f"Settings/Disabledchannels/{guild.id}"):
        os.remove(f"Settings/Disabledchannels/{guild.id}")
    #logging
    with open("Settings/logging.json","r") as f:
        log = json.load(f)
    log.pop(str(guild.id))
    with open("Settings/logging.json","w") as f:
        json.dump(log,f,indent=4)
    #permissionhandling
    if os.path.exists(f"Settings/Permissions/{guild.id}"):
        os.remove(f"Settings/Permissions/{guild.id}")
    os.remove(f"Settings/Permissions/permrank/{guild.id}")
    #voice
    if os.path.exists(f"Queue/{guild.id}"):
        shutil.rmtree(f"Queue/{guild.id}")
    if os.path.getsize(f"Settings/volume.json") > 10:
        with open(f"Settings/volume.json","r") as f:
            v = json.load(f)
        if v[str(guild.id)] == None:
            pass
        else:
            v.pop(str(guild.id))
    #autorank
    path = f"Ranks/{guild.id}.txt"
    if os.path.exists(path):
        os.remove(path)
    path = f"Ranks/autorank/{guild.id}"
    if os.path.exists(path):
        os.remove(path)
    #musicrestrict
    if os.path.getsize("Settings/VoiceSettings/channels") < 10:
        pass
    else:
        with open("Settings/VoiceSettings/channels", "r") as f:
            x = json.load(f)
        if x[str(guild.id)] == None:
            pass
        else:
            x.pop(str(guild.id))
            with open("Settings/VoiceSettings/channels","w") as f:
                json.dump(x,f,indent=4)
    #commandsdisabledinchannels
    if os.path.exists(f"Settings/Disabledcommandsinchannel/{guild.id}"):
        os.remove(f"Settings/Disabledcommandsinchannel/{guild.id}")
    #privaterooms
    if os.path.exists(f"Private/{guild.id}"):
        os.remove(f"Private/{guild.id}")

@client.event
async def on_member_join(member):
    with open("Settings/join.json", "r") as f:
        guildjoins = json.load(f)
    guild = member.guild
    id = str(guild.id)
    channelid = guildjoins[id]
    channel = guild.get_channel(channelid)

    if Logg(guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{member.mention} Joined! **",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Member ID: {member.id}")
        emb.set_author(name="Info",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    with open("Settings/joindesc.json", "r") as f:
        desc = json.load(f)
    if desc[id] == "":
        pass
    else:
        x = ""
        if "{name}" in desc[id]:
            x = desc[id].replace("{name}", member.name)

        if "{guild}" in desc[id]:
            x = desc[id].replace("{guild}", guild.name)
        await channel.send(f"{x}")

    path = f"Ranks/autorank/{id}"
    ranks = os.listdir(path)
    time = datetime.datetime.now()
    if len(ranks) == 0:
        pass
    elif member.bot == True:
        pass
    else:
        for i in ranks:
            with open(f"{path}/{i}","r") as f:
                dic = json.load(f)
            dic[str(member.name)] = str(time - datetime.timedelta(minutes=int(dic["freq"])))
            with open(f"{path}/{i}","w") as f:
                json.dump(dic,f,indent=4)

@client.event
async def on_member_remove(before):
    with open("Settings/join.json", "r") as f:
        guildjoins = json.load(f)
    guild = before.guild
    id = str(guild.id)
    channelid = guildjoins[id]
    channel = guild.get_channel(channelid)

    if Logg(guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{before.name} Left! **",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Member ID: {before.id}")
        emb.set_author(name="Info",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    with open("Settings/leavedesc.json", "r") as f:
        desc = json.load(f)
    if desc[id] == "":
        pass
    else:
        x = ""
        if "{name}" in desc[id]:
            x = desc[id].replace("{name}", before.name)

        if "{guild}" in desc[id]:
            x = desc[id].replace("{guild}", guild.name)
        await channel.send(f"{x}")

    path = f"Ranks/autorank/{id}"
    if os.path.exists(path) == False:
        pass
        ranks = []
    else:
        ranks = os.listdir(path)
    if len(ranks) == 0:
        pass
    else:
        for i in ranks:
            with open(f"{path}/{i}","r") as f:
                dic = json.load(f)
            keys = dic.keys()
            if before.name in keys:
                dic.pop(before.name)
                with open(f"{path}/{i}", "r") as f:
                    json.dump(dic,f,indent=4)
            else:
                pass
    for i in os.listdir("Alarm"):
        memb = discord.utils.get(guild.members,id=int(i))
        if memb != None:
            os.remove(f"Alarm/{i}")

    if os.path.getsize(f"Muted/time") > 5:
        pops = ""
        with open("Muted/time","r") as f:
            dic = json.load(f)
        keys = dic.keys()
        for i in keys:
            if before.id in i:
                pops = i
        if pops != "":
            dic.pop(pops)
            with open("Muted/time","w") as f:
                json.dump(dic,f,indent=4)
    if os.path.exists(f"Muted/{guild.id}/{before.id}"):
        os.remove(f"Muted/{guild.id}/{before.id}")

@client.event
async def on_command(ctx):
    if Logg(ctx.guild.id):
        if ctx.command in ["kick","ban","unban","edit","disablechannels","enablechannels","warn","move","deafen","undeafen","mute","unmute","editrank","delrank","rankcolor","autorank","delete","deletefolder","setnick"]:
            return
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} invoked command: `{ctx.command}`**",timestamp=t,color=discord.Color.green())
        emb.add_field(name="Message",value=ctx.message.content)
        emb.set_footer(text=f"Member ID: {ctx.message.author.id} | Message ID: {ctx.message.id} ")
        emb.set_author(name="Info",icon_url="https://i.imgur.com/YkEk3SN.png")
        await chn.send(embed=emb)

@client.event
async def on_guild_role_create(role):
    guild = role.guild
    if Logg(guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{role.name} role created!**",timestamp=t,color=discord.Color.green())
        emb.set_footer(text=f"Guild ID: {guild.id}")
        emb.set_author(name="Info",icon_url="https://i.imgur.com/YkEk3SN.png")
        await chn.send(embed=emb)

@client.event
async def on_guild_role_delete(role):
    guild = role.guild
    if Logg(guild.id):
        with open("Settings/loggingchannel.json", "r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{role.name} role deleted!**", timestamp=t, color=discord.Color.orange())
        emb.set_footer(text=f"Guild ID: {guild.id}")
        emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

@client.event
async def on_guild_role_update(before,after):
    guild = before.guild
    if Logg(guild.id):
        with open("Settings/loggingchannel.json", "r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{before.name} role changed!**", timestamp=t, color=discord.Color.green())
        emb.set_footer(text=f"Guild ID: {guild.id}")
        emb.set_author(name="Info", icon_url="https://i.imgur.com/YkEk3SN.png")
        await chn.send(embed=emb)

@client.event
async def on_member_update(before,after):
    guild = after.guild
    if before.nick != after.nick:
        if Logg(guild.id):
            with open("Settings/loggingchannel.json", "r") as f:
                x = json.load(f)
            chn = client.get_channel(int(x[str(guild.id)]))
            t = datetime.datetime.now()
            emb = discord.Embed(description=f"**{after.mention} changed nickname to: {after.nick}!**", timestamp=t, color=discord.Color.green())
            emb.set_footer(text=f"Member ID: {before.id}")
            emb.set_author(name="Info", icon_url="https://i.imgur.com/YkEk3SN.png")
            await chn.send(embed=emb)
    if before.roles != after.roles:
        for i in after.roles:
            newRank = True
            for j in before.roles:
                if i == j:
                    newRank=False
            if newRank:
                if Logg(guild.id):
                    with open("Settings/loggingchannel.json", "r") as f:
                        x = json.load(f)
                    chn = client.get_channel(int(x[str(guild.id)]))
                    t = datetime.datetime.now()
                    emb = discord.Embed(description=f"**{after.mention}'s role updated: `{i.name}`**", timestamp=t,color=discord.Color.green())
                    emb.set_footer(text=f"Member ID: {before.id}")
                    emb.set_author(name="Info", icon_url="https://i.imgur.com/YkEk3SN.png")
                    await chn.send(embed=emb)

        for i in before.roles:
            newRank = True
            for j in after.roles:
                if i == j:
                    newRank = False
            if newRank:
                if Logg(guild.id):
                    with open("Settings/loggingchannel.json", "r") as f:
                        x = json.load(f)
                    chn = client.get_channel(int(x[str(guild.id)]))
                    t = datetime.datetime.now()
                    emb = discord.Embed(description=f"**{after.mention}'s role removed: `{i.name}`**", timestamp=t,color=discord.Color.orange())
                    emb.set_footer(text=f"Member ID: {before.id}")
                    emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
                    await chn.send(embed=emb)

@client.event
async def on_guild_channel_delete(channel):
    guild = channel.guild
    if Logg(guild.id):
        with open("Settings/loggingchannel.json", "r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{channel.mention} deleted**", timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Channel ID: {channel.id}")
        emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

@client.event
async def on_guild_channel_create(channel):
    guild = channel.guild
    if Logg(guild.id):
        with open("Settings/loggingchannel.json", "r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{channel.mention} created**", timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Channel ID: {channel.id}")
        emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

@client.event
async def on_guild_channel_update(before,after):
    guild = after.guild
    if Logg(guild.id):
        with open("Settings/loggingchannel.json", "r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{after.mention} edited!**", timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Channel ID: {after.id}")
        emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

@client.event
async def on_message_edit(before,after):
    if before.content != after.content:
        guild = after.guild
        if Logg(guild.id):
            with open("Settings/loggingchannel.json", "r") as f:
                x = json.load(f)
            chn = client.get_channel(int(x[str(guild.id)]))
            t = datetime.datetime.now()
            emb = discord.Embed(description=f"**{before.author.mention} edited the message!**", timestamp=t, color=discord.Color.orange())
            emb.add_field(name="Before",value=before.content)
            emb.add_field(name="After",value=after.content)
            emb.set_footer(text=f"Message ID: {after.id}")
            emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
            await chn.send(embed=emb)

@client.event
async def on_message_delete(message):
    guild = message.guild
    if Logg(guild.id):
        with open("Settings/loggingchannel.json", "r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**Message got deleted!**", timestamp=t,
                            color=discord.Color.orange())
        emb.add_field(name="Message",value=message.content)
        emb.set_footer(text=f"Message ID: {message.id}")
        emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

@client.command()
@commands.has_guild_permissions(administrator=True)
async def changeprefix(ctx,pref):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command), str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    with open("Settings/prefixes.json","r") as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = pref
    with open("Settings/prefixes.json","w") as f:
        json.dump(prefixes,f, indent=4)
    await ctx.send(f"Prefix changed to: **{prefixes[str(ctx.guild.id)]}**")

@client.command()
async def prefix(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    with open("Settings/prefixes.json","r") as f:
        prefixes = json.load(f)
    await ctx.send(f"Current Prefix is: **{prefixes[str(ctx.guild.id)]}**")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def defaultchannel(ctx,channel : discord.TextChannel):
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    with open("Settings/join.json","r") as f:
        cache = json.load(f)
    id = str(ctx.guild.id)
    cache[id] = channel.id
    with open("Settings/join.json","w") as f:
        json.dump(cache,f,indent=4)
    await ctx.send(f"DefaultChannel Changed successfully to: **{channel.name}**!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def checkcommand(ctx,command:str):
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    id = str(ctx.guild.id)
    with open(f"Settings/Commands/{id}","r") as f:
        com = json.load(f)
    if command not in com:
        await ctx.send(f"No command with name: {command}")
        return
    if com[command] == True:
        await ctx.send(f"**{command}** is enabled!")
    else:
        await ctx.send(f"**{command}** is disabled!")
    if os.path.exists(f"Settings/Disabledchannels/{ctx.guild.id}") and os.path.getsize(f"Settings/Disabledchannels/{ctx.guild.id}") > 5:
        with open(f"Settings/Disabledchannels/{ctx.guild.id}","r") as f:
            x = json.load(f)
        l = []
        l.append("```")
        for i in x:
            l.append(i)
        l.append("```")
        await ctx.send("Commands are disabled in the following channels:")
        await ctx.send("\n".join(l))
    if os.path.exists(f"Settings/Permissions/permrank/{ctx.guild.id}") and os.path.getsize(f"Settings/Permissions/permrank/{ctx.guild.id}") > 10:
        with open(f"Settings/Permissions/permrank/{ctx.guild.id}","r") as f:
            x = json.load(f)
        try:
            x = x[command]
            await ctx.send(f"This rank is restricted to: {x}")
        except:
            pass

    if os.path.exists(f"Settings/Disabledcommandsinchannel/{ctx.guild.id}") and os.path.getsize(f"Settings/Disabledcommandsinchannel/{ctx.guild.id}") > 5:
        with open(f"Settings/Disabledcommandsinchannel/{ctx.guild.id}","r") as f:
            x = json.load(f)
        try:
            l = []
            x = x[command]
            for i in x:
                ch = client.get_channel(int(i))
                l.append(ch.name)
            await ctx.send(f"The command is disabled in the following channels: {l}")
        except:
            pass

@client.command()
@commands.has_guild_permissions(administrator=True)
async def disablecommand(ctx,command:str):
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    id = str(ctx.guild.id)
    with open(f"Settings/Commands/{id}","r") as f:
        com = json.load(f)
    if command not in com:
        await ctx.send(f"No command with name: {command}")
        return
    if command in forb:
        await ctx.send(f"You can't change this command!")
        return
    if com[command] == False:
        await ctx.send("Command already disabled!")
        return
    else:
        com[command] = False
        with open(f"Settings/Commands/{id}", "w") as f:
            json.dump(com, f, indent=4)
        await ctx.send(f"**{command}** disabled!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def enablecommand(ctx,command:str):
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    global forb
    id = str(ctx.guild.id)
    with open(f"Settings/Commands/{id}","r") as f:
        com = json.load(f)

    if command not in com:
        await ctx.send(f"No command with name: {command}")
        return
    if command in forb:
        await ctx.send(f"You can't change this command!")
        return
    if com[command] == True:
        await ctx.send("Command already enabled!")
        return
    else:
        com[command] = True
        with open(f"Settings/Commands/{id}", "w") as f:
            json.dump(com, f, indent=4)
        await ctx.send(f"**{command}** enabled!")

@client.command()
async def ping(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command), str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id),ctx.message.author.id,ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    p = client.latency
    p = p*1000
    num = random.randint(0,100)
    if num <= 5:
        await ctx.send(f"🎵Still alive...`{round(p)} ms`")
    else:
        await ctx.send(f"Pong!`{round(p)} ms`")

@client.command()
async def ban(ctx,member: discord.Member,silent=False,*,reason=""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.ban_members == False:
            await ctx.send("You are missing 'ban_members' permission for this command!")
            return
    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} banned {member.mention} for {reason}!**",timestamp=t,color=discord.Color.red())
        emb.set_footer(text=f"Author ID: {ctx.message.author.id} | Member ID: {member.id}")
        emb.set_author(name="Info",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    await member.ban(reason=reason)
    if silent == False:
        await ctx.send(f"{member.mention} has been banned from {ctx.guild.name}")

@client.command()
async def unban(ctx,member,silent=False,*,reason=""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.ban_members == False:
            await ctx.send("You are missing 'ban_members' permission for this command!")
            return

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} unbanned {member} for {reason}!**",timestamp=t,color=discord.Color.red())
        emb.set_footer(text=f"Author ID: {ctx.message.author.id}")
        emb.set_author(name="Moderation",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    entry = await ctx.guild.bans()
    mname,mdisc = member.split("#")

    for entryread in entry:
        user = entryread.user

        if(user.name,user.discriminator) == (mname,mdisc):
            await ctx.guild.unban(user)
            if silent == False:
                await ctx.send(f"{user.mention} unbanned for '{reason}' reason")
            return

@client.command()
async def kick(ctx,member: discord.Member,silent=False,*,reason=""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.kick_members == False:
            await ctx.send("You are missing 'kick_members' permission for this command!")
            return

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} kicked {member.mention} for {reason}!**",timestamp=t,color=discord.Color.red())
        emb.set_footer(text=f"Author ID: {ctx.message.author.id} | Member ID: {member.id}")
        emb.set_author(name="Info",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    if silent == False:
        await ctx.send(f"{member.mention} has been kicked from {ctx.guild.name}")
    await member.kick(reason=reason)

@client.command(aliases = ["clear"])
async def purge(ctx,amount=1):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_messages == False:
            await ctx.send("You are missing 'manage_messages' permission for this command!")
            return
    await ctx.channel.purge(limit=amount+1)

@client.command(aliases= ["createtextchannel"])
async def ctc(ctx,name="defaultroom",*,category=None,position=0):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_channels == False:
            await ctx.send("You are missing 'manage_channels' permission for this command!")
            return
    await ctx.message.guild.create_text_channel(name=name,category=category,position=position)

@client.command(aliases=["createvoicechannel"])
async def cvc(ctx,name="defaultvoiceroom",*,category=None,position=0):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_channels == False:
            await ctx.send("You are missing 'manage_channels' permission for this command!")
            return
    await ctx.message.guild.create_voice_channel(name=name,category=category,position=position)

@client.command(aliases=["createcategory"])
async def cc(ctx,*,name="defaultcategory"):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_channels == False:
            await ctx.send("You are missing 'manage_channels' permission for this command!")
            return
    await ctx.message.guild.create_category(name=name)

@client.command(aliases=["serveredit"])
async def edit(ctx,name,description=None,icon=None):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_guild == False:
            await ctx.send("You are missing 'manage_guild' permission for this command!")
            return

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} edited the server with values: `name={name},description={description},icon={icon}**",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Member ID: {ctx.message.author.id} | Message ID: {ctx.message.id} ")
        emb.set_author(name="Warning",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    if description == None:
        description = ctx.guild.description
    if icon == None:
        icon = ctx.guild.icon

    await ctx.message.guild.edit(name=name,description=description,icon=icon)

@client.command()
async def vote(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    emoji1= '\N{WHITE HEAVY CHECK MARK}'
    emoji2= '\N{CROSS MARK}'
    await ctx.message.add_reaction(emoji1)
    await ctx.message.add_reaction(emoji2)

@client.command(aliases=["members"])
async def getmembers(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    members = ctx.guild.members
    await ctx.send(f"Members of {ctx.guild.name} are:\n")
    list = []
    list.append("```")
    for i in members:
        if i.bot != True:
           list.append(i.name)
    list.append("```")
    await ctx.send("\n".join(list))
    await ctx.send(f"There are currently `{ctx.guild.member_count}` members in the guild")

@client.command()
async def time(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    def zcheck(x):
        x = '0'+ x
        return x

    days = datetime.date.today()
    t = datetime.datetime.now()
    h = t.hour
    m = t.minute
    s = t.second

    if h < 10:
       h = zcheck(str(h))
    if m < 10:
       m = zcheck(str(m))
    if s < 10:
       s = zcheck(str(s))

    await ctx.send(f"Server time is:** {days} / {h} : {m} : {s} **")

@client.command()
async def warn(ctx,member: discord.Member,*,reason):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.kick_members == False or ctx.message.author.guild_permissions.ban_members == False:
            await ctx.send("You are missing 'kick_members' or 'ban_members' permission for this command!")
            return

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} warned {member.mention} with reason: {reason}**",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Author ID: {ctx.message.author.id} | Message ID: {ctx.message.id} | Member ID: {member.id}")
        emb.set_author(name="Warning",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    await member.send(reason)
    await ctx.send(f"Member has been warned!")

@client.command()
async def announce(ctx,channel : discord.TextChannel,*,message:str):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.mention_everyone == False:
            await ctx.send("You are missing 'mention_everyone' permission for this command!")
            return
    await channel.send(f"@everyone\n {message}")

@client.command()
async def echo(ctx,*,message:str):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    if ".echo" in message:
        await ctx.send("Can't echo in echo")
        return
    channel = ctx.message.channel
    await channel.send(message)

@client.command(aliases=["setnickname"])
async def setnick(ctx,member: discord.Member,*,nick=""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_nicknames == False:
            await ctx.send("You are missing 'manage_nicknames' permission for this command!")
            return
    if len(nick) > 30:
        ctx.send("Nickname must be less than 30 character!")
        return
    else:
        oldnick = member.nick
        if nick == "":
            await member.edit(nick=None)
        else:
            await member.edit(nick=nick)
        if Logg(ctx.guild.id):
            with open("Settings/loggingchannel.json", "r") as f:
                x = json.load(f)
            chn = client.get_channel(int(x[str(ctx.guild.id)]))
            t = datetime.datetime.now()
            emb = discord.Embed(
                description=f"**{ctx.message.author.mention} changed {member.mention}'s nickname from {oldnick} to {member.nick}!**",
                timestamp=t, color=discord.Color.orange())
            emb.set_footer(
                text=f"Author ID: {ctx.message.author.id} | Message ID: {ctx.message.id} | Member ID: {member.id}")
            emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
            await chn.send(embed=emb)

@client.command()
async def nick(ctx,*,nick=""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    if len(nick) > 30:
        ctx.send("Nickname must be less than 30 character!")
        return
    if nick == "":
        await ctx.message.author.edit(nick=None)
    else:
        await ctx.message.author.edit(nick=nick)

@client.command()
async def avatar(ctx,member : discord.Member):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    avatar = discord.Embed(color = discord.Color.dark_grey())
    avatar.set_image(url=f"{member.avatar_url}")
    await ctx.send(embed=avatar)

@client.command()
async def summon(ctx,member: discord.Member):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    await ctx.channel.purge(limit=1)
    for i in range(3):
       await ctx.send(member.mention)

@client.command()
async def move(ctx,member:discord.Member,channel:discord.VoiceChannel=None):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.move_members == False:
            await ctx.send("You are missing 'move_members' permission for this command!")
            return

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} moved {member.mention} to {channel.name}**",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Author ID: {ctx.message.author.id} | Message ID: {ctx.message.id} | Member ID: {member.id}")
        emb.set_author(name="Warning",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    await member.move_to(channel)

@client.command()
async def mute(ctx,member:discord.Member,mins:int = 0):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_permissions == False:
            await ctx.send("You are missing 'manage_permissions' permission for this command!")
            return
    if mins < 0:
        await ctx.send("Invalid value for minutes!")
        return

    if mins > 10080:
        await ctx.send("Value is too high!(max: 10 080min)")
        return

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} muted {member.mention} for {mins} minutes!**",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Author ID: {ctx.message.author.id} | Message ID: {ctx.message.id} | Member ID: {member.id}")
        emb.set_author(name="Warning",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    isCreated = False
    membranks = member.roles
    guildranks = ctx.guild.roles
    for i in guildranks:
        if i.name == "Mute":
            isCreated = True
            break

    if isCreated == False:
        perms = discord.Permissions(send_messages=False,read_messages=True,send_tts_messages=False,read_message_history=True,connect=False,speak=False,attach_files=False,embed_links=False,view_channel=True,stream=False)
        await ctx.guild.create_role(name="Mute",permissions=perms,colour=discord.Color.magenta(),hoist=True)

    for i in membranks:
        if i.name == "Mute":
            await ctx.send("Member is already muted!")
            return
    id = str(ctx.guild.id)
    path = f"Muted/{id}"
    if os.path.exists(path) == False:
        os.mkdir(path)

    open(f"{path}/{member.id}","w").close()
    f = open(f"{path}/{member.id}","a")
    for i in membranks:
        f.write(str(i.name)+"\n")
    f.close()
    muted = get(ctx.guild.roles, name="Mute")
    await member.edit(roles=[muted])

    if mins !=0:
        dic = {}
        if os.path.getsize("Muted/time") > 20:
            with open("Muted/time", "r") as f:
                dic = json.load(f)
        curtime = datetime.datetime.now()
        curtime = curtime + datetime.timedelta(minutes=mins)
        dic[f"{str(member.id)}/{id}"] = str(curtime)
        with open("Muted/time","w") as f:
            json.dump(dic,f,indent=4)

@client.command()
async def unmute(ctx,member:discord.Member):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_permissions == False:
            await ctx.send("You are missing 'manage_permissions' permission for this command!")
            return

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} unmuted {member.mention}**",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Author ID: {ctx.message.author.id} | Message ID: {ctx.message.id} | Member ID: {member.id}")
        emb.set_author(name="Warning",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    checkrank = member.roles
    checkMute = False

    for i in checkrank:
        if i.name == "Mute":
            checkMute = True

    del checkrank

    if checkMute == False:
        await ctx.send("Member is not muted!")
        return

    del checkMute
    ranks = await ctx.guild.fetch_roles()
    membranks =[]
    id = str(ctx.guild.id)
    path = f"Muted/{id}/"
    f = open(f"{path}{member.id}","r")
    for i in f:
        if i.strip("\n") == "@everyone":
            continue
        membranks.append(i.strip("\n"))
    f.close()
    for i in membranks:
        for j in ranks:
            if i == j.name:
                await member.add_roles(j)
    muterank = get(ctx.guild.roles,name="Mute")
    await member.remove_roles(muterank)
    os.remove(f"{path}{member.id}")
    if os.path.getsize("Muted/time") >= 20:
        with open("Muted/time","r") as f:
            dic = json.load(f)
        keys = dic.keys
        for i in keys:
            if f"{member.id}/{id}" == i:
                dic.pop(i)
                with open("Muted/time","w") as f:
                    json.dump(dic,f,indent=4)

@client.command()
async def deafen(ctx,member:discord.Member):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.deafen_members == False:
            await ctx.send("You are missing 'deafon_members' permission for this command!")
            return

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} deafened {member.mention}**",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Author ID: {ctx.message.author.id} | Message ID: {ctx.message.id} | Member ID: {member.id}")
        emb.set_author(name="Warning",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    await member.edit(deafen=True)

@client.command()
async def undeafen(ctx,member:discord.Member):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.deafen_members == False:
            await ctx.send("You are missing 'deafen_members' permission for this command!")
            return

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} undeafened {member.mention}**",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Author ID: {ctx.message.author.id} | Message ID: {ctx.message.id} | Member ID: {member.id}")
        emb.set_author(name="Warning",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    await member.edit(deafen=False)

@client.command()
async def suggest(ctx,*,message : str):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    me = await client.fetch_user(522101997193658369)
    time = datetime.datetime.now()
    time = time.strftime("%H:%M:%S")
    await me.send(f"{time} {ctx.message.author} : {message}")
    await ctx.send("Suggesstion successfully sent, thanks for the idea!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def joindesc(ctx,*,message:str =""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    with open("Settings/joindesc.json","r") as f:
        desc = json.load(f)
    desc[str(ctx.guild.id)] = message
    with open("Settings/joindesc.json","w") as f:
        json.dump(desc,f,indent=4)
    await ctx.send("Join message changed succesfully!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def leavedesc(ctx,*,message:str =""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    with open("Settings/leavedesc.json","r") as f:
        desc = json.load(f)
    desc[str(ctx.guild.id)] = message
    with open("Settings/leavedesc.json","w") as f:
        json.dump(desc,f,indent=4)
    await ctx.send("Leave message changed succesfully!")

@client.command()
@commands.cooldown(1,0.5)
async def dog(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    try:
        opener = request.build_opener()
        opener.addheaders = [("user-agent",
                              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.123 Safari/537.36')]
        request.install_opener(opener)
        while True:
            request.urlretrieve(url="https://random.dog/woof.json", filename="Cache/dogcache.json")
            with open("Cache/dogcache.json", "r") as f:
                doggy = json.load(f)
            if doggy["url"].find(".mp4") == -1 and doggy["url"].find(".webm") == -1:
                break

    except error.HTTPError as e:
        await ctx.send("Something went wrong!")
        await ctx.send("Contact Owner with this error:", e.code)
        return

    except error.URLError as e:
        await ctx.send("Server not responding!")
        await ctx.send("Contact owner with this reason:", e.reason)
        return

    emoji = '\N{DOG FACE}'
    emb = discord.Embed(title=f"{emoji}Doggy!{emoji}", colour=discord.Colour.dark_magenta())
    emb.set_image(url=doggy["url"])
    await ctx.send(embed=emb)
    os.remove("Cache/dogcache.json")

@client.command()
@commands.cooldown(1,0.5)
async def cat(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    #FIRST OCCURENCE
    url = "https://random.cat/view/1481"
    try:
        site = requests.get(url)

    except error.HTTPError as e:
        await ctx.send("Something went wrong!")
        await ctx.send("Contact Owner with this error:", e.code)
        return

    except error.URLError as e:
        await ctx.send("Server not responding!")
        await ctx.send("Contact owner with this reason:", e.reason)
        return

    soup = BeautifulSoup(site.content, "lxml")
    a_tag = soup.find("a")
    #SECOND OCCURENCE
    url = a_tag["href"]
    site = requests.get(url)
    soup = BeautifulSoup(site.content, "lxml")
    img = soup.find("img")

    emoji = '\N{CAT FACE}'
    emb = discord.Embed(title=f"{emoji} Catto! {emoji}",colour=discord.Colour.dark_magenta())

    emb.set_image(url=img["src"])
    await ctx.send(embed=emb)

@client.command()
@commands.cooldown(1,0.5)
async def bird(ctx):
    return
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    try:
        opener = request.build_opener()
        opener.addheaders = [("user-agent",
                              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.123 Safari/537.36')]
        request.install_opener(opener)
        request.urlretrieve("https://random.birb.pw/tweet/random","Cache/birdcache.png")

    except error.HTTPError as e:
        await ctx.send("Something went wrong!")
        await ctx.send(f"Contact Owner with this error: {e.code}")
        return

    except error.URLError as e:
        await ctx.send("Server not responding!")
        await ctx.send("Contact owner with this reason: {e.code}")
        return

    emoji = '\N{BIRD}'
    await ctx.send(content=f"{emoji}BIRD{emoji}",file=discord.File("Cache/birdcache.png"))
    os.remove("Cache/birdcache.png")

@client.command()
async def animalsave(ctx,url:str,name):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    form = ""
    for i in range(len(url)-1,0,-1):
        if url[i] == ".":
            break
        else:
            form = form + url[i]

    form = form[::-1]

    if url.find("https://random.dog") == -1 and url.find("https://purr.objects"):
        await ctx.send("Invalid link!")
        return
    id = str(ctx.guild.id)
    path = f"Images/{id}"
    if os.path.exists(path) == False:
        os.mkdir(path)
    path = f"{path}/"
    if os.path.exists(f"{path}{name}.{form}"):
        for i in range(999):
            if os.path.exists(f"{path}{name}{i}.{form}") == False:
                request.urlretrieve(url,filename=f"{path}{name}{i}.{form}")
                break
    else:
        request.urlretrieve(url, filename=f"{path}{name}.{form}")
    await ctx.send(f"**{name}.{form}** succesfully saved!")

@client.command()
async def coin(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    x = random.randint(1,2)
    if x == 1:
        await ctx.send("Head")
    else:
        await ctx.send("Tails")

@client.command()
async def eightball(ctx,*,message:str):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    answers = ["As I see it, yes",
	"It is certain",
	"It is decidedly so",
	"Most likely",
	"Outlook good",
	"Signs point to yes",
	"Without a doubt",
	"Yes",
	"Yes - definitely",
	"You may rely on it",
    "Reply hazy, try again",
    "Ask again later",
    "Better not tell you now",
    "Cannot predict now",
    "Concentrate and ask again",
    "Don't count on it",
    "My reply is no",
    "My sources say no",
    "Outlook not so good",
    "Very doubtful",
    ]
    emoji = '\N{BOMB}'
    await ctx.send(f"{emoji}{random.choice(answers)}{emoji}")

@client.command()
async def setalarm(ctx,mins:int,repeat,*,message:str):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    if mins < 5:
        await ctx.send("Min. 5 min!")
        return
    if mins > 43200:
        await ctx.send("max: 43 200 mins, (30 days)")
        return
    if repeat not in ["True","False","true","false"]:
        await ctx.send("Invalid repeat value! (true,false)")
        return
    memid = ctx.message.author.id
    time = datetime.datetime.now()
    ftime = str(time + datetime.timedelta(minutes=mins))
    dic = []
    dic.append(ftime)
    dic.append(message)
    dic.append(repeat)
    dic.append(mins)
    with open(f"Alarm/{memid}","w+") as f:
        json.dump(dic,f,indent=4)
    await ctx.send("Alarm set!")

@client.command()
async def delalarm(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    if os.path.exists(f"Alarm/{str(ctx.message.author.id)}") == False:
        await ctx.send("Alarm not set!")
        return
    os.remove(f"Alarm/{str(ctx.message.author.id)}")
    await ctx.send("Alarm deleted!")

@client.command()
async def disablechannels(ctx,*args : discord.TextChannel):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_roles == False:
            await ctx.send("You are missing 'manage_roles' permission for this command!")
            return

    if len(args) == 0:
        await ctx.send("Please specify a channel name!")
        return
    for i in args:
        chn = discord.utils.get(ctx.guild.text_channels,name=i.name)
        if chn == None:
            await ctx.send(f"No channel with name: **{i.name}**")
            return

    chns = []
    path = f"Settings/Disabledchannels/{ctx.guild.id}"
    if os.path.exists(path) == False:
        open(path,"x").close()
    if os.path.getsize(path) > 5:
        with open(path,"r") as f:
            chns = json.load(f)
        for i in args:
            if i not in chns:
                chns.append(i.name)
    else:
        for i in args:
            chns.append(i.name)
    with open(path,"w") as f:
        json.dump(chns,f,indent=4)

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} disabled commands in {args}**",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Member ID: {ctx.message.author.id} | Message ID: {ctx.message.id}")
        emb.set_author(name="Warning",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    await ctx.send("Channels disabled!")

@client.command()
async def enablechannels(ctx,*args: discord.TextChannel):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_roles == False:
            await ctx.send("You are missing 'manage_roles' permission for this command!")
            return
    path = f"Settings/Disabledchannels/{ctx.guild.id}"
    if os.path.exists(path) == False:
        await ctx.send("No disabled channels!")
        return
    with open(path,"r") as f:
        l = json.load(f)
    if len(l) == 0:
        await ctx.send("No disabled channels!")
        return
    if len(args) == 0:
        await ctx.send("Please specify a channel name!")
        return
    for i in args:
        if i.name in l:
            l.remove(i.name)
    with open(path,"w") as f:
        json.dump(l,f,indent=4)

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} enabled commands in {args}**",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Member ID: {ctx.message.author.id} | Message ID: {ctx.message.id}")
        emb.set_author(name="Warning",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    await ctx.send("Channels enabled!")

@client.command()
async def memberinfo(ctx,member: discord.Member):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    bot = "Yes" if member.bot else "No"
    emb = discord.Embed(title=f"Member info",
                        description=f"**{member.mention}**",
                        colour=discord.Color.dark_teal())
    emb.set_thumbnail(url=member.avatar_url)
    emb.set_footer(text="///PyCord 0.9.2.5 BETA///")
    emb.add_field(name="Name",value=member.name,inline=True)
    emb.add_field(name="Discriminator",value=member.discriminator,inline=True)
    emb.add_field(name="Nickname",value=member.nick,inline=True)
    emb.add_field(name="Status", value=member.status, inline=True)
    emb.add_field(name="Bot", value=bot, inline=True)
    emb.add_field(name="Activity",value=member.activity,inline=True)
    emb.add_field(name="Joined",value=str(member.joined_at.strftime("%Y/%m/%d - %H:%M:%S")),inline=False)
    emb.add_field(name="Registration",value=str(member.created_at.strftime("%Y/%m/%d - %H:%M:%S")),inline=True)
    ranks = member.roles
    l =[]
    for i in ranks:
        l.append(i.name)
    emb.add_field(name="Roles",value=",".join(l),inline=False)
    await ctx.send(embed=emb)

@client.command()
@commands.has_guild_permissions(administrator=True)
async def logging(ctx,val:str,chn : discord.TextChannel):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    if val == "Enable" or "enable":
        x = discord.utils.get(ctx.guild.text_channels, id=chn.id)
        if x == None:
            await ctx.send("No channel with that name!")
            return
        with open("Settings/logging.json", "r") as f:
            x = json.load(f)
        if x[str(ctx.guild.id)] == True:
            await ctx.send("Logging already enabled!")
            return
        x[str(ctx.guild.id)] = True
        with open("Settings/logging.json", "w") as f:
            json.dump(x, f, indent=4)
        x = {}
        if os.path.getsize("Settings/loggingchannel.json") > 10:
            with open("Settings/loggingchannel.json", "r") as f:
                x = json.load(f)
        x[str(ctx.guild.id)] = str(chn.id)
        with open("Settings/loggingchannel.json", "w") as f:
            json.dump(x, f, indent=4)
        await ctx.send("Logging enabled!")

    elif val == "Disable" or "disable":
        with open("Settings/logging.json","r") as f:
            x = json.load(f)
        if x[str(ctx.guild.id)] == False:
            await ctx.send("Logging already disabled!")
            return
        x[str(ctx.guild.id)] = False
        with open("Settings/logging.json", "w") as f:
            json.dump(x, f, indent=4)
        with open("Settings/loggingchannel.json", "r") as f:
            x.pop(str(ctx.guild.id))
        x[str(ctx.guild.id)] = str(chn.id)
        with open("Settings/loggingchannel.json", "w") as f:
            json.dump(x, f, indent=4)
        await ctx.send("Logging disabled!")
    else:
        await ctx.send("Value must be 'enable' or 'disable'!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def setrankcommand(ctx,com,*ranks):
    com = client.get_command(com)
    if com == None:
        await ctx.send(f"No command with name: {com}")
        return

    for i in ranks:
        x = discord.utils.get(ctx.guild.roles,name=i)
        if x == None:
            await ctx.send(f"No role with name: {i}")
            return

    x = {}
    if os.path.exists(f"Settings/Permissions/permrank/{ctx.guild.id}") and os.path.getsize(f"Settings/Permissions/permrank/{ctx.guild.id}") > 10:
        with open(f"Settings/Permissions/permrank/{ctx.guild.id}","r") as f:
            x = json.load(f)
    x[str(com)] = ranks
    with open(f"Settings/Permissions/permrank/{ctx.guild.id}","w") as f:
        json.dump(x,f,indent=4)

    path = f"Settings/Permissions/{ctx.guild.id}"
    with open(path,"r") as f:
        x = json.load(f)
    x["rankperm"] = True
    with open(path,"w") as f:
        json.dump(x,f,indent=4)

    await ctx.send("Ranks succesfully set for commands!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def delrankcommand(ctx,com):
    com = client.get_command(com)
    if com == None:
        await ctx.send(f"No command with name: {com}")
        return
    if os.path.exists(f"Settings/Permissions/permrank/{ctx.guild.id}") and os.path.getsize(f"Settings/Permissions/permrank/{ctx.guild.id}") > 5:
        with open(f"Settings/Permissions/permrank/{ctx.guild.id}","r") as f:
            x = json.load(f)
    else:
        await ctx.send("No rank set up!")
        return
    try:
        x.pop(str(com))
    except:
        await ctx.send("No rank set up!")
        return
    finally:
        with open(f"Settings/Permissions/permrank/{ctx.guild.id}", "w") as f:
            json.dump(x,f,indent=4)
        if os.path.getsize(f"Settings/Permissions/permrank/{ctx.guild.id}") < 5:
            with open(f"Settings/Permissions/{ctx.guild.id}","r") as f:
                x = json.load(f)
            x["rankperm"] = False
            with open(f"Settings/Permissions/{ctx.guild.id}", "w") as f:
                json.dump(x,f,indent=4)
        await ctx.send("Ranks succesfully deleted for commands!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def discominchan(ctx,com:str,*channel:discord.TextChannel):
    if len(channel) == 0:
        await ctx.send("Must specify channel!")
        return
    com = client.get_command(com)
    if com == None:
        await ctx.send(f"No command with name: {com}")
        return
    for i in channel:
        try:
            chan = client.get_channel(i.id)
            if chan == None:
                ctx.send(f"No channel with name: {channel}")
                return
        except:
            ctx.send(f"No channel with name: {channel}")
            return
    x = {}
    if os.path.exists(f"Settings/Disabledcommandsinchannel/{ctx.guild.id}"):
        if os.path.getsize(f"Settings/Disabledcommandsinchannel/{ctx.guild.id}") > 10:
            with open(f"Settings/Disabledcommandsinchannel/{ctx.guild.id}","r") as f:
                x = json.load(f)
    x[str(com)] = []
    for i in channel:
        chan = client.get_channel(i.id)
        idd = chan.id
        x[str(com)].append(idd)
    with open(f"Settings/Disabledcommandsinchannel/{ctx.guild.id}","w") as f:
        json.dump(x,f,indent=4)
    await ctx.send(f"`{com}` sucessfully disabled in the channels!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def encominchan(ctx,com):
    com = client.get_command(com)
    if com == None:
        await ctx.send(f"No command with name: {com}")
        return
    if os.path.exists(f"Settings/Disabledcommandsinchannel/{ctx.guild.id}") == False:
        await ctx.send("No disabled commands!")
        return
    if os.path.getsize(f"Settings/Disabledcommandsinchannel/{ctx.guild.id}") < 10:
        await ctx.send("No disabled commands!")
        return
    with open(f"Settings/Disabledcommandsinchannel/{ctx.guild.id}", "r") as f:
        x = json.load(f)
    del x[str(com)]
    with open(f"Settings/Disabledcommandsinchannel/{ctx.guild.id}", "w") as f:
        json.dump(x,f,indent=4)
    await ctx.send(f"`{com}` enabled in all channels!")

@client.command()
async def private(ctx,name:str,*members:discord.Member):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    if os.path.exists(f"Private/{ctx.guild.id}") == False:
        os.mkdir(f"Private/{ctx.guild.id}")
    rooms = os.listdir(f"Private/{ctx.guild.id}")
    if len(rooms) > 0:
        for i in rooms:
            with open(f"Private/{ctx.guild.id}/{i}", "r") as f:
                save = json.load(f)
            if int(save["owner"]) == ctx.message.author.id:
                await ctx.send("You already own a private channel!")
                return
    save={}
    cat = discord.utils.get(ctx.guild.categories,name="_PrivateChannels_")
    if cat == None:
        perms = {
            ctx.guild.default_role: discord.PermissionOverwrite(manage_channels=False,manage_permissions=False,create_instant_invite=False,manage_messages=False,view_channel=False,mention_everyone=False)
        }
        cat = await ctx.guild.create_category_channel(name="_PrivateChannels_",overwrites=perms)
    perms = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False,view_channel=False,create_instant_invite=False,manage_channels=False,manage_permissions=False,mention_everyone=False),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True,manage_messages=True,view_channel=True,create_instant_invite=False),
    }
    n = name
    aux = discord.utils.get(ctx.guild.text_channels, name=f"{name}")
    if aux != None:
        for i in range(999):
            aux = discord.utils.get(ctx.guild.text_channels,name=f"{name}_{i}")
            if aux == None:
                n = f"{name}_{i}"
    chan = await ctx.guild.create_text_channel(name=n, overwrites=perms, category=cat)
    vchan = await ctx.guild.create_voice_channel(name=n, overwrites=perms, category=cat)
    t = datetime.datetime.now()
    overwrites = discord.PermissionOverwrite()
    overwrites.read_messages = True
    overwrites.send_messages = True
    overwrites.view_channel = True
    if len(members) > 0:
        for member in members:
            await chan.set_permissions(member, overwrite=overwrites)
            await vchan.set_permissions(member, overwrite=overwrites)
    save["owner"] = ctx.message.author.id
    save["channel"] = chan.id
    save["vchannel"] = vchan.id
    save["removed"] = str(t + datetime.timedelta(hours=24))
    if os.path.exists(f"Private/{ctx.guild.id}") == False:
        os.mkdir(f"Private/{ctx.guild.id}")
    with open(f"Private/{ctx.guild.id}/{chan.id}", "w") as f:
        json.dump(save, f, indent=4)
    await ctx.send(f"Private channel: `{n}` created!")

@client.command()
async def delprivate(ctx,channel:discord.TextChannel):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    if os.path.exists(f"Private/{ctx.guild.id}/{channel.id}") == False:
        await ctx.send("No Private channel with that name!")
        return
    else:
        with open(f"Private/{ctx.guild.id}/{channel.id}", "r") as f:
            dict = json.load(f)
        if str(dict["owner"]) != str(ctx.message.author.id):
            await ctx.send("You don't have permission to delete this private channel!")
            return
        else:
            chan = ctx.guild.get_channel(int(dict["channel"]))
            vchan = ctx.guild.get_channel(int(dict["vchannel"]))
            await vchan.delete()
            await chan.delete()
            os.remove(f"Private/{ctx.guild.id}/{channel.id}")
            await ctx.send(f"Private channel: `{channel}` deleted!")

@client.command()
async def addmember(ctx,*members:discord.Member):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    if os.path.exists(f"Private/{ctx.guild.id}/{ctx.message.channel.id}") == False:
        await ctx.send("You must be in private channel to use this!")
        return
    with open(f"Private/{ctx.guild.id}/{ctx.message.channel.id}", "r") as f:
        dict = json.load(f)
    vchan = ctx.guild.get_channel(int(dict["vchannel"]))
    if int(dict["owner"]) != ctx.message.author.id:
        await ctx.send("You don't have permission to use this command in this channel!")
        return
    overwrites = discord.PermissionOverwrite()
    overwrites.read_messages = True
    overwrites.send_messages = True
    overwrites.view_channel = True
    if len(members) > 0:
        for member in members:
            await ctx.message.channel.set_permissions(member, overwrite=overwrites)
            await vchan.set_permissions(member,overwrite=overwrites)
    else:
        await ctx.send("Must Specify atleast 1 member!")
        return
    await ctx.send("Members invited!")

@client.command()
async def delmember(ctx,*members:discord.Member):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    if os.path.exists(f"Private/{ctx.guild.id}/{ctx.message.channel.id}") == False:
        await ctx.send("You must be in private channel to use this!")
        return
    with open(f"Private/{ctx.guild.id}/{ctx.message.channel.id}", "r") as f:
        dict = json.load(f)
    vchan = ctx.guild.get_channel(int(dict["vchannel"]))
    if int(dict["owner"]) != ctx.message.author.id:
        await ctx.send("You don't have permission to use this command in this channel!")
        return
    overwrites = discord.PermissionOverwrite()
    overwrites.read_messages = False
    overwrites.send_messages = False
    overwrites.view_channel = False
    if len(members) > 0:
        for member in members:
            await ctx.message.channel.set_permissions(member, overwrite=overwrites)
            await vchan.set_permissions(member, overwrite=overwrites)
    else:
        await ctx.send("Must Specify atleast 1 member!")
        return
    await ctx.send("Members deleted!")

#///RANK/ROLES///

@client.command()
async def addrank(ctx,name,value="FFFFFF",hoist=False,mentionable=False):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_roles == False:
            await ctx.send("You are missing 'manage_roles' permission for this command!")
            return
    list = await ctx.guild.fetch_roles()
    for coinc in list:
        if coinc.name == name:
            id = str(ctx.guild.id)
            f = open(f"Ranks/{id}.txt", "a+")
            f.write(f"{name}\n")
            f.close()
            await ctx.send(f"**{name}** has been added!")
            return

    if value[0] == "#":
        value = value.strip("#")

    if value[0] != "0" and value[1] != "x":
        color = int(f"0x{value}",16)

    else:
        color = int(value, 16)
    await ctx.guild.create_role(name=name,colour=discord.Colour(color),hoist=hoist,mentionable=mentionable)
    await ctx.send(f"**{name}** has been created!")
    id = str(ctx.guild.id)
    f = open(f"Ranks/{id}.txt","a+")
    f.write(f"{name}\n")
    f.close()

@client.command()
async def delrank(ctx,rank : discord.Role):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_roles == False:
            await ctx.send("You are missing 'manage_roles' permission for this command!")
            return
    joinable = []
    id = str(ctx.guild.id)
    if not os.path.exists(f"Ranks/{id}.txt"):
        ctx.send("No joinable ranks!")
        return
    f = open(f"Ranks/{id}.txt","r")
    for i in f:
        i = i.strip("\n")
        joinable.append(i)
    f.close()
    for i in joinable:
        if i == rank.name:
            joinable.remove(i)
    open(f"Ranks/{id}.txt","w").close()
    f = open(f"Ranks/{id}.txt","a")
    for i in joinable:
        f.write(i)
    f.close()
    await rank.delete()

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} deleted {rank.name}**",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Member ID: {ctx.message.author.id} | Message ID: {ctx.message.id}")
        emb.set_author(name="Warning",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    await ctx.send(f"**{rank.name}** has been deleted!")

@client.command()
async def setrank(ctx,member:discord.Member,role:discord.Role):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_roles == False:
            await ctx.send("You are missing 'manage_roles' permission for this command!")
            return
    try:
        await member.add_roles(role)
    except:
        await ctx.message.author.send("No such Role or member!")

@client.command()
async def rank(ctx,role:discord.Role):
        if CCC(ctx.guild.id, ctx.message.channel, ctx.command):
            return
        if CIA(str(ctx.command), str(ctx.guild.id)) is False:
           return
        if CDC(ctx.message.channel, str(ctx.guild.id)) is False:
            return
        c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
        if c is False:
            await ctx.send("You don't have permission to use this command!")
            return
        joinable = []
        id = ctx.guild.id
        if not os.path.exists(f"Ranks/{id}.txt"):
            f = open(f"Ranks/{id}.txt", "x")
            f.close()
        f = open(f"Ranks/{id}.txt","r")
        for i in f:
            i = i.strip("\n")
            joinable.append(i)
        f.close()
        name = role.name
        for i in joinable:
            if name == i:
                await ctx.message.author.add_roles(role)
                await ctx.send(f"{ctx.message.author.mention} joined **{role.name}**")
                return
        await ctx.send(f"No such rank as **{role.name}**")

@client.command()
async def ranks(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    joinable = []
    joinable.append("```")
    id = ctx.guild.id
    if not os.path.exists(f"Ranks/{id}.txt"):
        f = open(f"Ranks/{id}.txt","x")
        f.close()
    f = open(f"Ranks/{id}.txt","r")
    for i in f:
        joinable.append(i)
    f.close()

    await ctx.send("Joinable ranks are:")
    if len(joinable) == 0:
        await ctx.send("No joinable ranks!")
    joinable.append("```")
    await ctx.send(f"\n".join(joinable))

@client.command()
async def editrank(ctx,rank:discord.Role,name="",value=""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_roles == False:
            await ctx.send("You are missing 'manage_roles' permission for this command!")
            return
    defname  = rank.name
    defvalue = rank.color

    if name != defname and name != "":
        await rank.edit(name=name)

    if value != defvalue and value !="":
        if value[0] == "#":
            value = value.strip("#")
        if value[0] != "0" and value[1] != "x":
            color = int(f"0x{value}", 16)
        else:
            color = int(value,16)
        await rank.edit(colour=discord.Colour(color))

    if Logg(ctx.guild.id):
        with open("Settings/loggingchannel.json","r") as f:
            x = json.load(f)
        chn = client.get_channel(int(x[str(ctx.guild.id)]))
        t = datetime.datetime.now()
        emb = discord.Embed(description=f"**{ctx.message.author.mention} edited rank: {rank.name}**",timestamp=t,color=discord.Color.orange())
        emb.set_footer(text=f"Member ID: {ctx.message.author.id} | Message ID: {ctx.message.id}")
        emb.set_author(name="Warning",icon_url="https://i.imgur.com/AqUO0hF.png")
        await chn.send(embed=emb)

    await ctx.send(f"**{rank.name}** modified!")

@client.command()
async def rankcolor(ctx,rank:discord.Role,value=""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_roles == False:
            await ctx.send("You are missing 'manage_roles' permission for this command!")
            return
    defvalue= rank.color

    if value != "" and defvalue!= value:
        if value[0] == "#":
            value = value.strip("#")
        if value[0] != "0" and value[1] !="x":
            color = int(f"0x{value}",16)
        else:
            color = int(value,16)

        if Logg(ctx.guild.id):
            with open("Settings/loggingchannel.json", "r") as f:
                x = json.load(f)
            chn = client.get_channel(int(x[str(ctx.guild.id)]))
            t = datetime.datetime.now()
            emb = discord.Embed(description=f"**{ctx.message.author.mention} edited {rank.name}'s color!**",
                                timestamp=t, color=discord.Color.orange())
            emb.set_footer(text=f"Member ID: {ctx.message.author.id} | Message ID: {ctx.message.id}")
            emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
            await chn.send(embed=emb)

        await rank.edit(colour=discord.Colour(color))
        await ctx.send(f"**{rank.name}**'s color modified!")

@client.command()
async def autorank(ctx,rank:discord.Role,mins=0):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_roles == False:
            await ctx.send("You are missing 'manage_roles' permission for this command!")
            return
    if mins == 0:
        await ctx.send("You must specify a time!")
        return
    if mins < 0:
        await ctx.send("Incorrect value!")
        return
    if mins > 14400:
        await ctx.send("Value too high! max: 14400")
        return
    ranks = ctx.guild.roles
    if rank not in ranks:
        await ctx.send(f"No rank with name: **{rank}**!")
        return
    else:
        gid = str(ctx.guild.id)
        path = f"Ranks/autorank/{gid}"
        memranks = rank.members
        membs = ctx.guild.members
        pairs = {}
        time = datetime.datetime.now()
        if os.path.exists(path) == False:
            os.mkdir(path)
        path = path + f"/{rank.name}"
        if os.path.exists(path) == False:
            with open(path,"w+") as f:
                f.write("")
        if os.path.getsize(path) >= 20:
           with open(path,"r") as f:
               pairs = json.load(f)
        for i in membs:
            if i.bot == True:
                continue
            hasRank = False
            for j in memranks:
                if i.name == j.name:
                    hasRank = True
                    break
            if hasRank == False:
                pairs[str(i.id)] = str(time + datetime.timedelta(minutes=mins))
        pairs["freq"] = str(mins)
        with open(path,"w") as f:
            json.dump(pairs,f,indent=4)

            if Logg(ctx.guild.id):
                with open("Settings/loggingchannel.json", "r") as f:
                    x = json.load(f)
                chn = client.get_channel(int(x[str(ctx.guild.id)]))
                t = datetime.datetime.now()
                emb = discord.Embed(description=f"**{ctx.message.author.mention} set {rank.name} to autorank!**",
                                    timestamp=t, color=discord.Color.orange())
                emb.set_footer(text=f"Member ID: {ctx.message.author.id} | Message ID: {ctx.message.id}")
                emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
                await chn.send(embed=emb)

        await ctx.send("Autorank sucessfully set!")

@client.command()
async def delautorank(ctx,rank:str):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_roles == False:
            await ctx.send("You are missing 'manage_roles' permission for this command!")
            return
    path = f"Ranks/autorank/{str(ctx.guild.id)}"
    ranks = os.listdir(path)
    if rank in ranks:
        os.remove(f"{path}/{rank}")
        await ctx.send(f"Autorank for **{rank}** is sucessfully deleted!")
    else:
        await ctx.send(f"Autorank not set for: **{rank}**")
        return

@client.command()
async def autorankinfo(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_roles == False:
            await ctx.send("You are missing 'manage_roles' permission for this command!")
            return
    path = f"Ranks/autorank/{str(ctx.guild.id)}"
    ranks = os.listdir(path)
    ranks.insert(0,"```")
    ranks.append("```")
    if len(ranks) == 0:
        await ctx.send("No Autorank set!")
    else:
        await ctx.send(f"The following ranks are autoranked:")
        await ctx.send("\n".join(ranks))

#///RANK END/////

#///HELP///

@client.command()
@commands.cooldown(1,5)
async def help(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    emb = discord.Embed(color= discord.Color.gold(),
                        title= "PyCord Commands",
                        description="**If you have any suggestions: .suggest (message)**",
                        )
    emb.set_author(name="Help",icon_url="https://i.imgur.com/YkEk3SN.png")

    emb.add_field(name="General",value=
    "**.settings** - The bot's settings!\n"
    "**.help** - This command\n"
    "**.imgsaver** - Information and help about the image saver system!\n"
    "**.ping** - pong\n"
    "**.nick (name)** - change Nickname\n"
    "**.time** - Current server time!\n"
    "**.vote (text)** - start a vote!\n"
    "**.getmembers** - Show all members\n"
    "**.prefix **- return's the server prefix!\n"
    "**.suggest (message)**-Suggest an idea, or bug to the bot owner!\n"
    "**.setalarm (time in minutes) (repeat= True/False) (message)** - Sets an alarm (max 30 days!) you can also choose to repeat it everytime!\n"
    "**.delalarm** - deletes an alarm!\n"
    "**.echo (message)** - Echoes a message!\n"
    "**.memberinfo (member)** - Shows the info of a member\n"
    "**.info** - Bot's info",inline=False)

    emb.add_field(name="Fun/Misc",value=
                  "**.summon (name)** - Summon a person!\n"
                  "**.avatar (name)** - Show user's avatar\n"
                  "**.dog** - Sends a doggy!\n"
                  "**.cat** - Sends a Catto!\n"
                  "**.bird** - Sends a Burdo!\n"
                  "**.animalsave (dog,cat,bird url) (name)** - If you want to save an animal, right click,copy the url and paste it, and give it a name!\n"
                  "**.eightball (message) **- The magic 8ball!\n"
                  "**.coin** - Heads or Tails!",inline=False
                  )

    emb.add_field(name="Moderator",value=
    "**.kick (name) (reason)**- kick a user\n"
    "**.ban (name) (silent=True/False) (reason)**- ban a user\n"
    "**.unban (name) (silent=True/False) (reason)**- unban a user\n"
    "**.warn (name) (silent=True/False) (reason)** - warn a user\n"
    "**.purge (amount)** - delete messages\n"
    "**.announce (channel) (message)** - Announces a message to a specific channel!\n"
    "**.setnick (name) (nick)** - set user's nickname\n"
    "**.cc,ctc,cvc (name)** - in order: Create Category,Text-channel,Voice-channel\n"
    "**.edit (name) (description-OPT) (icon-OPT)** - Edits the server (OPT- Optional)\n"
    "**.deafen/undeafen (name)** - Deafen/Undeafen's a member\n"
    "**.mute/unmute (name) (mins- Min 1, Max 10080)** - Mutes/Unmute's a member\n"
    "**.move (member) (channel)** - moves a member to a different channel, leave channel empty if you want to throw it out",inline=False)

    emb.add_field(name="Ranks/Roles",value=
    "**.addrank (name)(color:HEX)(hoist)(mentionable)** - create a rank, every argument is optional except NAME!\n"
    "hoist/mentionable only accepts True or False!\n"
    "**.delrank (name)** - deletes a rank\n"
    "**.editrank (rank) (name) (value)** - Edits a rank\n"
    "**.setrank (member) (rank)** - Adds a rank to member\n"
    "**.rank (member) (rank)** - Joins a rank\n"
    "**.autorank (rank) (mins)** - Sets a timer to give out this rank after a period of time!\n"
    "**.delautorank (rank)** - Deletes the autorank if set!\n"
    "**.autorankinfo** - Show the ranks that is autoranked!\n"
    "**.ranks ** - Joinable ranks!",inline=False)

    emb.add_field(name="Music Module",value=
    "**.play (search)** - Search and plays a music, it can be URL or Words\n"
    "**.volume (value)** - Changes's the bot's volume\n"
    "**.pause** - Pauses the music\n"
    "**.resume** - Continues the music\n"
    "**.stop** - Stops and disconnect's the bot\n"
    "**.skip** - Skips a music!\n"
    "**.queue** - Shows the queued musics\n"
    "**.np** - Shows the music that is currently playing!\n"
    "**.queueclear** - Clears the queue\n"
    "**.shufflequeue** - Shuffle's the queue\n"
    "**.repeatqueue** - Set's the queue to repeat\n"
    "**.jumpto (position)** - Jumps to a specific music in the queue\n"
    "**.removesong (position)** - Removes a song from the queue\n"
    "**.movebot (channel)** - move's the bot to a different Vchannel\n",inline=False)

    emb.add_field(name="Private channel",value=
    "**.private (room name) (*members)** - Creates a private room where you can invite people, 1 Per Member!\n"
    "**.delprivate (name)** - Deletes the private channel\n"
    "**.addmember (members)** - Add new members to the private room\n"
    "**.delmember (members)** - Remove members from the private room\n",inline=False)
                    
    emb.set_footer(text="///PyCord Beta v0.9.8.5///")

    await ctx.send(embed=emb)

@client.command()
async def imgsaver(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    emb = discord.Embed(color=discord.Color.blurple(),
                        title="ImgSaver Help",
                        description="**This will explain how the ImgSaver works!**"
                        )
    emb.set_author(name="Help", icon_url="https://i.imgur.com/VlECt4n.png")
    emb.add_field(name="Note",value=
    " **-** - If you see this star symbol, it means the argument is optional!\n"
    "-**WARNING:** If you accidentally delete a picture it can't be restored! so don't ask the owner to restore it!\n"
    "-**IMPORTANT:** if you don't specify a folder where it is optional it will be always the **MAIN** folder\n"
    "-You don't need to manually create the folder, when you save a picture and specifiy the folder it automaticly creates it!\n"
    "-If you have any suggestion or problem **.suggest (message)**",inline=False)
    emb.add_field(name="Commands",value=
    "**.saveurl (url) (name) (-folder)** - Save's an url image!, (url is the url you coppied) (name- the file's name,without format' (ex. .png,.jpg)\n"
    "**.savefile (attachment) (-rename) (-folder) **- Drag a picture into the discord chat and write .savefile into the comment or before dragging it!\n"
    "**.load (name) (folder)** - Load's an image!\n"
    "**.delete (name) (folder)** - Delete's a picture!\n"
    "**.saved (-folder)** - Show saved pictures\n"
    "**.folders** - Lists the created folders!\n"
    "**.deletefolder (folder)** - Deletes a folder!,**Also deletes every pictures in it!!!**\n"
    "**.randomfile** - Sends a random picture from the library", inline=False)
    emb.set_footer(text="///PyCord Beta v0.9.8.5///")
    await ctx.send(embed=emb)

#//HELP END\\

#//Settings\\

@client.command()
async def settings(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    emb = discord.Embed(color= discord.Colour.dark_red(),title="PyCord Settings")
    emb.set_author(name="Settings", icon_url="https://i.imgur.com/ZvGCEQH.png")
    emb.add_field(name=".changeprefix (prefix)",value="Changes the bot prefix",inline=True)
    emb.add_field(name=".edit (name) (description-optional) (icon-optional),",value="Changes the server properties",inline=True)
    emb.add_field(name="defaultchannel (channel)",value= "Changes the default announce channel where should the new member will be announced!",inline=False)
    emb.add_field(name=".joindesc (message)",value="Changes the member joining message, if you want to include name and guild use: {name} {guild}",inline=True)
    emb.add_field(name=".leavedesc (message)",value="Same as joindesc but for leave",inline=True)
    emb.add_field(name=".enable/disablecommand (command)",value="Enables/disables a command!",inline=False)
    emb.add_field(name=".checkcommand (command)",value="Checks if command is enabled or not!",inline=True)
    emb.add_field(name=".disablechannels (channel)",value="Disable the commands in the writen channels!",inline=False)
    emb.add_field(name=".enablechannels (channel)", value="Enables the commands in the writen channels!", inline=True)
    emb.add_field(name=".setrankcommand (command) (ranks)",value="Overwrites permissions with ranks for a command!",inline=False)
    emb.add_field(name=".delrankcommand (command)", value="Deletes rank permissions from a command",inline=True)
    emb.add_field(name=".logging (Enable/Disable) (Channel)",value="Enables or Disables logging of actions to a specified channel!",inline=False)
    emb.add_field(name=".restrictmusic (channel)",value="Restricts the music commands to one channel!",inline=False)
    emb.add_field(name=".unrestrictmusic",value="Remove`s the restriction from the music commands!",inline=True)
    emb.add_field(name=".discominchan (command) (channels)",value="Disables a command in the specific channels!",inline=False)
    emb.add_field(name=".encominchan (command)",value="Enables the command in the restricted channels!",inline=True)
    emb.set_footer(text="///PyCord Beta v0.9.8.5///")

    await ctx.send(embed=emb)

#//Settings END\\

#//Info//
@client.command()
async def info(ctx):
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    server = len(client.guilds)
    members = len(client.users)
    emb = discord.Embed(color=discord.Colour.dark_gold(),title="PyCord Info")
    emb.set_author(name="Bot Info",icon_url="https://i.imgur.com/trDLsfy.png")
    emb.add_field(name="Version",value="0.9.8.5 BETA",inline=True)
    emb.add_field(name="Bandwidth",value=f"{round(client.latency * 1000)}ms",inline=True)
    emb.add_field(name="Servers",value=str(server),inline=True)
    emb.add_field(name="Creators",value="JeRICOh#0220 - Team Leader/Programmer\ncsavesz#2324 - Designer",inline=True)
    emb.add_field(name="Members",value="  "+str(members),inline=True)
    emb.set_footer(text="///PyCord Beta 0.9.8.5///")
    await ctx.send(embed=emb)
#//Info END//

#///AnnounceUpdate///

async def anupdate():
    guilds = client.guilds
    for i in guilds:
        isCreated = False
        guild = i
        chns = guild.channels
        for j in chns:
            if j.name == "updateannouncment":
                isCreated = True
                break
        if isCreated == False:
            await guild.create_text_channel("updateannouncment")
        chan = discord.utils.get(client.get_all_channels(), guild__name=i.name, name='updateannouncment')
        emb = discord.Embed(color=discord.Color.gold(),
                            title="UPDATES",
                            description="**UPDATE V0.9.8.5 (BETA)**", )
        emb.add_field(name="Whats new?", value='''
             **Major and Minor Bugfix**
             
             **Imgsaver commands got simplified!**
             
             **Private channels**
              -From now on only name conviniences get a number
              -Channel remove timer got extended from 12 hours to 24 hours
             
             **Bot's play response got a new look!**
             
             **Have a good day! Please report the issues! #StayAtHome #StaySafe! @JeRICOh#0220**
            ''')
        await chan.set_permissions(guild.default_role, send_messages=False)
        await chan.purge(limit=100)
        await chan.send(embed=emb)

#//UpdateEND//

#///FILESAVER///

@client.command()
async def savefile(ctx,rename="",folder=""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    id = str(ctx.guild.id)
    if folder == "Main" or folder == "main":
        await ctx.send("Invalid folder name!")
        return
    path = f"Images/{id}"
    if os.path.exists(path) == False:
        os.mkdir(path)
    if folder != "":
       if os.path.exists(f"{path}/{folder}") == False:
           os.mkdir(f"{path}/{folder}")
    atcs = ctx.message.attachments
    if len(atcs) == 0:
        await ctx.send("No attachments")
    for i in atcs:
        filename,format = i.filename.split('.')
        if format != "png" and format != "jpg":
            await ctx.send(f"**{filename}** must be png or jpg!")
            return
        elif (i.size > 9437184):
            await ctx.send(f"**{filename}** too large! (max 9MB!)")
            return
        else:
            if rename != "":
                filename = rename
            if folder != "":
                path = f"{path}/{folder}"
            if os.path.exists(f"{path}/{filename}.{format}"):
                for n in range(999):
                    if os.path.exists(f"{path}/{filename}{n}.{format}") == False:
                        filename = filename + str(n)
                        break
            await i.save(fp=f"{path}/{filename}.{format}")
            if folder != "":
                await ctx.send(f"**{filename}.{format}** saved sucessfully to {folder}!")
            else:
                await ctx.send(f"**{filename}.{format}** saved sucessfully!")

@client.command(description="For Saving images")
async def saveurl(ctx,url : str,name : str, folder:str=""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    id = str(ctx.guild.id)
    if folder == "Main" or folder == "main":
        await ctx.send("Invalid folder name!")
        return
    if len(url) < 4 and url != "http":
        await ctx.send("Must be an URL!!!")
    else:
        path = "Images/"
        if os.path.exists(f"{path}{id}") == False:
            os.mkdir(f"{path}{id}")
        if folder != "":
            os.mkdir(f"{path}{id}/{folder}")
        if folder =="":
            path = path + f"{id}/"
        else:
            path = f"{path}{id}/{folder}/"
        if os.path.exists(f"{path}{name}.png"):
            for i in range(999):
                if os.path.exists(f"{path}{name}{i}.png") == False:
                    name = f"{name}{i}.png"
                    break

        else:
            name = name + ".png"

        try:
            opener = request.build_opener()
            opener.addheaders = [("user-agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.123 Safari/537.36')]
            request.install_opener(opener)
            request.urlretrieve(url=url,filename=f"{path}{name}")

        except error.HTTPError as e:
            await ctx.send("Something went wrong!")
            await ctx.send("Contact Owner with this error:", e.code)

        except error.URLError as e:
            await ctx.send("Server not responding!")
            await ctx.send("Contact owner with this reason:", e.reason)
        else:
            if folder !="":
                await ctx.send(f"Image saved as **{name}** to {folder} folder")
            else:
                await ctx.send(f"Image saved as **{name}**")

@client.command(description="For Loading images")
async def load(ctx,pic:str,folder:str="main"):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    id = str(ctx.guild.id)
    if folder == "main" or folder == "Main":
        path = f"Images/{id}"
    else:
        if os.path.exists(f"Images/{id}/{folder}") == False:
            await ctx.send("No Folder with that name!")
            return
        path = f"Images/{id}/{folder}"
    path = f"{path}/"
    if pic.find(".") == -1:
        await ctx.send(f"`{pic}` can't be found because it requires a format!")
        return
    filename, format = pic.split(".")
    if os.path.exists(f"{path}{filename}.{format}"):
        await ctx.send(file=discord.File(f"{path}{filename}.{format}"))
    else:
        await ctx.send("No picture saved with that name or format!")

@client.command(description="For deleting pictures")
async def delete(ctx,pic:str,folder:str="main"):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_messages == False:
            await ctx.send("You are missing 'manage_messages' permission for this command!")
            return
    id = str(ctx.guild.id)
    if folder == "main" or folder == "Main":
        path = f"Images/{id}"
    else:
        if os.path.exists(f"Images/{id}/{folder}") == False:
            await ctx.send("No Folder with that name!")
            return
        path = f"Images/{id}/{folder}"
    if os.path.exists(path) == False:
        await ctx.send("No picture saved with that name!")
        return
    path = f"{path}/"
    if pic.find(".") == -1:
        await ctx.send(f"`{pic}` can't be found because it requires a format!")
        return
    name, format = pic.split(".")
    if os.path.exists(f"{path}{name}.{format}"):
        os.remove(f"{path}{name}.{format}")

        if Logg(ctx.guild.id):
            with open("Settings/loggingchannel.json", "r") as f:
                x = json.load(f)
            chn = client.get_channel(int(x[str(ctx.guild.id)]))
            t = datetime.datetime.now()
            emb = discord.Embed(description=f"**{ctx.message.author.mention} deleted {name}.{format}!**",
                                timestamp=t, color=discord.Color.orange())
            emb.set_footer(text=f"Member ID: {ctx.message.author.id} | Message ID: {ctx.message.id}")
            emb.add_field(name="Command", value=ctx.command)
            emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
            await chn.send(embed=emb)

        await ctx.send(f"**{name}.{format}** deleted!")
    else:
        await ctx.send("No picture saved with that name!")

@client.command(description="For asking pictures")
async def saved(ctx,folder=""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    id = str(ctx.guild.id)
    if folder == "" or folder == "main":
        path = f"Images/{id}/"
    else:
        if os.path.exists(f"Images/{id}/{folder}") == False:
            await ctx.send("No Folder with that name!")
            return
        path = f"Images/{id}/{folder}/"
    list = []
    list.append("```")
    if len(os.listdir(path)) == 0 or os.path.exists(path) == False:
        await ctx.send("No pictures saved!")
    else:
        await ctx.send("The following pictures are saved:")
        for i in os.listdir(path):
            list.append(i)
        list.append("```")
        await ctx.send("\n".join(list))

@client.command()
async def folders(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    id = str(ctx.guild.id)
    path = f"Images/{id}/"
    list = []
    list.append("```")
    for dirs in os.listdir(path):
        if os.path.isdir(f"{path}{dirs}"):
            list.append(dirs)
    list.append("```")
    if len(list) == 2:
        await ctx.send("There are no folders created in this guild!")
    else:
        await ctx.send("The following folders are created:")
        await ctx.send("\n".join(list))

@client.command()
async def deletefolder(ctx,folder:str):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    elif c is None:
        if ctx.message.author.guild_permissions.manage_messages == False:
            await ctx.send("You are missing 'manage_messages' permission for this command!")
            return
    if folder == "main" or folder == "Main":
        await ctx.send("You can't delete the main folder!")
        return
    path = f"Images/{str(ctx.guild.id)}/{folder}"
    if os.path.exists(path) == False:
        await ctx.send("No folder with that name!")
        return
    else:
        os.remove(path)
        await ctx.send(f"**{folder}** Sucessfully deleted!")
        if Logg(ctx.guild.id):
            with open("Settings/loggingchannel.json", "r") as f:
                x = json.load(f)
            chn = client.get_channel(int(x[str(ctx.guild.id)]))
            t = datetime.datetime.now()
            emb = discord.Embed(description=f"**{ctx.message.author.mention} deleted some folder!**",
                                timestamp=t, color=discord.Color.orange())
            emb.set_footer(text=f"Member ID: {ctx.message.author.id} | Message ID: {ctx.message.id}")
            emb.add_field(name="Command", value=ctx.command)
            emb.set_author(name="Warning", icon_url="https://i.imgur.com/AqUO0hF.png")
            await chn.send(embed=emb)

@client.command()
async def randomfile(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    id = str(ctx.guild.id)
    if os.path.exists(f"Images/{id}") == False or os.path.getsize(f"Image/{id}") == 0:
        await ctx.send("No pictures saved yet...")
        return
    file = choice(os.listdir(f"Images/{id}/"))
    await ctx.send(file=discord.File(f"Images/{id}/{file}"))

#///FILESAVER END///

#//Voice//

players = {}
queues = {}
val = {}
count = {}
qu = {}
curplaying = {}
repeat = {}

def checkQueue(id):
    global qu,curplaying,repeat
    chan = players[id].channel
    if repeat[id] != True:
        if os.path.exists(f"Queue/{id}/{qu[id]}"):
            os.remove(f"Queue/{id}/{qu[id]}")
    if len(queues[id]) == 0 or len(chan.members) < 2:
        try:
            checkafk.start(id)
        except RuntimeError:
            pass
        return
    player = players[id]
    qu[id] = queues[id].pop(0)
    if repeat[id] == True:
        queues[id].append(qu[id])
    curplaying[id] = f"{qu[id][2:len(qu[id])-4]}"
    if len(qu[id]) == 0:
        queues[id].clear()
        return
    try:
        player.play(discord.FFmpegPCMAudio(f"Queue/{id}/{qu[id]}"),after=lambda x:checkQueue(id))
        player.source = discord.PCMVolumeTransformer(player.source)
        player.source.volume = val[id]
    except discord.ClientException:
        queues[id].clear()
        print("QueueVoiceModule Error!")
        return

@client.command()
async def play(ctx,*,url=""):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    global qu
    if ctx.message.author.voice == None:
        await ctx.send("You must be in a voicechannel!")
        queues[ctx.guild.id].clear()
        return
    if ctx.voice_client == None:
        vchannel = ctx.message.author.voice.channel
        try:
            await vchannel.connect()
        except asyncio.TimeoutError:
            await ctx.send("Something went wrong!")
            queues[ctx.guild.id].clear()
            return

        player = ctx.voice_client
        players[ctx.guild.id] = player
        queues[ctx.guild.id] = []
        count[ctx.guild.id] = 0
        val[ctx.guild.id] = 0.3
        repeat[ctx.guild.id] = False
        if os.path.exists("Settings/volume.json") and os.path.getsize("Settings/volume.json") > 10:
            with open("Settings/volume.json","r") as f:
                v = json.load(f)
            if v[str(ctx.guild.id)] != None:
                val[ctx.guild.id] = v[str(ctx.guild.id)]

    await ctx.send("`Processing...`")

    if "https://" not in url:
        words = ""
        url = url.split()
        for i in range(len(url)-1):
            url[i] = url[i] + "+"
        for i in url:
            words = words + i
        url = f"https://www.youtube.com/results?search_query={words}"
        site = requests.get(url).text

        soup = BeautifulSoup(site, "lxml")

        d = soup.find_all("a")
        for link in d:
            if "/watch?v=" in link["href"]:
                url = "https://www.youtube.com" + link["href"]
                break
        if "search_query" in url:
            emoji = '\U000026A0'
            await ctx.send(f"{emoji}No match for title!")
            return


    if "&list=" in url:
        await ctx.send("Can't play Playlists!")
        return

    if "&" in url:
        f = url.split("&")
        url = f[0]

    if "?t=" in url:
        f = url.split("?")
        url = f[0]+f[1]


    if os.path.exists(f"Queue/{ctx.guild.id}") == False:
        os.mkdir(f"Queue/{ctx.guild.id}")

    count[ctx.guild.id] +=1

    ydl_opts = {
        'format': 'worstaudio',
        'geo_bypass': True,
        'ignoreerrors': True,
        'quiet': True,
        'cachedir': False,
        'extractaudio': True,
        'nooverwrites': True,
        'outtmpl': f'Queue/{ctx.guild.id}/{count[ctx.guild.id]}_%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
            'preferredquality': '192',
        }],
    }

    chars = "\-\.\_\(\)\[\]\s"

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            video_length = info_dict['duration']
            if video_length > 14500:
                await ctx.send("Music is too long! (max 4 hour!)")
                return
            coinc = re.sub(r'[^\w' + chars + ']', '', video_title)
            if os.path.exists(f"Queue/{ctx.guild.id}/{coinc}.opus"):
                await ctx.send("Song is already in Queue!")
                return
            else:
                ydl.download([url])
                path = f"Queue/{ctx.guild.id}"
                p = os.listdir(path)
                for i in p:
                    if str(count[ctx.guild.id]) + "_" in i:
                        fix = re.sub(r'[^\w' + chars + ']', '', i)
                        try:
                            os.rename(path+f"/{i}", path+f"/{fix}")
                        except FileExistsError:
                            pass
                        finally:
                            break
                queues[ctx.guild.id].append(f"{fix}")
                emb = discord.Embed(
                    title= video_title,
                    url= url,
                    timestamp= datetime.datetime.now(),
                    colour= discord.Colour(int(f"0xFF0000",16))
                )
                emb.set_author(name=f"{ctx.message.author.display_name} added a song!",icon_url="https://i.imgur.com/FpwHmmL.png")
                emb.add_field(name="Duration",value=str(datetime.timedelta(seconds=video_length)),inline=True)
                emb.add_field(name="Position",value=len(queues[ctx.guild.id])-1)
                await ctx.send(embed=emb)
    except youtube_dl.DownloadError:
        emoji = '\U000026A0'
        await ctx.send(f"{emoji}Something went wrong!")
        return

    player = players[ctx.guild.id]
    tit = os.listdir(f"Queue/{ctx.guild.id}")

    try:
        player.play(discord.FFmpegPCMAudio(f'Queue/{ctx.guild.id}/{tit[0]}'),after=lambda x:checkQueue(ctx.guild.id))
        player.source = discord.PCMVolumeTransformer(player.source)
        player.source.volume = val[ctx.guild.id]
        curplaying[ctx.guild.id] = f"`{video_title}`"
        queues[ctx.guild.id].pop(0)
        qu[ctx.guild.id] = tit[0]
    except discord.ClientException:
        return

@client.command()
async def resume(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return

    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    if ctx.voice_client == None:
        await ctx.send("Bot is not connected!")
        queues[ctx.guild.id].clear()
        return
    elif ctx.voice_client and ctx.voice_client.is_paused() == True:
        emoji = '\U000025B6'
        await ctx.send(f"{emoji}Resuming...")
        ctx.voice_client.resume()
        return
    else:
        await ctx.send("Music is not paused!")
        return

@client.command()
async def pause(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return

    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    if ctx.voice_client == None:
        await ctx.send("Bot is not connected!")
        queues[ctx.guild.id].clear()
        return
    else:
        if ctx.voice_client.is_playing() == False:
            await ctx.send("Bot is not playing music!")
            return
        else:
            ctx.voice_client.pause()
            emoji = '\U000023F8'
            await ctx.send(f"{emoji}Music is paused!")

@client.command()
async def volume(ctx,value:int):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return

    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    if value > 100 or value < 1:
        await ctx.send("Value must be inside 1-100!")
        return
    voice = get(client.voice_clients,guild=ctx.guild)
    if voice and voice.is_connected():
        if voice.is_playing():
            v = {}
            val[ctx.guild.id] = value/100
            ctx.voice_client.source.volume = value/100

            if os.path.exists("Settings/volume.json") and os.path.getsize("Settings/volume.json") > 10:
                with open("Settings/volume.json","r") as f:
                    v = json.load(f)
            v[str(ctx.guild.id)] = value/100
            with open("Settings/volume.json","w") as f:
                json.dump(v,f,indent=4)

            emoji = '\U0001F4F6'
            await ctx.send(f"{emoji}Volume changed to: `{value}`")
        else:
            await ctx.send("Bot is not playing music!")
            return

@client.command()
async def stop(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return

    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice == None:
        return
    else:
        try:
            checkafk.stop()
        except:
            pass
        voice.stop()
        await voice.disconnect()
        del players[ctx.guild.id],queues[ctx.guild.id],val[ctx.guild.id],count[ctx.guild.id],qu[ctx.guild.id],curplaying[ctx.guild.id],repeat[ctx.guild.id]
        if os.path.exists(f"Queue/{ctx.guild.id}"):
            shutil.rmtree(f"Queue/{ctx.guild.id}")

@client.command()
async def skip(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return

    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    if ctx.message.author.voice == None:
        await ctx.send("You must be in a voicechannel!")
        return
    if ctx.voice_client == None:
        await ctx.send("Bot is not playing music!")
        return
    player = players[ctx.guild.id]
    player.stop()
    emoji = '\U000023ED'
    await ctx.send(f"{emoji}Skipped!")

@client.command()
async def queue(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return

    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    global curplaying
    if ctx.voice_client == None:
        await ctx.send("Bot is not playing music!")
        return
    if len(queues[ctx.guild.id]) == 0:
        await ctx.send("No queued music!")
        return
    else:
        li =[]
        li.append("```")
        c = 0
        for i in queues[ctx.guild.id]:
            c +=1
            numb = str(c)+"."
            li.append(numb+i[2:len(i)-4])
        emoji = '\U000025B6'
        await ctx.send(f"{emoji}Now playing: `{curplaying[ctx.guild.id]}`")
        emoji = '\U000023FA'
        await ctx.send(f"{emoji}The following musics are queued:")
        li.append("```")
        await ctx.send("\n".join(li))
        await ctx.send(f"There are `{len(li)-2}` musics queued!")

@client.command()
async def np(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return

    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    if ctx.voice_client == None or ctx.voice_client.is_playing() == False:
        await ctx.send("Nothing is played right now!")
        return
    global curplaying
    emoji = '\U000025B6'
    await ctx.send(f"{emoji}Now playing: `{curplaying[ctx.guild.id]}`")

@client.command()
async def queueclear(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return

    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    global queues,qu
    if ctx.voice_client == None:
        await ctx.send("Bot is not playing music!")
        return
    if len(queues[ctx.guild.id]) == 0:
        await ctx.send("Queue already empty!")
        return
    queues[ctx.guild.id].clear()
    qu[ctx.guild.id].clear()
    emoji = "\U00002705"
    await ctx.send(f"{emoji}Queue cleared!")

@client.command()
async def shufflequeue(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return

    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    global queues
    if ctx.voice_client == None:
        await ctx.send("Bot is not playing music!")
        return
    if len(queues[ctx.guild.id]) == 0:
        await ctx.send("Queue empty!")
        return
    random.shuffle(queues[ctx.guild.id],random.random)
    emoji = '\U0001F500'
    await ctx.send(f"{emoji}Queue shuffled!")

@client.command()
async def repeatqueue(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return

    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    global repeat
    if ctx.voice_client == None:
        await ctx.send("Bot is not playing music!")
        return
    if qu[ctx.guild.id] != "" and qu[ctx.guild.id] != None:
        queues[ctx.guild.id].append(qu[ctx.guild.id])
    elif len(queues[ctx.guild.id]) == 0:
        await ctx.send("Queue already empty!")
        return
    if repeat[ctx.guild.id] == True:
        repeat[ctx.guild.id] = False
        emoji = "\U0001F500"
        await ctx.send(f"{emoji}Repeat turned `off`!")
    else:
        repeat[ctx.guild.id] = True
        emoji = "\U0001F501"
        await ctx.send(f"{emoji}Repeat tuned `on`!")

@client.command()
async def jumpto(ctx,num:int):
    if CCC(ctx.guild.id, ctx.message.channel, ctx.command):
        return
    if CMR(ctx.guild.id, ctx.message.channel.id):
        return
    if CIA(str(ctx.command), str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel, str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    global queues
    if num > len(queues[ctx.guild.id]):
        await ctx.send("No music with that number!")
        return
    if len(queues[ctx.guild.id]) == 1:
        await ctx.send("Cant jump to next song!")
        return
    if num < 1:
        await ctx.send("Number must be minim : 1")
        return
    x = queues[ctx.guild.id][num-1]
    queues[ctx.guild.id][num-1] = queues[ctx.guild.id][0]
    queues[ctx.guild.id][0] = x
    emoji = '\U000023ED'
    await ctx.send(f"{emoji}Jumped to position: `{num}`")
    ctx.voice_client.stop()

@client.command()
async def removesong(ctx,num:int):
    if CCC(ctx.guild.id, ctx.message.channel, ctx.command):
        return
    if CMR(ctx.guild.id, ctx.message.channel.id):
        return
    if CIA(str(ctx.command), str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel, str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return
    global queues
    if num > len(queues[ctx.guild.id]):
        await ctx.send("No music with that number!")
        return

    if num < 1:
        await ctx.send("Number must be minim : 1")
        return
    x = queues[ctx.guild.id][num-1]
    queues[ctx.guild.id].remove(x)
    os.remove(f"Queue/{ctx.guild.id}/{x}")
    emoji = '\U00002757'
    await ctx.send(f"{emoji}Song Removed!")

@client.command()
async def movebot(ctx,channel:discord.VoiceChannel):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CMR(ctx.guild.id,ctx.message.channel.id):
        return

    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return

    c = CP(str(ctx.guild.id), ctx.message.author.id, ctx.command)
    if c is False:
        await ctx.send("You don't have permission to use this command!")
        return

    if ctx.voice_client == None:
        await ctx.send("Bot is not in channel!, use `play`!")
        return
    if channel == ctx.voice_client.channel:
        await ctx.send("Already in channel!")
        return
    else:
        await ctx.voice_client.move_to(channel)
        players[ctx.guild.id] = ctx.voice_client
        emoji = "\U0001F3C3"
        await ctx.send(f"{emoji}Bot switched voicechannel!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def restrictmusic(ctx,channel:discord.TextChannel):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    cid = channel.id
    if cid == None:
        await ctx.send(f"{channel} is not a textchannel!")
        return
    x = {}

    if os.path.getsize(f"Settings/VoiceSettings/channels") > 10:
        with open(f"Settings/VoiceSettings/channels","r") as f:
            x = json.load(f)

    x[str(ctx.guild.id)] = str(cid)

    with open(f"Settings/VoiceSettings/channels","w") as f:
        json.dump(x,f,indent=4)
    await ctx.send(f"Music commands restricted to `{channel.name}` channel!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def unrestrictmusic(ctx):
    if CCC(ctx.guild.id,ctx.message.channel,ctx.command):
        return
    if CIA(str(ctx.command),str(ctx.guild.id)) is False:
        return
    if CDC(ctx.message.channel,str(ctx.guild.id)) is False:
        return
    x = {}
    if os.path.getsize(f"Settings/VoiceSettings/channels") > 10:
        with open(f"Settings/VoiceSettings/channels", "r") as f:
            x = json.load(f)
    else:
        await ctx.send("Music commands are not restricted!")
        return
    if x[str(ctx.guild.id)] == None:
        await ctx.send("Music commands are not restricted!")
        return
    else:
        x.pop(str(ctx.guild.id))
        with open(f"Settings/VoiceSettings/channels","w") as f:
            json.dump(x,f,indent=4)
        await ctx.send("Music commands are unrestricted!")

#//Voice END//

#\\OWNERCOMMANDS\\

@client.command()
async def defcoms(ctx,name:str):
    if ctx.message.author.id != 522101997193658369:
        await ctx.send("Unauthorized action!")
        return

    with open("Settings/defcoms.json","r") as f:
        coms = json.load(f)

    coms[name] = "true"

    with open("Settings/defcoms.json","w") as f:
        json.dump(coms,f,indent=4)
    files = os.listdir("Settings/Commands/")
    for i in files:
        with open(f"Settings/Commands/{i}","r") as f:
            coms = json.load(f)
        coms[name] = "true"
        with open(f"Settings/Commands/{i}", "w") as f:
            json.dump(coms,f,indent=4)

    await ctx.message.author.send(f"**{name}** added!")

@client.command()
async def delcoms(ctx,name:str):
    if ctx.message.author.id != 522101997193658369:
        await ctx.send("Unauthorized action!")
        return

    with open("Settings/defcoms.json","r") as f:
        coms = json.load(f)

    coms.pop(name)

    with open("Settings/defcoms.json","w") as f:
        json.dump(coms,f,indent=4)
    files = os.listdir("Settings/Commands/")
    for i in files:
        with open(f"Settings/Commands/{i}","r") as f:
            coms = json.load(f)
        coms.pop(name)
        with open(f"Settings/Commands/{i}", "w") as f:
            json.dump(coms,f,indent=4)

    await ctx.message.author.send(f"**{name}** removed!")

@client.command()
async def shutdown(ctx):
    if ctx.message.author.id != 522101997193658369:
        await ctx.send("Unauthorized action!")
        return
    else:
        sys.exit()

@client.command()
async def announceservers(ctx,*,message:str):
    if ctx.message.author.id != 522101997193658369:
        await ctx.send("Unauthorized action!")
        return
    guilds = client.guilds
    for i in guilds:
        isCreated = False
        guild = i
        chns = guild.channels
        for j in chns:
            if j.name == "updateannouncment":
                isCreated = True
                break
        if isCreated == False:
            await guild.create_text_channel("updateannouncment")
        chan = discord.utils.get(client.get_all_channels(), guild__name=i.name, name='updateannouncment')
        await chan.send(message,delete_after=1800)

#//OWNER COMMANDS END\\

#\\ERROR HANDLING\\

@rank.error
async def role_error(ctx,error):
    if isinstance(error,commands.BadArgument):
        await ctx.send(error)

@editrank.error
async def editrole_error(ctx,error):
    if isinstance(error,commands.BadArgument):
        await ctx.send(error)

@mute.error
@unmute.error
@deafen.error
@undeafen.error
@summon.error
@setnick.error
@warn.error
@unban.error
@kick.error
@ban.error
@avatar.error
async def error(ctx,error):
    if isinstance(error,commands.BadArgument):
        await ctx.send("No member with that name!")

@disablechannels.error
@enablechannels.error
@private.error
@delprivate.error
@addmember.error
@delmember.error
async def error(ctx,error):
    if isinstance(error,commands.BadArgument):
        await ctx.send(error)

@defaultchannel.error
async def error(ctx,error):
    if isinstance(error,commands.BadArgument):
        await ctx.send("No channel with that name!")
@move.error
async def error(ctx,error):
    if isinstance(error,commands.BadArgument):
        await ctx.send("Name or Channel is incorrect!")

@purge.error
async def error(ctx,error):
    if isinstance(error,commands.BadArgument):
        await ctx.send("Value must be a number!")

@client.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):
       await ctx.send("No command with that name!")
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("Too few argument!")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(error)
    if isinstance(error,commands.CommandOnCooldown):
        await ctx.send("Chill!")

@client.event
async def on_error(on_message):
    with open("on_error_log.log","a+") as f:
        f.write(on_message)
        f.write("\n")

#\\ERROR HANDLING END\\
client.run("TOKEN")
