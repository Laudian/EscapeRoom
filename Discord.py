import logging
import discord
from queue import Queue
from Message import *
import asyncio


class DiscordBot(discord.Client):

    def __init__(self, game):
        super.__init__()

        self.game_users = {}

        self.game_channels = {}

        self.game_message_queue = Queue()

        self.game = game

        self.game_sendMessageTask = self.loop.create_task(self.game_sendMessageTask())
        return


    # logged in and prepared
    async def on_ready(self):
        self.game_channels[self.game.room.name] = self.get_channel(784596953496813598)
        logging.info("Bot is online")

    # someone sends a message anywhere the bot can read it
    async def on_message(self, message):
        if message.content.startswith("!"):
            logging.debug("on_message event was triggered")

    # someone adds a reaction anywhere the bot can see it
    async def on_raw_reaction_add(self, payload):
        pass

    async def game_sendMessageTask(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                message = self.game_message_queue.get(block=False)
            except:
                continue
            if message.type == MessageType.CHANNEL:
                target = self.get_channel(message.target)
                target.send(message.content)
            # await asyncio.sleep(60)  # task runs every 60 seconds

    def game_sendMessage(self, message : Message):
        self.game_message_queue.put(message)
        return