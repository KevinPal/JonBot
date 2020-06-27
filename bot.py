import discord
from mcstatus import MinecraftServer
import datetime
import threading
from pydub import AudioSegment
import os
import hashlib
import math
import asyncio
import logging
import re
import time
import random
import numpy as np
import discord.opus as opus
import pafy
import pydub
import subprocess
from subprocess import Popen, PIPE
import time
import random

from audio import *

client = discord.Client()

emotes = ["<:teem:677761555521339412>", "<:pogtim:677772157765419035>", 
        "<:PixKev:687506615691509760>", "<:PixJon2:687553248940261426>", 
        "<:OhGodOhFuck:681622273282670661>", "<:huh:678051783679148051>", 
        "<:e1010:678122150128910336>", "<:marshade:678055909670256662>", 
        "<:marsus:678056307441532958>", "<:kevsad:677770488486952961>", 
        "<:clangry:677773656931434496>"]

curses = ['fuck']


special_role = 'Class A-1'
error_channel = 'commands'
# special_role = 'yayeet'
special_name = 'Jon'
special_channel = 'general'
# special_channel = 'bot_log'

black_list = ['Legends of Runeterra', 'League of Legends', 'Rust']

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

reg = re.compile(r'^`*\s*([Uu]+|[Hh]+|[Mm]+|\s+)+\s*`*$')
re_reg = re.compile(r'^`*\s*([Rr]+[Ee]+)+\s*`*$')

voices = {}



guesses = {}
random_games = []
random_games_running = False

