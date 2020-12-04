import logging
import Settings_local as Settings
import Discord
from Player import Player

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

        # Initializes the Dictionary where functions corresponding to the commands are stored in
        self.command_handlers = {}

        # Commands are registered here
        self.registerCommand("help", self.help, "Explains how to play the game.")

        # A list of players that are currently in the game
        self.players = {}

        # Starting the Discord Bot
        self.bot = Discord.DiscordBot()
        self.bot.run(Settings.discord_token)
        return

    # Use this to register your own command functions
    # Function should have the form handler(self, caller, content), where caller is a Player object
    # Name should be without the commandprefix (e.g. help, not !help)
    def registerCommand(self, name, function, description):
        self.commands[name] = description
        self.command_handlers[name] = function
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

    def help(self, caller : Player, content):
        logging.debug("{caller} has called the help function.".format(caller=caller.name))

game = EscapeRoom()