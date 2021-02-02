import logging
import discord
from queue import Queue, Empty
from Message import *
import asyncio
import Settings_local as Settings

# noinspection PyUnreachableCode
if False:
    from EscapeRoom import EscapeRoom


class DiscordBot(discord.Client):

    def __init__(self, controller: "EscapeRoom"):
        super().__init__()

        self.messageQueue = Queue()

        self.controller = controller

        self.sendMessageTask = self.loop.create_task(self.dispatch_messages())
        self.enableMessaging = False
        return

    # logged in and prepared
    async def on_ready(self):
        self.server: discord.Guild = self.get_guild(767358980241621012)  # discord Server
        for channel in self.server.channels:
            await channel.delete()

        await self.controller.setup_discord()
        self.enableMessaging = True
        logging.info("Bot is online")

    # someone sends a message anywhere the bot can read it
    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if message.content.startswith(Settings.commandPrefix + "register"):
            content = message.content.strip(Settings.commandPrefix + "register").strip(" ")
            if content == "":
                content = None
            await self.controller.register_player(message.author, content)

        elif message.content.startswith(Settings.commandPrefix):
            logging.debug("Command Prefix Detected: " + message.content)
            split = message.content.split(" ", 1)
            command = split[0].lstrip("!")
            content = None if len(split) < 2 else split[1]
            await self.controller.handle_command(message.author, command, content)
            # await asyncio.sleep(5)
            # await message.delete()
        else:
            await self.controller.handle_command(message.author, None, message.content)

    # someone adds a reaction anywhere the bot can see it
    async def on_raw_reaction_add(self, payload):
        pass

    async def dispatch_messages(self):
        await self.wait_until_ready()
        while not self.is_closed():
            while self.enableMessaging:
                try:
                    message = self.messageQueue.get(block=False)
                    await message.target.send(message.content)
                except Empty:
                    break
            await asyncio.sleep(1)  # task runs every second

    def send_message(self, message: Message):
        self.messageQueue.put(message)
        return
