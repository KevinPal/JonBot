import re
from mcstatus import MinecraftServer
import numpy as np
import random
from prettytable import PrettyTable
import itertools
from poll import Poll
import os

emotes = ["<:teem:677761555521339412>", "<:pogtim:677772157765419035>", 
        "<:PixKev:687506615691509760>", "<:PixJon2:687553248940261426>", 
        "<:OhGodOhFuck:681622273282670661>", "<:huh:678051783679148051>", 
        "<:e1010:678122150128910336>", "<:marshade:678055909670256662>", 
        "<:marsus:678056307441532958>", "<:kevsad:677770488486952961>", 
        "<:clangry:677773656931434496>"]

class InvalidArgsException(Exception):
    pass

cmds = {}
rax = {}
curses = ['fuck']


class Jon:

    def _jon_cmd(fun):
        global cmds
        cmds[re.compile(f"^!{fun.__name__}")] = fun
        return fun

    def _jon_rax(regex):
        def _jon_rax_internal(fun):
            global rax
            rax[re.compile(regex)] = (fun, regex)
            return fun
        return _jon_rax_internal

    def __init__(self, guild_id, client):
        self.guild_id = guild_id
        self.voices = {}
        self.client = client
        self.random_games = []
        self.random_games_running = False
        self.poll = None

    async def do_message(self, message):
        global cmds

        # commands
        for reg, func in cmds.items():
            if reg.match(message.content):
                try:
                    await func(self, message, *(message.content.split(' ')))
                except InvalidArgsException as e:
                    if str(e):
                        await message.channel.send(f"Invalid usage: {str(e)}\n{func.__doc__}")
                    else:
                        await message.channel.send(f"Invalid usage\n{func.__doc__}")
                except Exception as e:
                    await self.do_error(message, e)
                return

        # game picker
        if self.random_games_running:
            self.random_games.append(message.content)
        # reactions
        if message.mention_everyone:
            await message.add_reaction("<:clangry:677773656931434496>")
        if message.tts:
            await message.add_reaction("<:pogtim:677772157765419035>")
        for reg, (func, _) in rax.items():
            if reg.match(message.content):
                try:
                    await func(self, message)
                except Exception as e:
                    await self.do_error(message, e)
                return

    async def do_error(self, message, e):
        await message.channel.send(f"Unknown Error: {type(e).__name__}\n{str(e)}")
        await message.channel.send("<@!148202759987003392>")

    async def do_reaction(self, reaction, user, removed):
        if self.poll != None and self.poll.get_poll_id() == reaction.message.id:
            await self.poll.update_poll(reaction, user)
        else:
            await reaction.message.add_reaction(emotes[random.randint(0, len(emotes)-1)])


    @_jon_rax(r'<:kevsad:677770488486952961>')
    async def kevsad_rax(self, message):
        await message.channel.send("<:kevsad:677770488486952961>")

    @_jon_rax(r'flip a coin')
    async def flip_coin_rax(self, message):
        await message.channel.send("Heads" if random.randint(0, 1) == 1 else "Tails")

    @_jon_rax(r'roll a die')
    async def roll_die_rax(self, message):
        await message.channel.send(str(random.randint(0, 5) + 1))

    @_jon_rax(r'roll a (\d+) sided die')
    async def roll_n_die_rax(self, message):
        await message.channel.send(str(random.randint(0, int(r2.group(1))-1) + 1))

    @_jon_rax(r'^\s*([Uu]+([Hh]+|[Mm]+)|\s+|([Hh]+[Uh]+[Hh]+))+\s*$')
    async def jon_uh_q_rax(self, message):
        await message.channel.send(message.content + '?')

    @_jon_rax(r'^\s*([Rr]+[Ee]+)+\s*$')
    async def ree_rax(self, message):
        await message.channel.send(message.content)

    @_jon_rax(r'<@713473249903771690>')
    async def jon_bot_uh_rax(self, message):
        global curses
        if any(x in message.content.lower() for x in curses):
            await message.channel.send("<:kevsad:677770488486952961>")
        else:
            await message.channel.send("uh")

    @_jon_rax('<@!179848643321266176>')
    async def jon_uh(self, message):
        await message.channel.send("uh")

    @_jon_cmd
    async def help(self, message, *args):
        '''
        Displays a list of commands, or gives more info about a specific command
        Usage: !help {optional cmd}
        '''
        global cmds

        if len(args) == 1:
            s = ''
            for _, func in cmds.items():
                h = func.__doc__.split('\n')[1].strip()
                s += f"{func.__name__}: {h}" + "\n"
            await message.channel.send(s)
        elif len(args) == 2:
            for _, func in cmds.items():
                if func.__name__ == args[1]:
                    await message.channel.send(re.sub(' +', ' ', func.__doc__))
                    return
            await message.channel.send(f"Command {args[1]} not found")
        else:
            raise InvalidArgsException()

    @_jon_cmd
    async def reactions(self, message, *args):
        '''
        Lists all of jon bot's reactions and what trigger them
        Usage: !reactions
        '''
        s = ''
        for _, (func, raw_reg) in rax.items():
            s +=  f"{func.__name__.replace('_', ' ')}: `{raw_reg}`" + '\n'
        await message.channel.send(s)

    @_jon_cmd
    async def connect(self, message, *args):
        '''
        Connects to a voice channel
        Usage: !connect {channel_id}
        '''
        
        if len(args) != 2:
            raise InvalidArgsException()

        voice_id = str(args[1])

        for guild in self.client.guilds:
            for vc in guild.voice_channels:
                if str(vc.id) == voice_id:
                    print(f"Connected to voice {vc.name}")
                    con_vc = await vc.connect()
                    self.voices[str(vc.id)] = con_vc
                    await message.add_reaction("<:pogtim:677772157765419035>")

    @_jon_cmd
    async def disconnect(self, message, *args):
        '''
        Disconnects from a voice channel
        Usage: !disconnect {channel_id}
        '''
        
        if len(args) != 2:
            raise InvalidArgsException()

        voice_id = str(args[1])

        if voice_id in voices.keys():
            await message.add_reaction("<:pogtim:677772157765419035>")
            await voices[voice_id].disconnect()
            del voices[voice_id]
        else:
            await message.channel.send("Not connected to channel")

    @_jon_cmd
    async def yeet(self, message, *args):
        '''
        Plays a youtube video. Must be already connected
        Usage: !yeet {channel_id} {youtube_url}
        '''
        
        if len(args) != 3:
            raise InvalidArgsException()

        voice_id = str(args[1])
        url = str(args[2])

        if voice_id in voices.keys():
            vc = voices[voice_id]

            # player = YTAudio(r2.group(2))
            # print("Running")
            # f = open('./audio/output.raw', 'rb')
            # print(f)
            # player = discord.PCMAudio(f)
            player = create_YTAudio(url, message.channel)
            def err_func(err):
                if err:
                    print(str(err))
                    message.channel.send(f"Error playing video: {str(err)}")
            vc.play(player, after = err_func)
            while vc.is_playing():
                await asyncio.sleep(1)
                await player.update_msg()
        else:
            await message.channel.send("Not connected to channel")

    @_jon_cmd
    async def split_grp(self, message, *args):
        '''
        Splits people into groups
        Usage: !split_grp {num_groups} {name1} {name2} ...
        '''
        if len(args) <= 2:
            raise InvalidArgsException()

        out = ''
        num_groups = int(args[1])
        names = list(args[2:])
        group_size = len(names) / num_groups
        if not group_size.is_integer():
            out += f"Could not evenly split {len(names)} names into {num_groups} groups\n"
        group_size = int(group_size)
        np.random.shuffle(names)
        groups = np.array_split(names, num_groups)
        groups = [x for x in groups if x.size > 0]
        for i in range(len(groups)):
            out += f"Group {i+1}: {', '.join(groups[i])}\n"
        await message.channel.send(out)

    @_jon_cmd
    async def imposter(self, message, *args):
        '''
        Jon is always the imposter
        Usage: !imposter
        '''
        await message.channel.send("The imposter is Jon", tts=True)


    @_jon_cmd
    async def yes(self, message, *args):
        '''
        Says yes
        Usage: !yes
        '''
        await message.channel.send("Yes")

    @_jon_cmd
    async def no(self, message, *args):
        '''
        Says yes
        Usage: !no
        '''
        await message.channel.send("Yes")

    @_jon_cmd
    async def game_picker(self, message, *args):
        '''
        Starts or ends the game picker
        Usage: !game_picker {start | end}
        '''
        if len(args) != 2 or args[1] not in ['start', 'end']:
            raise InvalidArgsException()

        if args[1] == 'start':
            await message.channel.send("Send options to randomly choose from")
            self.random_games = []
            self.random_games_running = True
        elif args[1] == 'end':
            await message.channel.send(str(self.random_games[random.randint(0, len(self.random_games)-2)]))
            self.random_games = []
            self.random_games_running = False

    @_jon_cmd
    async def mc_status(self, message, *args):
        '''
        Checks the status of Mar's minecraft server
        Usage !mc_status
        '''
        server = MinecraftServer.lookup("thebeanserver.minecraftr.us:25565")
        status = server.status()
        await message.channel.send("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
        query = server.query()
        await message.channel.send("The server has the following players online: {0}".format(", ".join(query.players.names)))

    @_jon_cmd
    async def poll(self, message, *args):
        '''
        Starts a poll for a specific role or ends the last poll
        !poll start {role} 
            --yes {yes text}
            --no {no text}
            --default {default text}
            --channel {channel name}
        !poll end
        '''
        if len(args) < 2:
            raise InvalidArgsException()

        if args[1] not in ['start', 'end']:
            raise InvalidArgsException()

        if (args[1] == 'start' and self.poll != None) or (args[1] == 'end'):
            await self.poll.end_poll()
            self.poll = None

        if args[1] == 'start':
            self.poll = Poll(self, message, *args)
            await self.poll.start_poll()

    @_jon_cmd
    async def test(self, message, *args):
        '''
        Test cmd
        !test
        '''
        await message.channel.send(f"Test {str(args)}")

    @_jon_cmd
    async def restart(self, message, *args):
        '''
        Restarts jonbot
        !restart
        '''
        os.system('python3 run.py --kill')



