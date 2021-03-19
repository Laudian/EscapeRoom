from Room import Room
import asyncio
import logging


class BossRoom(Room):   #TODO add comments
    def __init__(self, game):
        super().__init__("Globglogabgalab", game)

        self.ritualtext = "Noch zu erstellen"
        self.light1_on = True
        self.light2_on = True
        self.atlight1 = []
        self.atlight2 = []
        self.lighter_blocked = False
        self.birol_in_position = False
        self.book_in_position = False
        self.book_prepared = False
        self.book_moving = False
        self.pulling_players = []
        self.ropeendings = -1
        self.counter = 0
        self.can_photo = False
        self.photo_shot = False

        # TODO register commands

    async def enter(self, player):
        self.lock.acquire()
        self.players.append(player)
        await self.game.show_room(self, player, text=True, voice=True)
        self.lock.release()

    async def giveItem(self, player, command, content):
        pass  #  TODO

    async def checkRitualSpelling(self, player, command, content):
        if content.strip(" ") == self.ritualtext and player.id == "Tusitalafou der Reviewer":
            player.currentRoom.send("Ritual gestartet")
            await asyncio.sleep(30)
            # g. appears
            if self.light1_on or self.light2_on:
                player.currentRoom.send("Globglogabgalab kommt irgendwie nicht heraus")
                return
            elif self.birol_in_position:
                player.currentRoom.send("Globglogabgalab kommt irgendwie nicht heraus")
                return
            player.currentRoom.send("Globglogabgalab erscheint und sucht nach einem seiner entwendeten Bücher")
            await asyncio.sleep(2)
            # g. stays to grab book
            if not self.book_in_position:
                player.currentRoom.send("G. kann kein Buch finden und verschwindet wieder in seiner Höhle")
                return
            player.currentRoom.send("Entdeckt das Buch und läuft los um es aufzuheben")
            await asyncio.sleep(3)
            # g. follows moving book
            if not self.book_moving:
                if self.book_prepared:
                    player.currentRoom.send("globglo löst knoten und nimmt buch mit")
                    return
                player.currentRoom.send("globglo nimmt buch mit")
                return
            player.currentRoom.send("g. flogt dem buch")
            lost = False
            # licht an oder lost
            while not self.light1_on and not self.light2_on:
                await asyncio.sleep(1)
                self.counter += 1
                # lost
                if self.counter == 15:
                    player.currentRoom.send("g. bemerkt das lockmanöver flüchtet")
                    return
            # licht an
            player.currentRoom.send("g. erschrickt und flüchtet Richtung Höhle")
            await asyncio.sleep(2)
            if not self.birol_in_position:
                player.currentRoom.send("Keiner kann verhindern das g. wieder verschwindet")
                return
            player.currentRoom.send("Birols Größe lässt g. kurz innehalten")
            await asyncio.sleep(2)
            if self.photo_shot:
                await self.rewardPlayers()
                return
            player.currentRoom.send("g. erkennt Birols Freudlichkeit und läuft an ihm vorbei")

    async def knotRopeToBook(self, player, command, content):
        if "rope" in player.inventory and "book" in player.inventory and player.character == "Knotenmensch":
            self.ropeendings = 2
            self.book_prepared = True

    async def grabRopeEnding(self, player, command, content):
        if self.ropeendings and player not in self.pulling_players:
            self.ropeendings -= 1
            self.pulling_players.append(player)

    async def climbUpAndPlaceBook(self, player, command, content):
        if player.inventory.count("Kletterschuh") == 2 and player.character == "Ormänniska der Gelenkige":
            self.book_in_position = True

    async def pullBookWithRope(self, player, command, content):
        if self.book_prepared and "rope" in player.inventory and self.ropeendings == 0:
            self.book_moving = True

    async def turnLightOn(self, player, command, content):
        if "Feuerzeug" not in player.inventory:
            player.room.send("sorry aber du hast nichts um die Fackel anzuzünden")
            return
        elif content == "1":
            if player in self.atlight2:
                player.room.send("sorry aber du stehst noch nicht wieder an der anderen Fackel")
                return
            self.light1_on = True
            self.atlight1.append(player)
            self.lighter_blocked = True
            if player.character == "Rinua die Flinke":
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(5)
            self.atlight1.remove(player)
            self.lighter_blocked = False
        elif content == "2":
            if player in self.atlight1:
                player.room.send("sorry aber du stehst noch nicht wieder an der anderen Fackel")
                return
            self.light2_on = True
            self.atlight2.append(player)
            self.lighter_blocked = True
            if player.character == "Rinua die Flinke":
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(5)
            self.atlight2.remove(player)
            self.lighter_blocked = False
        else:
            player.room.send("Welche Fackel willst du anzünden? 1 oder 2?")

    async def turnLightOff(self, player, command, content):
        if content == "1":
            if player in self.atlight2:
                player.room.send("sorry aber du stehst noch nicht wieder an der anderen Fackel")
                return
            self.light1_on = False
            self.atlight1.append(player)
            if player.character == "Rinua die Flinke":
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(5)
            self.atlight1.remove(player)
        elif content == "2":
            if player in self.atlight1:
                player.room.send("sorry aber du stehst noch nicht wieder an der anderen Fackel")
                return
            self.light2_on = False
            self.atlight2.append(player)
            if player.character == "Rinua die Flinke":
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(5)
            self.lighter_blocked = False
        else:
            player.room.send("Welche Fackel willst du löschen? 1 oder 2?")

    async def guideBirol(self, player, command, content):
        pass  #TODO create puzzle?

    async def takePicture(self, player, comamnd, content):
        if self.light1_on and self.light2_on:
            if self.can_photo:
                self.photo_shot = True
            else:
                player.room.send("Auf dem Foto ist g. leider nicht zu sehen")
        else:
            player.currentRoom.send("bei diesen Lichtverhältnissen wir das nichts mit einem guten Bild")

    async def resetRoom(self):
        self.light1_on = True
        self.light2_on = True
        self.atlight1 = []
        self.atlight2 = []
        self.lighter_blocked = False
        self.birol_in_position = False
        self.book_in_position = False
        self.book_prepared = False
        self.book_moving = False
        self.pulling_players = []
        self.ropeendings = -1
        self.counter = 0
        self.can_photo = False
        self.photo_shot = False

    async def rewardPlayers(self):
        self.send("Geschafft!")

    async def deletePhoto(self):
        pass
