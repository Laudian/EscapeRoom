import logging
import discord
from queue import Queue
from Message import *
import asyncio


class DiscordBot(discord.Client):

    def __init__(self, game):
        super().__init__()

        self.game_users = {}

        self.game_channels = {}

        self.game_message_queue = Queue()

        self.game = game

        self.game_sendMessageTask = self.loop.create_task(self.game_sendMessageTask())
        self.game_sendMessages = False
        return


    # logged in and prepared
    async def on_ready(self):
        self.game_channels[self.game.room] = self.get_channel(784596953496813598)
        self.game_sendMessages = True
        logging.info("Bot is online")

    # someone sends a message anywhere the bot can read it
    async def on_message(self, message):
        if message.content.startswith("!"):
            logging.debug("on_message event was triggered")
            await asyncio.sleep(5)
            await message.delete()

    # someone adds a reaction anywhere the bot can see it
    async def on_raw_reaction_add(self, payload):
        pass

    async def game_sendMessageTask(self):
        logging.debug("sendMessageTask was started")
        await self.wait_until_ready()
        while not self.is_closed():
            if not self.game_sendMessages:
                await asyncio.sleep(1)  # task runs every second
                continue
            try:
                message = self.game_message_queue.get(block=False)
                logging.debug("Message object was retrieved succesfully")
            except:
                logging.debug("Message object was not retrieved")
                await asyncio.sleep(1)  # task runs every second
                continue
            if message.type == MessageType.CHANNEL:
                logging.debug("Message Type is Channel")
                target = self.game_channels[message.target]
                await target.send(message.content)
                logging.debug("Message was sent successfully")
            else:
                logging.debug("Message Type is not Channel")
            await asyncio.sleep(1)  # task runs every second

    def game_sendMessage(self, message : Message):
        self.game_message_queue.put(message)
        return