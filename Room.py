


class Room(object):
    # Subclasses should always call this in their initializer
    def __init__(self, name):
        # The name of the room, used for text- and voicechannels for example
        self.name = name
        # Rooms must list commands available in this room as tuples of the form:
        # ("name", "description")
        self.commands = []

        # A list of commands that are not available in this room, for example "inventory"
        self.commands_disabled = []

        # A list of players currently in this room
        self.players = []

        # A Dictionary to keep track of permissions
        self.permissions =\
        {
            "textchannel_available" : False,
            "voicechannel_available": False
        }

        # Initializes the Dictionary where functions corresponding to the commands are stored in
        self.command_handler = {}

    # Usually returns self.players, but may be overridden to include subrooms
    def getPlayers(self):
        return self.players

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

    # This method handles commands that players use and should be called by the game commandHandler
    # Usually,  every command should have it's own function which is accessed via a dicitonary
    def handleCommand(self, caller, command, content):
        self.command_handler.get(command)(caller, content)