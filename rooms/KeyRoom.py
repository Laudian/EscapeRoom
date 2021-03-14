from Room import Room
from PrivateRoom import PrivateRoom
import datetime
import discord
import time
import logging
from typing import Dict

entrymessage = "Hier kommt der Entrytext hin."
result = 12345

with open("/resources/keyroom_colored.png", "rb") as imagefile:
    keyimage = discord.File(imagefile)


class KeyRoom(Room):
    def __init__(self, game):
        self.game = game
        super().__init__("Kerker", game)
        self.__rooms = {}
        self.__lasttry: Dict[str, datetime.datetime] = {}
        self.nextroom = self.game.get_room("Eingangshalle")

        self.register_command("pin", self.pin, "Benutze '!pin 12345' um eine Lösung einzugeben.")

    async def enter(self, player):
        private = PrivateRoom(self, nameappend=" " + player.name)
        self.__rooms[player] = private
        await private.setup()
        await private.enter(player)
        await self.game.show_room(private, player, text=True)
        private.send(entrymessage)
        private.send(keyimage)

    def pin(self, player, content):
        lasttime = self.__lasttry.get(player, None)
        current = datetime.datetime.now()
        if lasttime is not None and (current - lasttime) < datetime.timedelta(minutes=1):
            player.currentRoom.send("Du musst noch warten, bevor du eine weitere Eingabe tätigen kannst.")
            return

        try:
            pin = int(content)
        except:
            player.currentRoom.send("Diese Eingabe ist keine gültige Zahl.")
            return

        if pin == result:
            player.currentRoom.send("Die Kerkertür öffnet sich.")
            time.sleep(secs=5)
            self.leave(player)
            self.nextroom.enter(player)
