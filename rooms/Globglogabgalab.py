from Room import Room
import asyncio
import logging


class BossRoom(Room):
    def __init__(self, game):
        super().__init__("Globglogabgalab", game)

        self.empty = True
        self.ritualtext = "Isithathu nesibini kunye nenye Masambe"
        self.light1_on = True
        self.light2_on = True
        self.atlight1 = []
        self.atlight2 = []
        self.lighter_blocked = False
        self.birol_in_position = False
        self.book_position = []
        self.book_prepared = False
        self.book_moving = False
        self.pulling_players = []
        self.items_to_take = []
        self.ropeendings = False
        self.counter = 0
        self.can_photo = False
        self.photo_shot = False
        self.pulling_power = 0
        self.birol_follows_iris = False
        self.startmessage = ("Geschafft! Ihr habt alle Passwörter herausgefunden und an den richtigen Eingabetafeln "
                             "eingegeben. Nun seid ihr wieder alle vereint in einer großen Halle. Und nach allem was "
                             "ihr von den Berichten von Prof Firnossepor Athro Pilazanigisiti gehört habt, muss das die"
                             " Höhle sein, in der der Globglogabgalab zu finden sein muss. Bisher aber keine Spur von "
                             "ihm. Nur die 2 Fackeln an den beiden langen Enden des Raumes. Eine kleine klippenartige "
                             "Erhöhung im Raum und an der Wand dahinter ein tiefdunkles Loch. Einige Felsen und "
                             "Stalagmiten und an einer Wand seht ihr auch das große Tor mit der Stasimopus Robertsi "
                             "wieder! Nachdem sich alle ausgiebig umgeschaut haben, kommt ihr zusammen und versucht "
                             "euch an das zu erinnern, was euch der Prof. erzählt hat:\n“Wir wurden alle aufgrund "
                             "unserer Talente ausgewählt und hatten eine bestimmte Aufgabe zu erfüllen. Um den "
                             "Globglogabgalab abzulichten müssen wir ihn, sofern er denn wirklich hier zuhause ist, aus"
                             " seinem Versteck locken.”\nLeider kann sich niemand mehr an die eigenen "
                             "Spezialfähigkeiten oder die Art wie man ihn für das Bild vor die Kamera bekommt, "
                             "erinnern. Der heftige Schlag auf den Hinterkopf ganz am Anfang scheint doch Schäden "
                             "hinterlassen zu haben. Grade so bekommt ihr noch zusammen: Der Globglogabgalab liebt "
                             "Bücher, darf niemanden von euch sehen oder hören und ist sehr schreckhaft! Ihr habt auch "
                             "noch die Gegenstände dabei, die euch aus dem Tunnel nachgeflogen kamen. Weiterhin stehen "
                             "euch folgende Aktionen zur Verfügung, um den Globglogabgalab zu fotographieren:\n!take\n"
                             "!drop\n!picture\n!climb-and-place\n!light-on\n!shout Isithathu nesibini kunye nenye "
                             "Masambe\n!light-off\n!knot\n!pull\n!pick-up-rope\n!follow-Iris\n!guide\n!inventory\n")

        # register commands
        self.register_command("drop", self.dropItem, "Item ablegen")
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
        self.register_command("inventory", self.inventory, "sein eigenes Inventar anzeigen anlassen")

    async def enter(self, player):
        await super().enter(player)
        await self.game.show_room(self, player, text=True, voice=True)
        if self.empty:
            self.empty = False
            self.send(self.startmessage)

    # show a players inventory
    async def inventory(self, player, command, content):
        self.send(str(player.inventory).strip("[]"))

    # Item ablegen damit es jemand anderes aufnehmen kann
    async def dropItem(self, player, command, content):
        if content in player.inventory:
            player.inventory.remove(content)
            self.items_to_take.append(content)
            self.send(content + " liegt jetzt auf dem Boden")
        else:
            self.send("Dieses Item hast du nicht.")

    # Item aufnehmen
    async def takeItem(self, player, command, content):
        if content in self.items_to_take:
            self.items_to_take.remove(content)
            player.inventory.append(content)
            self.send(player.name + " hat jetzt: " + content)
        else:
            self.send("Dieses Item liegt nirgendwo")

    # the great plan
    async def startRiutal(self, player, command, content):
        if content.strip(" ") == self.ritualtext and player.character == "Tusitalafou der Reviewer":
            self.send("Ritual gestartet.")
            await asyncio.sleep(19)
            # g. appears
            if self.light1_on or self.light2_on:
                self.send("Globglogabgalab kommt irgendwie nicht heraus.")
                self.send("Fangt noch einmal von vorne an.")
                await self.resetRoom()
                return
            elif self.birol_in_position:
                self.send("Globglogabgalab kommt irgendwie nicht heraus.")
                self.send("Fangt noch einmal von vorne an.")
                await self.resetRoom()
                return
            self.send("Globglogabgalab erscheint und sucht nach einem seiner entwendeten Bücher.")
            await asyncio.sleep(0.5)
            # g. stays to grab book
            if not self.book_in_position:
                self.send("Globglogabgalab kann kein Buch finden und verschwindet wieder in sein Loch.")
                self.send("Fangt noch einmal von vorne an.")
                await self.resetRoom()
                return
            self.send("Globglogabgalab entdeckt das Buch und läuft los um es aufzuheben.")
            await asyncio.sleep(3)
            # g. follows moving book
            if not self.book_moving:
                if self.book_prepared:
                    self.send("Globglogabgalab scheitert am Knoten und verschwindet wieder.")
                    self.send("Fangt noch einmal von vorne an.")
                    await self.resetRoom()
                    return
                self.send("Globglogabgalab will das Buch mitnehmen, aber ein Geräusch erschreckt ihn und"
                                        "er flüchtet in die Dunkelheit.")
                self.send("Fangt noch einmal von vorne an.")
                await self.resetRoom()
                return
            self.send("Globglogabgalab flogt dem Buch.")
            # light on or lost
            while not self.light1_on and not self.light2_on:
                await asyncio.sleep(1)
                self.counter += 1
                # lost
                if self.counter == 8:
                    self.send("Globglogabgalab bemerkt das Lockmanöver verschwindet wieder.")
                    self.send("Fangt noch einmal von vorne an.")
                    await self.resetRoom()
                    return
            # light on
            self.send("Globglogabgalab erschrickt und flüchtet Richtung Höhle")
            await asyncio.sleep(2)
            if not self.birol_in_position:
                self.send("Keiner kann verhindern das Globglogabgalab wieder verschwindet")
                self.send("Fangt noch einmal von vorne an.")
                await self.resetRoom()
                return
            self.send("Birols Größe lässt Globglogabgalab innehalten.")
            await asyncio.sleep(5)
            if self.photo_shot:
                await self.rewardPlayers()
                return
            self.send("Globglogabgalab erkennt Birols Freudlichkeit und läuft an ihm vorbei.")
        # start not spelled correct
        else:
            self.send("Erst Totenstille ...")
            await asyncio.sleep(3)
            self.send("... und dann ...")
            await asyncio.sleep(3)
            self.send("... passiert nichts")
            self.send("Fangt noch einmal von vorne an.")
            await self.resetRoom()

    async def knotRopeToBook(self, player, command, content):
        if "Seil" not in player.inventory or "Buch" not in player.inventory:
            self.send("Dafür fehlt dir noch etwas in deinem Inventar")
        elif "Nyja mit den geschickten Fingern" != player.character:
            self.send("Du hast alles was man braucht außer das nötige Talent.")
        elif not self.light1_on and not self.light2_on:
            self.send("Man sagt zwar du könntest alle Knoten im Schlaf, aber im Dunkeln "
                                    "schaffst du es leider nicht.")
        else:
            self.book_prepared = True
            self.ropeendings = True
            self.send("Das Seil ist mit einem deiner Spezialknoten am Buch befestigt.")

    async def grabRopeEnding(self, player, command, content):
        if not self.ropeendings:
            self.send("Schön das du das Seil festhalten willst, aber der Fachmann braucht beide Seilenden"
                      " für seinen Spezialknoten. FLoglich lässt du wieder los.")
        elif player in self.pulling_players or "Seil" in player.inventory:
            self.send("Du hälst das Seil bereits mit fest.")
        else:
            self.pulling_players.append(player)
            self.send(player.name + " hält das Seil mit fest.")

    async def climbUpAndPlaceBook(self, player, command, content):
        if not self.light1_on or not self.light2_on:
            self.send("Im Dunkeln kommt man da nicht hoch.")
        elif player.character != "Ormänniska der Gelenkige":
            self.send("**DU** kommst da leider nicht hoch. Frag mal jemand anderen.")
        elif player.inventory.count("Kletterschuhe") == 2:
            self.send("Ohne 2 Kletterschuhe kommst auch du da nicht hoch")
        elif "Buch" not in player.inventory:
            self.send("Du solltest ein Buch mitnehmen wenn du es hier oben hinlegen willst.")
        else:
            self.book_position.append("Buch")
            player.inventory.remove("Buch")
            self.send("Das Buch wurde vor dem Loch abgelegt")

    async def pullBookWithRope(self, player, command, content):
        if not self.book_prepared:
            self.send("Ihr solltet das Seil schon am Buch befestigen sonst braucht man auch nicht ziehen.")
        elif "Seil" not in player.inventory and player not in self.pulling_players:
            self.send("Du hast das Seil nicht in der Hand.")
        else:
            self.pulling_power += 1
            if self.pulling_power < 4:
                self.send("Du ziehst am Seil, aber es hängt noch irgendwo fest. Ihr braucht mehr Leute zum ziehen")
            else:
                self.book_moving = True
                self.send("Das Seil bewegt sich und ihr zieht das Buch in eure Richtung.")

    async def turnLightOn(self, player, command, content):
        if "Feuerzeug" not in player.inventory:
            self.send("Du hast nichts um die Fackel anzuzünden")
            return
        elif content == "1":
            if player in self.atlight2:
                self.send("Du bist noch auf dem Weg zur anderen Fackel.")
                return
            self.light1_on = True
            self.send("Fackel 1 ist an.")
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
                self.send("Du bist noch auf dem Weg zur anderen Fackel.")
                return
            self.light2_on = True
            self.send("Fackel 2 ist an.")
            self.atlight2.append(player)
            self.lighter_blocked = True
            if player.character == "Rinua die Flinke":
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(5)
            self.atlight2.remove(player)
            self.lighter_blocked = False
        else:
            self.send("Welche Fackel willst du anzünden? 1 oder 2?")

    async def turnLightOff(self, player, command, content):
        if content == "1":
            if player in self.atlight2:
                self.send("Du bist noch auf dem Weg zur anderen Fackel.")
                return
            self.light1_on = False
            self.send("Fackel 1 ist aus.")
            self.atlight1.append(player)
            if player.character == "Rinua die Flinke":
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(5)
            self.atlight1.remove(player)
        elif content == "2":
            if player in self.atlight1:
                self.send("Du bist noch auf dem Weg zur anderen Fackel.")
                return
            self.light2_on = False
            self.send("Fackel 2 ist aus.")
            self.atlight2.append(player)
            if player.character == "Rinua die Flinke":
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(5)
            self.atlight2.remove(player)
        else:
            self.send("Welche Fackel willst du löschen? 1 oder 2?")

    async def followIris(self, player, command, content):
        if player.character != "Birol der gigantische Wächter":
            self.send("Du solltest besser hier bleiben, denn du wirst gebraucht.")
        elif "Playmobilmännchen" not in player.inventory:
            self.send("Ohne seinen treuen Begleiter geht Birol im Dunkeln nirgendwo hin.")
        else:
            self.birol_follows_iris = True

    async def guideBirol(self, player, command, content):
        if not self.birol_follows_iris:
            self.send("Iris dir folgt niemand.")
        else:
            self.send("Birol folgt dir durch die Dunkelheit")
            await asyncio.sleep(5)
            self.birol_in_position = True
            self.send("Birol steht jetzt vor dem Loch.")

    async def takePicture(self, player, comamnd, content):
        if player.character != "Sheying der Fotograf":
            self.send("Es gibt jemand besseren für diesen Job.")
            return
        if "Fotoapparat" not in player.inventory:
            self.send("Dir fehlt noch etwas entscheidendes zum Foto machen.")
            return
        if self.light1_on and self.light2_on:
            if self.can_photo:
                self.photo_shot = True
            else:
                self.send("Auf dem Foto ist Globglogabgalab leider nicht zu sehen.")
        else:
            self.send("Bei diesen Lichtverhältnissen wir das nichts mit einem guten Bild.")

    async def resetRoom(self):
        if self.book_position:
            self.items_to_take = ["Buch"]
        self.light1_on = True
        self.light2_on = True
        self.atlight1 = []
        self.atlight2 = []
        self.lighter_blocked = False
        self.birol_in_position = False
        self.book_prepared = False
        self.book_moving = False
        self.pulling_players = []
        self.ropeendings = False
        self.counter = 0
        self.can_photo = False
        self.photo_shot = False
        self.pulling_power = 0
        self.birol_follows_iris = False
        self.book_position = []

    async def rewardPlayers(self):
        self.send("Geschafft! Ihr habt das Bild und könnt endlich aus dieser Höhle verschwinden. Doch noch während "
                  "ihr überlegt wie ihr eigentlich aus der Höhle kommen wollt, hört ihr eine fremde Stimme:"
                  "“I am  impressed by you fellow mortals! No one ever managed to trick me like that, not to mention "
                  "taking a picture of me. You have redeemed yourself and as a reward I shall allow you to leave "
                  "my cave with your little piece of approval. I will make sure for myself no one ever makes it "
                  "this far again! Geschafft! Tatsächlich öffnet sich die große Spinnentür und ihr kommt aus der Höhle"
                  " raus. Auf dem Rückweg findet ihr auch wieder Prof. Firnossepor Athro Pilazanigisiti, auf einem"
                  " Stein sitzend vor der Höhle. Na da habt ihr ja einiges zu berichten…!")
