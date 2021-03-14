from Room import Room
from .PrivateRoom import PrivateRoom
import logging
import random


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
        self.currentflags = [{":flag_cu:": "up", ":flag_mz:": "left", ":flag_ss:": "down", ":flag_jo:": "right"},
                             {":flag_cu:": "up", ":flag_mz:": "left", ":flag_ss:": "down", ":flag_jo:": "right"},
                             {":flag_cu:": "up", ":flag_mz:": "left", ":flag_ss:": "down", ":flag_jo:": "right"},
                             {":flag_cu:": "up", ":flag_mz:": "left", ":flag_ss:": "down", ":flag_jo:": "right"}]

        # colors
        self.colors = {":red_circle:", ":blue_circle:", ":green_circle:", ":yellow_circle:",
                       ":orange_circle:", ":purple_circle:", "white_check_mark"}

        self.colorspots = {1 : [(2, 1), (3, 2), (6, 3), (7, 6), (1, 7), (5, 8)],
                           2 : [(4, 2), (8, 2), (2, 4), (5, 5), (1, 8), (3, 8), (7, 8)],
                           3 : [(5, 2), (1, 4), (3, 4), (8, 4), (8, 7), (2, 8)],
                           4 : [(6, 1), (1, 2), (8, 3), (4, 4), (1, 6), (4, 8)],
                           5 : [(8, 1), (5, 4), (6, 6), (8, 6), (4, 7)],
                           6 : [(1, 1), (5, 1), (7, 3), (3, 5), (5, 6), (8, 8)],
                           7 : [(3, 1), (7, 1), (6, 4), (1, 5), (3, 6), (6, 8)]}

        self.colororder = (":red_circle:", ":blue_circle:", ":green_circle:", ":yellow_circle:",  #TODO
                           ":orange_circle:", ":purple_circle:", "white_check_mark")

        self.colormappings = {1: [":red_circle:", ":red_circle:", ":red_circle:", ":red_circle:"],
                              2: [":blue_circle:", ":blue_circle:", ":blue_circle:", ":blue_circle:"],
                              3: [":green_circle:", ":green_circle:", ":green_circle:", ":green_circle:"],
                              4: [":yellow_circle:", ":yellow_circle:", ":yellow_circle:", ":yellow_circle:"],
                              5: [":orange_circle:", ":orange_circle:", ":orange_circle:", ":orange_circle:"],
                              6: [":purple_circle:", ":purple_circle:", ":purple_circle:", ":purple_circle:"],
                              7: ["white_check_mark", "white_check_mark", "white_check_mark", "white_check_mark"]}
        # locks mirrored
        self.locks = [(7, 1), (8, 8), (8, 4), (1, 3), (4, 7), (4, 6), (3, 4)]

        # boards preset
        self.gameboard = {}
        self.infoboard = {}
        # create coordinates
        for y in range(10):
            for x in range(10):
                # brown border
                if x in [0, 9] or y in [0, 9]:
                    self.gameboard[(x, 9 - y)] = ":brown_square:"
                    self.infoboard[(x, y)] = ":brown_square:"
                # fill up board
                else:
                    self.gameboard[(x, 9 - y)] = ":black_large_square:"
                    self.infoboard[(x, y)] = ":skull:"

        # list for saving boards
        self.infoboards = []
        self.gameboards = []
        for i in range(4):
            self.infoboards.append(self.infoboard.copy())
            self.gameboards.append(self.gameboard.copy())
            # add locks
            for (x, y) in [(7, 1), (8, 8), (8, 4), (1, 3), (5, 7), (4, 6), (3, 4)]:
                self.gameboards[i][(x, y)] = ":lock:"
            self.gameboards[i][(6, 2)] = ":key:"

        # register commands
        # TODO

    # privat methods

    async def _makeStringfromDict_(self, boarddict):
        string = ""
        for y in range(10):
            for x in range(10):
                string += boarddict[(x, y)]
                string += "."
            string = string[:-1]
            string += "\n"
        return string

    async def _placeNewFlags_(self, duo_nr):
        # change flagnumbers
        self.flagstarts[duo_nr] += 3
        self.flagstarts[duo_nr] %= 7
        flagstart = self.flagstarts[duo_nr]
        # get flag-emojis from list
        top = self.allflags[flagstart]
        left = self.allflags[flagstart + 1]
        down = self.allflags[flagstart + 2]
        right = self.allflags[flagstart + 3]
        # update infoboard
        self.infoboards[duo_nr][(4, 0)] = top
        self.infoboards[duo_nr][(5, 0)] = top
        self.infoboards[duo_nr][(0, 4)] = left
        self.infoboards[duo_nr][(0, 5)] = left
        self.infoboards[duo_nr][(4, 9)] = down
        self.infoboards[duo_nr][(5, 9)] = down
        self.infoboards[duo_nr][(9, 4)] = right
        self.infoboards[duo_nr][(9, 5)] = right
        # save new flags as current
        self.currentflags[duo_nr]["top"] = top
        self.currentflags[duo_nr]["left"] = left
        self.currentflags[duo_nr]["down"] = down
        self.currentflags[duo_nr]["right"] = right

    async def _changeColors_(self, duo_nr):
        pass  #TODO
    # global methods

    async def enter(self, player):
        self.lock.acquire()
        if self.unfilledroom:
            # Spieler 2 zu Voicechannel hinzufügen
            await self.game.show_room(self.unfilledroom, player, False, True)
            # privaten Raum kofigurieren Spieler 2
            private = PrivateRoom(self, " 2")
            await self._placeNewFlags_(self.duo_counter)
            await self._changeColors_(self.duo_counter)
            message = await self._makeStringfromDict_(self.infoboards[self.duo_counter])
            self.duos[player] = self.duo_counter
            self.duo_counter += 1
        else:
            # Voicechannel für Spieler 1 und 2 erstellen
            self.unfilledroom = PrivateRoom(self, " Voice")
            await self.unfilledroom.setup()
            # Spieler 1 zu Voicechannel hinzufügen
            await self.game.show_room(self.unfilledroom, player, False, True)
            # privaten Raum kofigurieren Spieler 1
            private = PrivateRoom(self, " 1")
            message = await self._makeStringfromDict_(self.gameboards[self.duo_counter])
            self.duos[player] = self.duo_counter
        # privaten Raum erstellen
        await private.setup()
        textchannel = self.game.room_to_textchannel(private)
        await textchannel.set_permissions(self.game.roleRegistered, send_messages=False)
        await private.enter(player)
        await self.game.show_room(private, player, text=True, voice=False)
        player.currentRoom.send(message)
        self.players.append(player)
        self.lock.release()
        return

    async def moveKey(self, direction):
        pass  #TODO links und rechts vertauscht bewegen

    async def openLock(self, emoji):
        pass  #TODO
