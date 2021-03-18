import logging
import Settings_local as Settings
from Discord import DiscordBot
from rooms import Caveentrance, Entrance, TwoDoors, Keyroom, FourWalls, BossRoom
from Player import Player, Rank
from Message import *
from typing import Dict, Union, List
import discord

# noinspection PyUnreachableCode
if False:
    from Room import Room

# Set up logging
logging.basicConfig(filename=Settings.logfile, level=Settings.loglevel,
                    format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S',
                    encoding="utf-8")

class EscapeRoom(object):
    def __init__(self):
        logging.info("A new EscapeRoom has begun!")

        # A Dictionary of the commands available in the game at all times
        # "name" : "description"
        self.commands = {}

        # Dictionaries to translate between Players and Discord users
        self.__players: Dict[Player, discord.Member] = {}
        self.__discordUsers: Dict[discord.Member, Player] = {}

        # Dictionaries to translate between Rooms and Discord channels
        self.__discordChannels: Dict[discord.TextChannel, Room] = {}
        self.__roomsToDiscordText: Dict["Room", discord.TextChannel] = {}
        self.__roomsToDiscordVoice: Dict["Room", discord.VoiceChannel] = {}
        self.__logRooms: Dict["Room", discord.TextChannel] = {}

        # Dictionary to identify rooms by name
        self.__rooms: Dict[str, Room] = {}

        # Initializes the Dictionary where functions corresponding to the commands are stored in
        self.command_handlers = {}

        # Commands are registered here
        self.register_command("help", self.help, "Explains how to play the game.")
        self.register_command("register", self.register, "Register to the game by writing !register.")
        self.register_command("admin", self.makeadmin, "Wird von Laudian benutzt, um sich zum Admin zu machen.")

        # Roles and Categories, will be initializes when bot is ready
        self.categoryRooms = None
        self.categoryLog = None
        self.roleRegistered = None
        self.roleUnregistered = None
        self.roleModerator = None
        self.roleAdmin = None

        # Starting the Discord Bot
        self.bot = DiscordBot(self)
        return

    # Use this to register your own command functions
    # Function should have the form handler(self, caller, content), where caller is a Player object
    # Name should be without the command prefix (e.g. help, not !help)
    def register_command(self, name, function, description):
        self.commands[name] = description
        self.command_handlers[name] = function
        return

    # This Method is called if the command used is unavailable in the general game.
    # will try tio resolve this by calling caller.handleCommand()
    async def handle_invalid_command(self, caller: Player, command, content):
        await caller.handle_command(caller, command, content)
        return

    # This method handles commands that players use and should be called by the Discord module
    # Usually, every command should have it's own function which is accessed via a dict
    async def handle_command(self, caller: discord.Member, command, content: str):
        handler = self.command_handlers.get(command, self.handle_invalid_command)
        if command in ["register", "admin", "start"]:
            await handler(caller, command, content)
        else:
            player = self.discord_to_player(caller)
            if player is None:
                return
            else:
                await handler(player, command, content)
        return

    # Implements the help command
    def help(self, caller: Player, command, content):
        logging.debug("{caller} has called the help function.".format(caller=caller))
        return

    def start(self):
        self.bot.run(Settings.discordToken)
        return

    def send_message(self, target: Union[Player, "Room"], content, mtype=None):
        if mtype == MessageType.LOG:
            self.bot.send_message(Message(self.get_log_channel(target), content))
        elif mtype == MessageType.CHANNEL:
            self.bot.send_message(Message(self.room_to_textchannel(target), content))
        elif mtype == MessageType.PLAYER:
            self.bot.send_message(Message(self.player_to_discord(target), content))
        else:
            logging.error("Unknown MessageType in sendMessage")
        return

    # translates a discord user into a game player
    # returns None if that user is not in the game
    def discord_to_player(self, user: discord.Member) -> Player:
        return self.__discordUsers.get(user)

    # translates a Player user into a Discord User
    # returns None if that user is not in the game
    def player_to_discord(self, player: Player) -> discord.Member:
        return self.__players.get(player)

    # returns a list of all current players
    def get_players(self):
        return self.__players.keys()

    # returns a list of all current discord Users
    def get_discord_users(self):
        return self.__discordUsers.keys()

    async def register(self, user: discord.Member, command: str, content: str):
        if content != "":
            if not (self.roleModerator in user.roles or self.roleAdmin in user.roles):
                self.get_room("Eingangshalle").send("Da musst Moderator sein, um andere Spieler anzumelden.")
                return
            dcid = content.strip("<@").strip(">").strip("!")
            mention = await self.bot.server.fetch_member(int(dcid))
            if mention is None:
                self.get_room("Eingangshalle").log("The mentioned User does not exist: " + dcid)
                return
            else:
                user = mention
        if user in self.get_discord_users():
            self.discord_to_player(user).send("Du bist bereits angemeldet")
            self.discord_to_player(user).currentRoom\
                .log("User tried to register but was already registered")
            return

        player = Player(user.name, self)
        self.__players[player] = user
        self.__discordUsers[user] = player
        await self.get_room("Eingangshalle").enter(player)
        await user.remove_roles(self.roleUnregistered)
        await user.add_roles(self.roleRegistered)
        player.set_rank(await self.get_rank(player))
        player.currentRoom.send("{name} wurde erfolgreich angemeldet.".format(name=player.name))
        player.currentRoom\
            .log("User {name} was registered".format(name=player.name))
        return

    # translates a discord channel into a game Room
    # returns None if that channel is not in the game
    def discord_to_room(self, channel: discord.TextChannel) -> "Room":
        return self.__discordChannels.get(channel)

    # translates a Room user into a discord textchannel
    # returns None if that room is not in the game
    def room_to_textchannel(self, room: "Room") -> discord.TextChannel:
        return self.__roomsToDiscordText.get(room)

    # translates a Room user into a discord voicechannel
    # returns None if that room is not in the game
    def room_to_voicechannel(self, room: "Room") -> discord.VoiceChannel:
        return self.__roomsToDiscordVoice.get(room)

    # returns a list of all current Rooms
    def get_rooms(self) -> List["Room"]:
        return list(self.__roomsToDiscordText.keys())

    def get_room(self, name: str) -> "Room":
        return self.__rooms.get(name)

    # returns a list of all current discord Channels
    def get_discord_channels(self) -> List[discord.TextChannel]:
        return list(self.__discordChannels.keys())

    def get_log_channel(self, room: "Room") -> discord.TextChannel:
        return self.__logRooms.get(room)

    async def setup_room(self, room: 'Room', category: discord.CategoryChannel = None, parent: "Room" = None):
        if category is None:
            category = await self.bot.server.create_category(room.name, overwrites=
            {
                self.bot.server.default_role: discord.PermissionOverwrite(read_messages=False),
            })
            room.category = category

        if parent is None:
            channel_log = await self.categoryLog.create_text_channel(room.name + "_log")
            self.__logRooms[room] = channel_log
            self.__rooms[room.name] = room

        channel = await category.create_text_channel(room.name, topic=room.topic)
        voice = await category.create_voice_channel(room.name, topic=room.topic)
        self.__discordChannels[channel] = room
        self.__discordChannels[voice] = room
        self.__roomsToDiscordText[room] = channel
        self.__roomsToDiscordVoice[room] = voice
        room.log("{name} was created".format(name=room.name))

    # Creates the discord channels for all the rooms used
    async def setup_discord(self):
        self.categoryLog: discord.CategoryChannel = await self.bot.server.create_category("Log", overwrites=
        {
            self.bot.server.default_role: discord.PermissionOverwrite(read_messages=False),
        })

        self.roleUnregistered = self.bot.server.get_role(Settings.idRoleUnregistered)
        self.roleRegistered = self.bot.server.get_role(Settings.idRoleRegistered)
        self.roleModerator = self.bot.server.get_role(Settings.idRoleModerator)
        self.roleAdmin = self.bot.server.get_role(Settings.idRoleAdmin)

        async for member in self.bot.server.fetch_members():
            await member.remove_roles(self.roleRegistered)
            await member.add_roles(self.roleUnregistered)

        entrance = Entrance(self)
        category = await self.bot.server.create_category(entrance.name, overwrites=
        {
            self.bot.server.default_role: discord.PermissionOverwrite(read_messages=True),
        })
        await self.setup_room(entrance, category)

        caveentrance = Caveentrance(self)
        await self.setup_room(caveentrance)

        dungeon = Keyroom.Keyroom(self)
        await self.setup_room(dungeon)

        twodoors = TwoDoors(self)
        await self.setup_room(twodoors)

        fourwalls = FourWalls(self)
        await self.setup_room(fourwalls)

        bossroom = BossRoom(self)
        await self.setup_room(bossroom)

    # Used to make a discord channel visible to players
    async def show_room(self, room: "Room", player: Player, text=False, voice=False, write=True, react=True,
                        speak=True):
        member = self.player_to_discord(player)
        if text:
            textchannel = self.room_to_textchannel(room)
            await textchannel.set_permissions(member, read_messages=True, send_messages=write, add_reactions=react)
        if voice:
            voicechannel = self.room_to_voicechannel(room)
            await voicechannel.set_permissions(member, read_messages=True, speak=speak, stream=False)

    # Used to make a discord channel invisible to players
    async def hide_room(self, room: "Room", player: Player):
        member = self.player_to_discord(player)
        textchannel = self.room_to_textchannel(room)
        await textchannel.set_permissions(member, read_messages=False)

        voicechannel = self.room_to_voicechannel(room)
        await voicechannel.set_permissions(member, read_messages=False)

    async def get_rank(self, player: Player) -> Rank:
        user = self.player_to_discord(player)
        if self.roleAdmin in user.roles:
            return Rank.ADMIN
        elif self.roleModerator in user.roles:
            return Rank.MOD
        elif self.roleRegistered in user.roles:
            return Rank.REGISTERED
        else:
            return Rank.UNREGISTERED
    
    async def makeadmin(self, caller: discord.Member, command, content):
        member = caller
        if member.id == Settings.idLaudian:
            if self.roleAdmin in member.roles:
                await member.remove_roles(self.roleAdmin)
            else:
                await member.add_roles(self.roleAdmin)


game = EscapeRoom()
game.start()
