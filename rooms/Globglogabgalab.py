from Room import Room
import asyncio
import logging


class BossRoom(Room):
    def __init__(self, game):
        super().__init__("Globglogabgalab", game)

        self.ritualtext = "Isithathu nesibini kunye nenye Masambe"
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
        self.ropeendings = 0
        self.counter = 0
        self.can_photo = False
        self.photo_shot = False
        self.items_to_take = []
        self.pulling_power = 0
        self.birol_follows_iris = False

        # register commands
        self.register_command("give", self.giveItem, "Item ablegen damit es jemand anderes nehmen kann")
        self.register_command("take", self.takeItem, "Item nehmen, welches jemand anderes abgelegt hat")
        self.register_command("shout", self.startRiutal, "Text rufen um Ritual zu starten")
        self.register_command("knot", self.knotRopeToBook, "Knoten machen")
        self.register_command("climb-and-place", self.climbUpAndPlaceBook, "Buch hinlegen")
        self.register_command("light-on", self.turnLightOn, "Fackel anzünden")
        self.register_command("light-off", self.turnLightOff, "Fackel löschen")
        self.register_command("pull", self.pullBookWithRope, "an Seil mit Buch ziehen")
        self.register_command("follow-Iris", self.followIris, "Iris folgen")
        self.register_command("guide", self.guideBirol, "Iris bringt Birol zum Loch")
        self.register_command("picture", self.takePicture, "macht Foto")
        self.register_command("pick-up-rope", self.grabRopeEnding, "Seil in die Hand nehmen")

    async def enter(self, player):
        self.lock.acquire()
        self.players.append(player)
        await self.game.show_room(self, player, text=True, voice=True)
        self.lock.release()

    # Item ablegen damit es jemand anderes aufnehmen kann
    async def giveItem(self, player, command, content):
        if content in player.inventory:
            player.inventory.remove(content)
            self.items_to_take.append(content)
            player.currentRoom.send(content + " liegt jetzt auf dem Boden")
        else:
            player.send("Dieses Item hast du nicht.")

    # Item aufnehmen
    async def takeItem(self, player, command, content):
        if content in self.items_to_take:
            self.items_to_take.remove(content)
            player.inventory.append(content)
            player.currentRoom.send(player.name + " hat jetzt: " + content)
        else:
            player.currentRoom.send(" Dieses Item liegt nirgendwo")

    # the great plan
    async def startRiutal(self, player, command, content):
        if content.strip(" ") == self.ritualtext and player.id == "Tusitalafou der Reviewer":
            player.currentRoom.send("Ritual gestartet.")
            await asyncio.sleep(19)
            # g. appears
            if self.light1_on or self.light2_on:
                player.currentRoom.send("Globglogabgalab kommt irgendwie nicht heraus.")
                player.currentRoom.send("Fangt noch einmal von vorne an.")
                await self.resetRoom()
                return
            elif self.birol_in_position:
                player.currentRoom.send("Globglogabgalab kommt irgendwie nicht heraus.")
                player.currentRoom.send("Fangt noch einmal von vorne an.")
                await self.resetRoom()
                return
            player.currentRoom.send("Globglogabgalab erscheint und sucht nach einem seiner entwendeten Bücher.")
            await asyncio.sleep(0.5)
            # g. stays to grab book
            if not self.book_in_position:
                player.currentRoom.send("Globglogabgalab kann kein Buch finden und verschwindet wieder in sein Loch.")
                player.currentRoom.send("Fangt noch einmal von vorne an.")
                await self.resetRoom()
                return
            player.currentRoom.send("Globglogabgalab entdeckt das Buch und läuft los um es aufzuheben.")
            await asyncio.sleep(3)
            # g. follows moving book
            if not self.book_moving:
                if self.book_prepared:
                    player.currentRoom.send("Globglogabgalab scheitert am Knoten und verschwindet wieder.")
                    player.currentRoom.send("Fangt noch einmal von vorne an.")
                    await self.resetRoom()
                    return
                player.currentRoom.send("Globglogabgalab will das Buch mitnehmen, aber ein Geräusch erschreckt ihn und"
                                        "er flüchtet in die Dunkelheit.")
                player.currentRoom.send("Fangt noch einmal von vorne an.")
                await self.resetRoom()
                return
            player.currentRoom.send("Globglogabgalab flogt dem Buch.")
            # light on or lost
            while not self.light1_on and not self.light2_on:
                await asyncio.sleep(1)
                self.counter += 1
                # lost
                if self.counter == 8:
                    player.currentRoom.send("Globglogabgalab bemerkt das Lockmanöver verschwindet wieder.")
                    player.currentRoom.send("Fangt noch einmal von vorne an.")
                    await self.resetRoom()
                    return
            # light on
            player.currentRoom.send("Globglogabgalab erschrickt und flüchtet Richtung Höhle")
            await asyncio.sleep(2)
            if not self.birol_in_position:
                player.currentRoom.send("Keiner kann verhindern das Globglogabgalab wieder verschwindet")
                player.currentRoom.send("Fangt noch einmal von vorne an.")
                await self.resetRoom()
                return
            player.currentRoom.send("Birols Größe lässt Globglogabgalab innehalten.")
            await asyncio.sleep(5)
            if self.photo_shot:
                await self.rewardPlayers()
                return
            player.currentRoom.send("Globglogabgalab erkennt Birols Freudlichkeit und läuft an ihm vorbei.")
        # start not spelledd correct
        else:
            player.currentRoom.send("Erst Totenstille ...")
            await asyncio.sleep(2)
            player.currentRoom.send("... und dann ...")
            await asyncio.sleep(2)
            player.currentRoom.send("... passiert nichts")
            player.currentRoom.send("Fangt noch einmal von vorne an.")
            await self.resetRoom()

    async def knotRopeToBook(self, player, command, content):
        if "Seil" not in player.inventory or "Buch" not in player.inventory:
            player.currentRoom.send("Dafür fehlt dir noch etwas in deinem Inventar")
        elif "Nyja mit den geschickten Fingern" != player.character:
            player.currentRoom.send("Du hast alles was man braucht außer das nötige Talent.")
        elif not self.light1_on and not self.light2_on:
            player.currentRoom.send("Man sagt zwar du könntest alle Knoten im Schlaf, aber im Dunkel "
                                    "schaffst du es leider nicht.")
        else:
            self.book_prepared = True
            self.ropeendings = 2
            player.currentRoom.send("Das Seil ist mit einem deiner Speizalknoten am Buch befestigt.")

    async def grabRopeEnding(self, player, command, content):
        if not self.ropeendings:
            player.currentRoom.send("Schön das du das Seil festhalten willst, aber der Fachmann braucht beide Seilenden"
                                    "für seinen Spezialknoten. FLoglich lässt du wieder los.")
        elif player in self.pulling_players or "Seil" in player.inventory:
            player.currentRoom.send("Du hälst das Seil bereits mit fest.")
        else:
            self.ropeendings -= 1
            self.pulling_players.append(player)
            player.currentRoom.send(player.name + " hält das Seil mit fest.")

    async def climbUpAndPlaceBook(self, player, command, content):
        if not self.light1_on or not self.light2_on:
            player.currentRoom.send("Im Dunkeln kommt man da nicht hoch.")
        elif player.character != "Ormänniska der Gelenkige":
            player.currentRoom.send("**DU** kommst da leider nicht hoch. Frag mal jemand anderen.")
        elif player.inventory.count("Kletterschuhe") == 2:
            player.currentRoom.send("Ohne 2 Kletterschuhe kommst auch du da nicht hoch")
        elif "Buch" not in player.inventory:
            player.currentRoom.send("Du solltest ein Buch mitnehmen wenn du es hier obe hinlegen willst.")
        else:
            self.book_in_position = True
            player.currentRoom.send("Das Buch wurde vor dem Loch abgelegt")

    async def pullBookWithRope(self, player, command, content):
        if not self.book_prepared:
            player.currentRoom.send("Ihr solltet das Seil schon am Buch befestigen sonst"
                                    " braucht man auch nicht ziehen.")
        elif "Seil" not in player.inventory and player not in self.pulling_players:
            player.currentRoom.send("Du hast das Seil nicht in der Hand.")
        else:
            self.pulling_power += 1
            if self.pulling_power < 4:
                player.currentRoom.send("Du ziehst am Seil, aber es hängt noch irgendwo fest. Ihr braucht mehr"
                                        " Leute zum ziehen")
            else:
                self.book_moving = True
                player.currentRoom.send("Das Seil bewegt sich und ihr zieht das Buch in eure Richtung.")

    async def turnLightOn(self, player, command, content):
        if "Feuerzeug" not in player.inventory:
            player.room.send("Du hast nichts um die Fackel anzuzünden")
            return
        elif content == "1":
            if player in self.atlight2:
                player.room.send("Du bist noch auf dem Weg zur anderen Fackel.")
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
                player.room.send("Du bist noch auf dem Weg zur anderen Fackel.")
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

    async def followIris(self, player, command, content):
        if player.character != "Birol der gigantische Wächter":
            player.currentRoom.send("Du solltest besser hier bleiben, denn du wirst gebraucht.")
        else:
            self.birol_follows_iris = True

    async def guideBirol(self, player, command, content):
        if not self.birol_follows_iris:
            player.currentRoom.send("Iris dir folgt niemand.")
        elif "Playmobilmännchen" not in player.inventory:
            player.currentRoom.send("Ohne seinen treuen Begleiter geht Birol im dunkeln nirgendwo hin.")
        else:
            player.currentRoom.send("Birol folgt dir durch die Dunkelheit")
            await asyncio.sleep(5)
            self.birol_in_position = True
            player.currentRoom.send("Birol steht jetzt vor dem Loch.")

    async def takePicture(self, player, comamnd, content):
        if player.character != "Sheying der Fotograf":
            player.currentRoom.send("Es gibt jemand besseren für den Job.")
            return
        if "Fotoapparat" not in player.inventory:
            player.currentRoom.send("Dir fehlt noch etwas entscheidendes zum Foto machen.")
            return
        if self.light1_on and self.light2_on:
            if self.can_photo:
                self.photo_shot = True
            else:
                player.room.send("Auf dem Foto ist Globglogabgalab leider nicht zu sehen.")
        else:
            player.currentRoom.send("Bei diesen Lichtverhältnissen wir das nichts mit einem guten Bild.")

    async def resetRoom(self):
        self.ritualtext = "Isithathu nesibini kunye nenye Masambe"
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
        self.ropeendings = 0
        self.counter = 0
        self.can_photo = False
        self.photo_shot = False
        self.items_to_take = []
        self.pulling_power = 0
        self.birol_follows_iris = False

    async def rewardPlayers(self):
        self.send("Geschafft!")
