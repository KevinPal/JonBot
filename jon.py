import re
import random

class InvalidArgsException(Exception):
    pass

cmds = {}
rax = {}

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

    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.voices = {}
        self.random_games = []
        self.random_games_running = False

    async def do_message(self, message):
        global cmds

        # commands
        for reg, func in cmds.items():
            if reg.match(message.content):
                try:
                    await func(self, message, *(message.content.split(' ')))
                except InvalidArgsException:
                    await message.channel.send(f"Invalid usage\n{func.__doc__}")
                except Exception as e:
                    await message.channel.send(f"Unknown Error\n{str(e)}")
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
                    await message.channel.send(f"Unknown Error\n{str(e)}")
                return

    @_jon_rax(r'flip a coin')
    async def flip_coin_rax(self, message):
        await message.channel.send("Heads" if random.randint(0, 1) == 1 else "Tails")

    @_jon_rax(r'roll a die')
    async def roll_die_rax(self, message):
        await message.channel.send(str(random.randint(0, 5) + 1))

    @_jon_rax(r'roll a (\d+) sided die')
    async def roll_n_die_rax(self, message):
        await message.channel.send(str(random.randint(0, int(r2.group(1))-1) + 1))

    @_jon_rax(r'^\s*([Uu]+|[Hh]+|[Mm]+|\s+)+\s*$')
    async def jon_uh_q_rax(self, message):
        await message.channel.send(message.content + '?')

    @_jon_rax(r'^\s*([Rr]+[Ee]+)+\s*$')
    async def ree_rax(self, message):
        await message.channel.send(message.content)

    @_jon_rax(r'<@713473249903771690>')
    async def jon_bot_uh_rax(self, message):
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

        for guild in client.guilds:
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

