import logging
from Message import *

# noinspection PyUnreachableCode
if False:
    from Room import Room

class Player(object):
    id = 0
    def __init__(self, name, game):
        self.id = Player.getId()
        self.name = name
        self.current_room = None
        self.message_type = MessageType.PLAYER
        logging.info("Player {name} has joined the game, ID is {id}.".format(name=name, id=self.id))
        self.game = game

        # A Dictionary of commands available to this player (e.g. admin commands)
        # "name" : "description"
        self.commands = {}

        # Initializes the Dictionary where functions corresponding to the commands are stored in
        self.command_handlers = {}

        # Commands are registered here
        #self.registerCommand("help", self.help, "Explains how to play the game.")
        return

    # Use this to register your own command functions
    # Function should have the form handler(self, caller, content), where caller is a Player object
    # Name should be without the commandprefix (e.g. help, not !help)
    def registerCommand(self, name, function, description):
        self.commands[name] = description
        self.command_handlers[name] = function
        return

    # This Method is called if the command used is unavailable to this player
    # will try tio resolve this by calling caller.current_room.handleCommand()
    async def invalidCommandHandler(self, caller, command, content):
        logging.debug("4")
        logging.debug(self)
        await self.current_room.handle_command(caller, command, content)
        return

    # This method handles commands that players use and should be called by the game commandHandler
    # Usually,  every command should have it's own function which is accessed via a dicitonary
    async def handleCommand(self, caller, command, content):
        logging.debug("3")
        await self.command_handlers.get(command, self.invalidCommandHandler)(caller, command, content)
        return

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self == other

    # Sends a message to this player, me be string or an image
    def send(self, message):
        self.game.send_message(self, message, MessageType.PLAYER)
        return

    @classmethod
    def getId(cls):
        cls.id += 1
        return cls.id

    def __hash__(self):
        return self.id

    def __repr__(self):
        return self.name + ":" + str(self.id)

    def setRoom(self, room):
        self.current_room = room