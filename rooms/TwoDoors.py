from Room import Room
from .PrivateRoom import PrivateRoom
import logging


class TwoDoors(Room):
    def __init__(self, game):
        super().__init__("Zwei Türen", game)
        self.game = game

        # variables
        self.unfilledroom = False
        self.duo_counter = 0
        self.duos = {}
        self.locksopened = [0, 0, 0, 0]

        # flags
        self.allflags = [":flag_cu:", ":flag_mz:", ":flag_ss:", ":flag_jo:", ":flag_gy:", ":flag_ps:", ":flag_st:"]
        self.flagstarts = [0, 0, 0, 0]
        self.currentflags = [{"up": ":flag_cu:", "left": ":flag_mz:", "down": ":flag_ss:", "right": ":flag_jo:"},
                             {"up": ":flag_cu:", "left": ":flag_mz:", "down": ":flag_ss:", "right": ":flag_jo:"},
                             {"up": ":flag_cu:", "left": ":flag_mz:", "down": ":flag_ss:", "right": ":flag_jo:"},
                             {"up": ":flag_cu:", "left": ":flag_mz:", "down": ":flag_ss:", "right": ":flag_jo:"}]

        # boards
        self.gameboard = {}
        self.infoboard = {}
        # create coordinates
        for y in range(10):
            for x in range(10):
                # brown border
                if x in [0, 9] or y in [0, 9]:
                    self.gameboard[(x, y)] = ":brown_square:"
                    self.infoboard[(x, y)] = ":brown_square:"
                # fill up board
                else:
                    self.gameboard[(x, y)] = ":black_large_square:"
                    self.infoboard[(x, y)] = ":skull:"
        # TODO: place locks and key
        # TODO: place color dots, checks and flags

        self.infoboards = []
        self.gameboards = []

        # register commands

    # privat methods

    async def _makeStringfromDict_(self, boarddict):
        string = ""
        for y in range(10):
            for x in range(10):
                string += boarddict[(x, y)]
                string += "."
            string.strip(".")
            string += "\n"
        return string

    async def _placeNewFlags_(self, duo_nr):
        flagstart = self.flagstarts[duo_nr]
        flagstart += 3
        top = self.allflags[flagstart]
        left = self.allflags[flagstart + 1]
        down = self.allflags[flagstart + 2]
        right = self.allflags[flagstart + 3]

    # global methods

    async def enter(self, player):
        await super().enter(player)
        if self.unfilledroom:
            # Spieler 2 zu Voicechannel hinzufügen
            await self.game.show_room(self.unfilledroom, player, False, True)
            # privaten Raum kofigurieren Spieler 2
            private = PrivateRoom(self, " 2")
            self.infoboards.append(self.infoboard.copy())
            message = await self._makeStringfromDict_(self.infoboards[self.duo_counter])
            self.duo_counter += 1
        else:
            # Voicechannel für Spieler 1 und 2 erstellen
            self.unfilledroom = PrivateRoom(self, " Voice")
            await self.unfilledroom.setup()
            # Spieler 1 zu Voicechannel hinzufügen
            await self.game.show_room(self.unfilledroom, player, False, True)
            # privaten Raum kofigurieren Spieler 1
            private = PrivateRoom(self, " 1")
            self.gameboards.append(self.infoboard.copy())
            message = await self._makeStringfromDict_(self.gameboards[self.duo_counter])
        # privaten Raum erstellen
        await private.setup()
        textchannel = self.game.room_to_textchannel(private)
        await textchannel.set_permissions(self.game.roleRegistered, send_messages=False)
        await private.enter(player)
        await self.game.show_room(private, player, True, False)
        await player.currentRoom.send(message)

    async def moveKey(self, direction):
        pass

    async def openLock(self, emoji):
        pass
