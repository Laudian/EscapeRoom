import logging
import Settings_local as Settings
import Discord

# Set up logging
logging.basicConfig(filename=Settings.logfile, level=Settings.loglevel,
                    format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

logging.info("A new EscapeRoom has begun!")

# starting bot
bot = Discord.DiscordBot
bot.run(Settings.discord_token)

