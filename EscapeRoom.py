import logging
import Settings_local as Settings
from Discord import DiscordBot
from rooms import Quizroom, Entrance
from Player import Player
from Message import *
from typing import Dict, Union
import discord, threading

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
        self.__players: Dict[Player, DiscordBot.user] = {}
        self.__discordUsers: Dict[DiscordBot.user, Player] = {}

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
        logging.debug("2")
        await caller.handleCommand(caller, command, content)
        return

    # This method handles commands that players use and should be called by the Discord module
    # Usually, every command should have it's own function which is accessed via a dict
    async def handle_command(self, caller: DiscordBot.user, command, content: str):
        player = self.discord_to_player(caller)
        if player is None:
            return
        handler = self.command_handlers.get(command, self.handle_invalid_command)
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
            self.bot.send_message(Message(self.room_to_discord(target), content))
        elif mtype == MessageType.PLAYER:
            self.bot.send_message(Message(self.player_to_discord(target), content))
        else:
            logging.error("Unknown MessageType in sendMessage")
        return

    # translates a discord user into a game player
    # returns None if that user is not in the game
    def discord_to_player(self, user: DiscordBot.user) -> Player:
        return self.__discordUsers.get(user)

    # translates a Player user into a Discord User
    # returns None if that user is not in the game
    def player_to_discord(self, player: Player) -> DiscordBot.user:
        return self.__players.get(player)

    # returns a list of all current players
    def get_players(self):
        return self.__players.keys()

    # returns a list of all current discord Users
    def get_discord_users(self):
        return self.__discordUsers.keys()

    async def register_player(self, user: DiscordBot.user, content=None):
        if content is not None:
            id = content.strip("<@").strip(">").strip("!")
            mention = self.bot.get_user(int(id))
            if mention is None:
                self.get_room("Eingangshalle").log("The mentioned User does not exist: " + id)
                return
            else:
                user = mention
        else:
            if user in self.get_discord_users():
                self.discord_to_player(user).send("Du bist bereits angemeldet")
                self.discord_to_player(user).current_room\
                    .log("User tried to register but was already registered")
                return

        player = Player(user.name, self)
        self.__players[player] = user
        self.__discordUsers[user] = player
        await self.get_room("Eingangshalle").enter(player)
        player.current_room.send("{name} wurde erfolgreich angemeldet.".format(name=player.name))
        player.current_room\
            .log("User {name} was registered".format(name=player.name))
        return

    # translates a discord channel into a game Room
    # returns None if that channel is not in the game
    def discord_to_room(self, channel: discord.TextChannel) -> "Room":
        return self.__discordChannels.get(channel)

    # translates a Room user into a discord channel
    # returns None if that room is not in the game
    def room_to_discord(self, room: "Room") -> discord.TextChannel:
        return self.__roomsToDiscordText.get(room)

    # returns a list of all current Rooms
    def get_rooms(self):
        return self.__roomsToDiscordText.keys()

    def get_room(self, name: str):
        return self.__rooms.get(name)

    # returns a list of all current discord Channels
    def get_discord_channels(self):
        return self.__discordChannels.keys()

    def get_log_channel(self, room: "Room"):
        return self.__logRooms.get(room)

    async def setup_room(self, room: 'Room', category: discord.CategoryChannel = None, parent: "Room" = None):
        if category is None:
            category = self.bot.server

        if parent is None:
            channel_log = await self.categorylog.create_text_channel(room.name + "_log")
            self.__logRooms[room] = channel_log
            self.__rooms[room.name] = room

        channel = await category.create_text_channel(room.name, topic=room.topic)
        self.__discordChannels[channel] = room
        self.__roomsToDiscordText[room] = channel
        room.log("{name} was created".format(name=room.name))

    # Creates the discord channels for all the rooms used
    async def setup_discord(self):
        self.categoryrooms: discord.CategoryChannel = await self.bot.server.create_category("Rooms", overwrites=
        {
            self.bot.server.default_role: discord.PermissionOverwrite(read_messages=True),
        })
        self.categorylog: discord.CategoryChannel = await self.bot.server.create_category("Log", overwrites=
        {
            self.bot.server.default_role: discord.PermissionOverwrite(read_messages=False),
        })

        entrance = Entrance(self)
        await self.setup_room(entrance)

        quizroom = Quizroom(self)
        await self.setup_room(quizroom, self.categoryrooms)


game = EscapeRoom()
game.start()
