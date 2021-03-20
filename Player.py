import logging
from Message import *
from enum import Enum
from typing import Dict, Callable
from threading import Lock

# noinspection PyUnreachableCode
if False:
    from Room import Room
    from EscapeRoom import EscapeRoom
    from Message import MessageType


class Rank(Enum):
    UNREGISTERED = 0
    REGISTERED = 1
    MOD = 2
    ADMIN = 3


class Player(object):
    id = 0
    idLock = Lock()
    characters = {1: "Tusitalafou der Reviewer", 2: "Nyja mit den geschickten Fingern", 3: "Ormänniska der Gelenkige",
                  4: "Rinua die Flinke", 5: "Aplistus der Habgierige", 6: "Iris die alte Höhlenführerin",
                  7: "Birol der gigantische Wächter", 8: "Sheying der Fotograf"}
    items = {1: "Kletterschuh", 2: "Feuerzeug", 3: "Playmobilmännchen",
             4: "Seil", 5: "Buch", 6: "Fotoapparat",
             7: "Kletterschuh", 8: "Buch"}

    def __init__(self, name: str, game: "EscapeRoom"):
        self.id: int = Player.get_id()
        self.name: str = name
        self.character = Player.get_character(self.id)
        item = Player.get_item(self.id)
        self.inventory = [item]
        self.currentRoom: "Room" = None
        self.messageType: "MessageType" = MessageType.PLAYER
        self.__rank: Rank = Rank.UNREGISTERED
        logging.info("Player {name} has joined the game, ID is {id}.".format(name=name, id=self.id))
        self.game = game

        # A Dictionary of commands available to this player (e.g. admin commands)
        # "name" : "description"
        self.commands = {}

        # Initializes the Dictionary where functions corresponding to the commands are stored in
        self.command_handlers = {}

        # Commands are registered here
        # self.registerCommand("help", self.help, "Explains how to play the game.")
        return

    # Use this to register your own command functions
    # Function should have the form handler(self, caller, content), where caller is a Player object
    # Name should be without the commandprefix (e.g. help, not !help)
    def register_command(self, name: str, function: Callable, description: str):
        self.commands[name] = description
        self.command_handlers[name] = function
        return

    # This Method is called if the command used is unavailable to this player
    # will try tio resolve this by calling caller.current_room.handleCommand()
    async def handle_invalid_command(self, caller: "Player", command: str, content: str):
        await self.currentRoom.handle_command(caller, command, content)
        return

    # This method handles commands that players use and should be called by the game commandHandler
    # Usually,  every command should have it's own function which is accessed via a dicitonary
    async def handle_command(self, caller: "Player", command: str, content: str):
        await self.command_handlers.get(command, self.handle_invalid_command)(caller, command, content)
        return

    def __eq__(self, other: "Player") -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __ne__(self, other: "Player") -> bool:
        return not self == other

    # Sends a message to this player, me be string or an image
    def send(self, message: str):
        self.game.send_message(self, message, MessageType.PLAYER)
        return

    @classmethod
    def get_id(cls) -> int:
        cls.idLock.acquire()
        cls.id += 1
        cls.idLock.release()
        return cls.id

    @classmethod
    def get_character(cls, nr):
        return cls.characters[nr]

    @classmethod
    def get_item(cls, nr):
        return cls.items[nr]

    def __hash__(self):
        return self.id

    def __repr__(self):
        return self.name + ":" + str(self.id)

    def set_room(self, room: "Room"):
        self.currentRoom = room

    def check_rank(self, rank: Rank) -> bool:
        return self.__rank.value >= rank.value

    def set_rank(self, rank: Rank):
        self.__rank = rank
