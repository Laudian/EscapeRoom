import logging
import datetime

DEBUG = True
loglevel = logging.DEBUG
logfile = "log/EscapeRoom_" + str(datetime.datetime.now())[:-7].replace("-", "_").replace(" ", "-").replace(":", "_") + ".log"
discord_token = "12345"
commandPrefix = "!"
idRoleRegistered = 12345
idRoleUnregistered = 12345
idRoleModerator = 12345
idRoleAdmin = 12345
