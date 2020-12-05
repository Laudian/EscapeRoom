import logging
from Message import MessageType

class Room(object):
    # Subclasses should always call this in their initializer
    def __init__(self, name, game):
        # The name of the room, used for text- and voicechannels for example
        self.name = name
        # A Dictionary of the commands available in this room
        # "name" : "description"
        self.commands = {}

        # A list of players currently in this room
        self.players = []

        # A Dictionary to keep track of permissions
        self.permissions =\
        {
            "textchannel_available" : False,
            "voicechannel_available": False
        }

        # Initializes the Dictionary where functions corresponding to the commands are stored in
        self.command_handlers = {}
        self.message_type = MessageType.CHANNEL
        self.game = game
        return

    # Set Permissions
    def setPermission(self, name, permission):
        self.permissions[name] = permission
        return

    # Get a permissoin, returns None if permission is not set
    def getPermission(self, name):
        return self.permissions.get(name, None)

    # Usually returns self.players, but may be overridden to include subrooms
    def getPlayers(self):
        return self.players

    # Used to view the commands made available by this room, for example to
    # show which commands are available to the player.
    def getCommands(self):
        return self.commands

    # This method is called when a player enters a room and must be available
    # You should probably override this method
    def enter(self, player):
        if player not in self.players:
            self.players.append(player)
        else:
            # This should not happen. TODO: Probably log this in some error file
            return None
        return True

    # This method is called when a player leaves a room and must always be available
    # You may want to override this method
    def leave(self, player):
        if player in self.players:
            self.players.remove(player)
        else:
            # This should not happen. TODO: Probably log this in some error file
            return None
        return True

    # This method should write a message in the textchannel corresponding to this room
    # This should do nothing if the permission "textchannel_available" is False
    def sendTextMessage(self):
        return

    # This Method is called if the command used is unavailable in this room. It will inform the player
    # of this by whispering to him
    def invalidCommandHandler(self, caller, content):
        caller.sendMessage("This command is not available here. See !commands for a list of all commands that are"
                            "available to you or !help to get more general information.")
        return

    # This method handles commands that players use and should be called by the game commandHandler
    # Usually,  every command should have it's own function which is accessed via a dicitonary
    def handleCommand(self, caller, command, content=None):
        self.command_handlers.get(command, self.invalidCommandHandler)(caller, content, command)
        return

    # Use this to register your own command functions
    # Function should have the form handler(self, caller, content), where caller is a Player object
    # Name should be without the commandprefix (e.g. help, not !help)
    def registerCommand(self, name, function, description):
        self.commands[name] = description
        self.command_handlers[name] = function
        return

    # Sends a message to this player, me be string or an image
    def send(self, message):
        self.game.sendMessage(self, message)
        return