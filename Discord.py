import logging
import discord
import asyncio


class DiscordBot(discord.Client):
    # logged in and prepared
    async def on_ready(self):
        logging.info("Bot is online")

    # someone sends a message anywhere the bot can read it
    async def on_message(self, message):
        if message.startswith("!"):
            await asyncio.sleep(5)
            message.delete()

    # someone adds a reaction anywhere the bot can see it
    async def on_raw_reaction_add(self, payload):
        pass
