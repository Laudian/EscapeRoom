import logging
import discord
from queue import Queue, Empty
from Message import *
import asyncio
import Player
import Settings_local as Settings


class DiscordBot(discord.Client):

    def __init__(self, controller):
        super().__init__()

        self.messageQueue = Queue()

        self.controller = controller

        self.sendMessageTask = self.loop.create_task(self.dispatch_messages())
        self.enableMessaging = False
        return

    # logged in and prepared
    async def on_ready(self):
        self.controller.register_rooms()
        self.enableMessaging = True
        logging.info("Bot is online")

    # someone sends a message anywhere the bot can read it
    async def on_message(self, message: discord.Message):
        if message.content == Settings.commandPrefix + "register":
            self.controller.register_player(message.author)

        elif message.content.startswith(Settings.commandPrefix):
            logging.debug("on_message event was triggered")
            split = message.content.split(" ", 1)
            command = split[0].lstrip("!")
            content = None if len(split) < 2 else split[1]
            self.controller.handle_command(message.author, command, content)
            await asyncio.sleep(5)
            await message.delete()

    # someone adds a reaction anywhere the bot can see it
    async def on_raw_reaction_add(self, payload):
        pass

    async def dispatch_messages(self):
        await self.wait_until_ready()
        while not self.is_closed():
            while self.enableMessaging:
                try:
                    message = self.messageQueue.get(block=False)
                    if message.target.message_type == MessageType.CHANNEL:
                        target = self.controller.room_to_discord(message.target)
                    elif message.target.message_type == MessageType.PLAYER:
                        target = self.controller.player_to_discord(message.target)
                    else:
                        logging.debug("Message type unknown")
                        continue
                    await target.send(message.content)
                except Empty:
                    break
            await asyncio.sleep(1)  # task runs every second


    def send_message(self, message : Message):
        self.messageQueue.put(message)
        return
