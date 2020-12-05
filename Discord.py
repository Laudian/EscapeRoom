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

        self.game_sendMessageTask = self.loop.create_task(self.game_MessageDispatcher())
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

    async def game_MessageDispatcher(self):
        await self.wait_until_ready()
        while not self.is_closed():
            while self.game_sendMessages:
                try:
                    message = self.game_message_queue.get(block=False)
                    if message.target.message_type == MessageType.CHANNEL:
                        target = self.game_channels[message.target]
                    elif message.target.message_type == MessageType.PLAYER:
                        target = self.game_users[message.target]
                    else:
                        logging.debug("Messagetype unknown")
                    await target.send(message.content)
                except:
                    break
            await asyncio.sleep(1)  # task runs every second


    def game_sendMessage(self, message : Message):
        self.game_message_queue.put(message)
        return