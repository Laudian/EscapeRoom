import logging
import Settings_local as Settings

# Set up logging
logging.basicConfig(filename=Settings.logfile, level=Settings.loglevel,
                    format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

logging.info("A new EscapeRoom has begun!")