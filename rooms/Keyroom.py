from Room import Room
from .PrivateRoom import PrivateRoom
import datetime
import discord
import asyncio
import logging
from typing import Dict

# noinspection PyUnreachableCode
if False:
    import Player

entrymessage = "Hier kommt der Entrytext hin."
result = 12345


class Keyroom(Room):
    def __init__(self, game):
        self.game = game
        super().__init__("Kerker", game)
        self.__rooms = {}
        self.__lasttry: Dict[str, datetime.datetime] = {}
        self.nextroom = self.game.get_room("Zwei Türen")

        self.register_command("pin", self.pin, "Benutze '!pin #####' um eine Lösung einzugeben.")
        self.register_command("skip", self.skip, "Kann von Mods benutzt werden um den Raum zu überspringen.")

    async def enter(self, player):
        self.players.append(player)
        private = PrivateRoom(self, nameappend=" " + player.name)
        self.__rooms[player] = private
        await private.setup()
        await private.enter(player)
        await self.game.show_room(private, player, text=True)
        private.send(entrymessage)
        with open("resources/keyroom_colored.png", "rb") as keyimage:
            private.send(discord.File(keyimage))   # funktioniert nur beim ersten Spieler der dem Raum betritt

    @Room.requires_mod
    async def skip(self, player, command, content):
        nextroom = self.game.get_room("Zwei Türen")
        for player in list(self.get_players()):
            await self.leave(player)
            await nextroom.enter(player)

    async def leave(self, player: "Player"):
        await self.game.hide_room(player.currentRoom, player)
        await player.currentRoom.leave(player)
        self.players.remove(player)

    async def pin(self, player, command, content):
        lasttime = self.__lasttry.get(player, None)
        current = datetime.datetime.now()
        if lasttime is not None and (current - lasttime) > datetime.timedelta(minutes=1):
            player.currentRoom.send("Du musst noch warten, bevor du eine weitere Eingabe tätigen kannst.")
            return

        try:
            pin = int(content)
        except:
            player.currentRoom.send("Diese Eingabe ist keine gültige Zahl.")
            return

        if pin == result:
            player.currentRoom.send("Die Kerkertür öffnet sich.")
            nextroom = self.game.get_room("Zwei Türen")
            await asyncio.sleep(5)
            await self.leave(player)
            await nextroom.enter(player)
        else:
            player.currentRoom.send("Dies ist leider nicht das richtige Ergebnis."
                                    "Versuche es in einer Minute noch einmal.")
