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

entrymessage1 = ("Alle Drehscheiben zeigen die Spinne, du schaust in die Runde - suchend nach einer Reaktion, schaust "
                 "zum Tor, ob es sich bewegt, als plötzlich: Ein lautes Krachen, 8 Falltüren öffnen sich unter den "
                 "Knöpfen. Alles geht viel zu schnell als das jemand reagieren könnte. Der freie Fall scheint dir ewig "
                 "und nimmt dir die Luft zum atmen oder irgendeinen Ton von dir zu geben. Alles ist Stockdunkel, aber "
                 "du spürst, dass du wieder Kontakt zu einem Untergrund hast. Gebremst bist du aber kaum und wirst nun "
                 "links und rechts geschleudert - in einer Art Tunnelsystem verlierst du das letzte bisschen was du "
                 "noch an Orientierung nach dem Labyrinth übrig hattest. Das einzige was du noch wahrnimmst sind die "
                 "Schreie deiner Mit-Abenteurer:innen, die scheinbar nicht weit von dir sind. \n"
                 "Als du am Ende des Tunnels rauskommst, findest du dich etwas benommen in einem Kerkerartigen Raum "
                 "wieder. Alleine. Schwache Beleuchtung, gegenüber von dir etwas, das aussieht wie eine Tür und eine "
                 "Einbuchtung in der Wand links von dir. \n"
                 "Grade als du dich wieder sortiert hattest, fliegt dir noch "
                 "etwas hinterher an den Kopf. Schon wieder schummrig vom Schlag, schaust du was dir denn diese "
                 "Überraschung beschert hat: Ein {item}! Das muss sich wohl in der Achterbahnfahrt von deinem Gürtel "
                 "gelöst haben. Du steckst es sicherheitshalber mal ein. \n")
entrymessage2 = ("Du widmest dich zuerst der Tür, kannst aber wenig ausrichten gegen eine 2m hohe Steinwand. Drücken,"
                 "ziehen, dagegen stemmen, schlagen, vor Verzweiflung an der Tür herabsinken und weinen - Es hilft"
                 "alles nichts, die Tür bewegt sich keinen Millimeter. Bleibt noch die unscheinbare Ausbuchtung an der"
                 "Wand links. Die bei genauerer Betrachtung gar nicht so unscheinbar ist"
                 "(Captain Obvious to the rescue): Man kann eine kleine Vertiefung erkennen, wie bei deiner" 
                 "Fernbedienung zuhause, wo du jetzt so gerne wärst, wo die Batterien sind. Mit ein bisschen Gewalt" 
                 "bekommst du den Mechanismus auf und es tut sich ein Gitter und ein Text auf: \n"          
                 "Um zu Lösen das Rätsel, \n"
                 "Unterteile das Gitter an den Linien, aber mach’ keine Brezel! \n" 
                 "Nur Rechtecke und Quadrate sind erlaubt, \n"
                 "Nichtmal überschneiden dürfen sie sich, sonst ist alles versaut! \n"
                 "Einfacher wird’s nicht: Jedes Viereck  \n"
                 "möge enthalten genau die Anzahl an Zellen, was ein Dreck, \n" 
                 "die die Ziffer vorgibt innerhalb der Grenze. \n"  
                 "Mit !pin kannst du aufschließen das Schloss \n"  
                 "und die Farbfelder von oben nach unten als Zahlencode, du Boss! \n")
result = 128639


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
        private.send(entrymessage1.format(item=player.inventory[0]))
        private.send(entrymessage2)
        with open("resources/keyroom_colored_new.png", "rb") as keyimage:
            private.send(discord.File(keyimage))   # funktioniert nur beim ersten Spieler der dem Raum betritt

    @Room.requires_mod
    async def skip(self, player, command, content):
        nextroom = self.game.get_room("Zwei Türen")
        for player in list(self.get_players()):
            await self.leave(player)
            await nextroom.enter(player)
        self.game.set_current_room(nextroom)

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
            player.currentRoom.send("Das Schiebefenster öffnet sich.")
            nextroom = self.game.get_room("Zwei Türen")
            await asyncio.sleep(5)
            await self.leave(player)
            await nextroom.enter(player)
            if len(self.players) == 0:
                self.game.set_current_room(nextroom)
        else:
            player.currentRoom.send("Dies ist leider nicht das richtige Ergebnis."
                                    "Versuche es in einer Minute noch einmal.")
