import logging
import discord
from queue import Queue
from Message import *
import asyncio
import Player


class DiscordBot(discord.Client):

    def __init__(self, game):
        super().__init__()

        # Dict of {player : discorduser}
        self.game_users = {}

        # Dict of {room : discordchannel}
        self.game_channels = {}

        self.game_message_queue = Queue()

        self.game = game

        self.game_sendMessageTask = self.loop.create_task(self.game_MessageDispatcher())
        self.game_sendMessages = False
        return

    # translates a discord channel into a game room
    # returns None if there is no room associated with that channel
    def getRoom(self, channel):
        reversed = {value: key for (key, value) in self.game_channels.items()}
        return reversed.get(channel, None)

    # translates a discord user into a game player
    # returns None if that user is not in the game
    def getPlayer(self, user) -> Player.Player:
        reversed = {value: key for (key, value) in self.game_users.items()}
        return reversed.get(user, None)

    # logged in and prepared
    async def on_ready(self):
        self.game_channels[self.game.room] = self.get_channel(784596953496813598)
        self.game_sendMessages = True
        logging.info("Bot is online")

    # someone sends a message anywhere the bot can read it
    async def on_message(self, message:discord.Message):
        if message.content == "!register":
            if message.author in self.game_users.items():
                message.author.send("Du bist bereits angemeldet")
                logging.debug("User tried to register but was already registered")
            else:
                player = self.game.registerPlayer(message.author.name)
                self.game_users[player] = message.author
                player.send("Du wurdest erfolgreich angemeldet")
                logging.debug("User {name} was successfully registered".format(name=message.author.name))
                self.game.room.enter(player)

        elif message.content.startswith("!"):
            logging.debug("on_message event was triggered")
            split = message.content.split(" ", 1)
            command = split[0].lstrip("!")
            content = None if len(split) < 2 else split[1]
            self.game.handleCommand(self.getPlayer(message.author), command, content)
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
                        continue
                    await target.send(message.content)
                except:
                    break
            await asyncio.sleep(1)  # task runs every second


    def game_sendMessage(self, message : Message):
        self.game_message_queue.put(message)
        return