@client.event
async def on_message(message):
    global curses
    global voices
    global random_games
    global random_games_running

    await load_opus_lib()
    print(discord.opus.is_loaded())
    print(message.author, message.content)
    try:
        if message.author == client.user:
            return
        if reg.match(message.content):
            await message.channel.send(message.content + '?')
        if re_reg.match(message.content):
            await message.channel.send(message.content)
        if '<@713473249903771690>' in message.content: #jon bot
            if any(x in message.content.lower() for x in curses):
                await message.channel.send("<:kevsad:677770488486952961>")
            else:
                await message.channel.send("uh")
        if '<@!179848643321266176>' in message.content: #jon
            await message.channel.send("uh")
            return

        if message.mention_everyone:
            await message.add_reaction("<:clangry:677773656931434496>")
        if message.tts:
            await message.add_reaction("<:pogtim:677772157765419035>")

        if random_games_running:
            random_games.append(message.content)

        r = re.search(r'^!connect (\d+)', message.content)
        if r:
            print(r.group(1))
            for guild in client.guilds:
                for vc in guild.voice_channels:
                    print(vc.id)
                    if str(vc.id) == str(r.group(1)):
                        print(f"Connected to voice {vc.name}")
                        con_vc = await vc.connect()
                        voices[str(vc.id)] = con_vc
                        await message.add_reaction("<:pogtim:677772157765419035>")

        r2 = re.search(r'^!disconnect (\d+)', message.content)
        if r2:
            if str(r2.group(1)) in voices.keys():
                await message.add_reaction("<:pogtim:677772157765419035>")
                await voices[r2.group(1)].disconnect()
                del voices[r2.group(1)]
            else:
                await message.channel.send("Not connected to channel")

        r2 = re.search(r'^!yeet (\d+) (.*)', message.content)
        if r2:
            if str(r2.group(1)) in voices.keys():
                try:
                    vc = voices[r2.group(1)]

                    # player = YTAudio(r2.group(2))
                    # print("Running")
                    # f = open('./audio/output.raw', 'rb')
                    # print(f)
                    # player = discord.PCMAudio(f)
                    player = create_YTAudio(r2.group(2), message.channel)
                    def err_func(err):
                        if err:
                            print(str(err))
                            message.channel.send(str(err))
                    vc.play(player, after = err_func)
                    while vc.is_playing():
                        await asyncio.sleep(1)
                        await player.update_msg()
                except Exception as e:
                    await message.channel.send(f"Here {str(e)}")
            else:
                await message.channel.send("Not connected to channel")

        r2 = re.search(r'flip a coin', message.content)
        if r2:
            await message.channel.send("Heads" if random.randint(0, 1) == 1 else "Tails")

        r2 = re.search(r'roll a die', message.content)
        if r2:
            await message.channel.send(str(random.randint(0, 5) + 1))

        r2 = re.search(r'roll a (\d+) sided die', message.content)
        if r2:
            await message.channel.send(str(random.randint(0, int(r2.group(1))-1) + 1))

        r2 = re.search(r'!yes', message.content)
        if r2:
            await message.channel.send("Yes")

        r2 = re.search(r'!no', message.content)
        if r2:
            await message.channel.send("Yes")

        r2 = re.search(r'!game picker start', message.content)
        if r2:
            await message.channel.send("Send games to randomly choose from")
            random_games = []
            random_games_running = True

        r2 = re.search(r'!game picker end', message.content)
        if r2:
            await message.channel.send(str(random_games[random.randint(0, len(random_games)-2)]))
            random_games = []
            random_games_running = False

        r2 = re.search(r'!mc status', message.content)
        if r2:
            server = MinecraftServer.lookup("thebeanserver.minecraftr.us:25565")
            status = server.status()
            await message.channel.send("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
            query = server.query()
            await message.channel.send("The server has the following players online: {0}".format(", ".join(query.players.names)))
    except Exception as e:
        await message.channel.send(str(e))
        print(str(e))


@client.event
async def on_disconnect():
    global vc
    for _, vc in voices.items():
        await vc.disconnect()

@client.event
async def on_voice_state_update(member, before, after):
    print(member.name, " from ", before.channel, " to ", after.channel)
    if 'CoffeeVector' == member.name:
        if after.channel == None:
            for guild in client.guilds:
                for channel in guild.channels:
                    if channel.name == 'palani-hotline':
                        count = 1
                        with open('zheng_counter', 'r') as f:
                            count = int(f.read())
                        o = count * 'o'
                        f = int(count / 2) * 'f'
                        await channel.send(f"{o}{f} <@!206991505162895360>")
                        with open('zheng_counter', 'w') as f:
                            f.write(str(count + 1))

                        


@client.event
async def on_error(event, *args, **kwargs):
    return
    print("ERROR")
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == error_channel:
                await channel.send("ERROR:")
                await channel.send(str(event))
                await channel.send(str(args))
                await channel.send(str(kwargs))

@client.event
async def on_guild_channel_create(channel):
    await channel.send("first")

@client.event
async def on_message_edit(before, after):
    if before.content == after.content:
        return
    if before.author == client.user:
        return
    await before.channel.send(f"\"{before.content}\" <:icu:678121250840641547>")

@client.event
async def on_message_delete(before):
    print("DEleTE")
    if before.author == client.user:
        return
    await before.channel.send(f"\"{before.content}\" <:icu:678121250840641547>")

anti_spam = []
tfti_queue = []
spam_lock = asyncio.Lock()

@client.event
async def on_member_update(before, after):
    global anti_spam
    global spam_lock
    global tfti_queue
    print("Update ", time.time())
    guild = after.guild

    def check_users():
        games = {}
        for i in client.get_all_members():
            if str(i.status) == 'idle':
                continue
            if special_role in [r.name for r in i.roles]:
                if(i.activity != None):
                    games_ = {i.name.strip() : [a.name for a in i.activities if a.name != None]}
                    if len(games_) > 0:
                        games.update(games_)
        matches = {}
        for user, user_games in games.items():
            for subuser, sub_user_games in games.items():
                if user == subuser:
                    continue
                for g in user_games:
                    if g in sub_user_games:
                        if g not in matches:
                            matches.update({g : [user, subuser]})
                        else:
                            if user not in matches[g]:
                                matches[g].append(user)
                            if subuser not in matches[g]:
                                matches[g].append(subuser)
        return matches
    first_matches = check_users()
    await asyncio.sleep(15)
    second_matches = check_users()


    to_remove = []
    async with spam_lock:
        print("Got lock")
        for g in anti_spam:
            if g not in second_matches.keys():
                to_remove.append(g)
        print(f"Removing {to_remove} from anti_spam, was {anti_spam}")
        anti_spam = [g for g in anti_spam if g not in to_remove]

    print("Anti Spam: ", anti_spam)
    print("Matches: ", second_matches)

    for game, _ in first_matches.items():
        if game in second_matches.keys():
            ppl = list(set(second_matches[game]) & set(first_matches[game]))
            if special_name in ppl:
                continue

            if len(ppl) > 1 and game not in black_list:
                async with spam_lock:
                    print("Got lock 2")
                    if game in anti_spam:
                        print(f"Skipping {game} due to anti spam")
                        continue
                    for channel in guild.channels:
                        if channel.name == special_channel:
                            await channel.send(f"Tfti to {game} @{' @'.join(ppl)}")
                            print(f"Sending {game}")
                            anti_spam.append(game)

@client.event
async def on_reaction_add(reaction, user):
    await reaction.message.add_reaction(emotes[random.randint(0, len(emotes)-1)])

token = ''
with open('token_file', 'r') as f:
    token = f.read()
client.run(token)
