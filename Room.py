import logging
from Message import MessageType
from typing import Dict, List

# noinspection PyUnreachableCode
if False:
    from Player import Player
    from EscapeRoom import EscapeRoom


class Room(object):
    # Subclasses should always call this in their initializer
    def __init__(self, name: str, game: "EscapeRoom"):
        # The name of the room, used for text- and voicechannels for example
        self.name = name
        # A Dictionary of the commands available in this room
        # "name" : "description"
        self.commands: Dict[str, str] = {}

        # A list of players currently in this room
        self.players: List["Player"] = []

        # A Dictionary to keep track of permissions
        self.permissions =\
        {
            
        }

        # Topic for Discord Channel
        self.topic = "Topic setzen"

        # Initializes the Dictionary where functions corresponding to the commands are stored in
        self.command_handlers = {}
        self.message_type = MessageType.CHANNEL
        self.game = game
        
        # Register commands
        self.registerCommand(None, self.handle_none, "")
        return

    # Set Permissions
    def setPermission(self, name, permission):
        self.permissions[name] = permission
        return

    # Get a permission, returns None if permission is not set
    def getPermission(self, name):
        return self.permissions.get(name, None)

    # Usually returns self.players, but may be overridden to include subrooms
    def getPlayers(self):
        return self.players

    # Used to view the commands made available by this room, for example to
    # show which commands are available to the player.
    def getCommands(self):
        return self.commands

    async def handle_none(self, player, command, content):
        pass

    # This method is called when a player enters a room and must be available
    # You should probably override this method
    async def enter(self, player):
        if player not in self.players:
            self.players.append(player)
            player.setRoom(self)
            self.log("{name} entered the room".format(name=player.name))
            logging.info("Player {name} has entered room {room}".format(name=player.name, room=self.name))
        else:
            logging.error("Player {player} is already a member of room {room}".format(player=player.name, room=self.name))
        return

    # This method is called when a player leaves a room and must always be available
    # You may want to override this method
    async def leave(self, player):
        if player in self.players:
            self.players.remove(player)
            self.log("{name} left the room".format(name=player.name))
        else:
            logging.error("Player {player} is not a member of room {room}".format(player=player.name, room=self.name))
        return

    # This Method is called if the command used is unavailable in this room. It will inform the player
    # of this by whispering to him
    async def handle_invalid_command(self, caller, command, content):
        caller.send("This command is not available here. See !commands for a list of all commands "
                    "available to you or !help to get more general information.")
        return

    # This method handles commands that players use and should be called by the game commandHandler
    # Usually,  every command should have it's own function which is accessed via a dicitonary
    async def handle_command(self, caller, command, content=None):
        await self.command_handlers.get(command, self.handle_invalid_command)(caller, command, content)
        return

    # Use this to register your own command functions
    # Function should have the form handler(self, caller, content), where caller is a Player object
    # Name should be without the commandprefix (e.g. help, not !help)
    def registerCommand(self, name, function, description):
        self.commands[name] = description
        self.command_handlers[name] = function
        return

    # Sends a message to this room, me be string or an image
    def send(self, message):
        self.game.send_message(self, message, mtype=MessageType.CHANNEL)
        return

    def __repr__(self):
        return self.name

    def log(self, message: str):
        self.game.send_message(self, message, mtype=MessageType.LOG)
