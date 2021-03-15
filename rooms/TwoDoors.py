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
        self.allflags = ["🇨🇺", "🇲🇿", "🇸🇸", "🇯🇴", "🇬🇾", "🇵🇸", "🇸🇹"]
        self.flagstarts = [0, 0, 0, 0]
        self.currentflags = [{"🇨🇺": "up", "🇲🇿": "left", "🇸🇸": "down", "🇯🇴": "right"},
                             {"🇨🇺": "up", "🇲🇿": "left", "🇸🇸": "down", "🇯🇴": "right"},
                             {"🇨🇺": "up", "🇲🇿": "left", "🇸🇸": "down", "🇯🇴": "right"},
                             {"🇨🇺": "up", "🇲🇿": "left", "🇸🇸": "down", "🇯🇴": "right"}]
        # left and right switched because of mirrored gameboard
        self.directions = {"up": (0, -1), "left": (1, 0), "down": (0, 1), "right": (-1, 0)}

        # colors
        self.colors = [":red_circle:", ":blue_circle:", ":green_circle:", ":yellow_circle:",
                       ":orange_circle:", ":purple_circle:", ":brown_circle:"]

        self.colorspots = {0 : [(2, 1), (3, 2), (6, 3), (7, 6), (1, 7), (5, 8)],
                           1 : [(4, 2), (8, 2), (5, 5), (1, 8), (3, 8), (7, 8)],
                           2 : [(5, 2), (1, 4), (3, 4), (8, 4), (8, 7), (2, 8)],
                           3 : [(6, 1), (1, 2), (8, 3), (4, 4), (1, 6), (4, 8)],
                           4 : [(8, 1), (2, 4), (5, 4), (6, 6), (8, 6), (4, 7)],
                           5 : [(1, 1), (5, 1), (7, 3), (3, 5), (5, 6), (8, 8)],
                           6 : [(3, 1), (7, 1), (6, 4), (1, 5), (3, 6), (6, 8)]}

        self.colororder = (":red_circle:", ":blue_circle:", ":green_circle:", ":yellow_circle:",  #TODO
                           ":orange_circle:", ":purple_circle:", ":brown_circle:")

        self.colormappings = {0: [":red_circle:", ":red_circle:", ":red_circle:", ":red_circle:"],
                              1: [":blue_circle:", ":blue_circle:", ":blue_circle:", ":blue_circle:"],
                              2: [":green_circle:", ":green_circle:", ":green_circle:", ":green_circle:"],
                              3: [":yellow_circle:", ":yellow_circle:", ":yellow_circle:", ":yellow_circle:"],
                              4: [":orange_circle:", ":orange_circle:", ":orange_circle:", ":orange_circle:"],
                              5: [":purple_circle:", ":purple_circle:", ":purple_circle:", ":purple_circle:"],
                              6: [":brown_circle:", ":brown_circle:", ":brown_circle:", ":brown_circle:"]}
        # locks mirrored
        self.locks = {(7, 1): 0, (8, 8): 1, (8, 4): 2, (1, 3): 3, (5, 7): 4, (4, 6): 5, (3, 4): 6}

        # key
        self.key_positions = [(6, 2), (6, 2), (6, 2), (6, 2)]
        self.behind_key = [":black_circle:", ":black_circle:", ":black_circle:", ":black_circle:"]

        # boards preset
        self.gameboard = {}
        self.infoboard = {}
        # create coordinates
        for y in range(10):
            for x in range(10):
                # brown border
                if x in [0, 9] or y in [0, 9]:
                    self.gameboard[(x, 9 - y)] = ":white_square_button:"
                    self.infoboard[(x, y)] = ":white_square_button:"
                # fill up board
                else:
                    self.gameboard[(x, 9 - y)] = ":black_circle:"
                    self.infoboard[(x, y)] = ":skull:"

        # list for saving boards
        self.infoboards = []
        self.gameboards = []
        for i in range(4):
            self.infoboards.append(self.infoboard.copy())
            self.gameboards.append(self.gameboard.copy())
            # add locks
            for (x, y) in self.locks.keys():
                self.gameboards[i][(x, y)] = ":lock:"
            self.gameboards[i][self.key_positions[i]] = ":key:"

        # unlock tries
        self.unlock_tries = [0, 0, 0, 0]

        # textpanels
        self.infotext = ["Hmm...", "Hmm...", "Hmm...", "Hmm..."]
        self.gametext = ["Hmm...", "Hmm...", "Hmm...", "Hmm..."]

        # register commands
        self.register_command("move", self.moveKey, "bewegt etwas jenachdem was hinter !move steht")
        self.register_command("unlock", self.openLock, "öffnet das Schloss wenn die Farbe passt")

    # privat methods

    async def _createMessage_(self, duo_nr, board):
        if board == "info":
            boarddict = self.infoboards[duo_nr]
            string = self.infotext[duo_nr]
        else:
            boarddict = self.gameboards[duo_nr]
            string = self.gametext[duo_nr]
        string += "\n"
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
        flagstart = self.flagstarts[duo_nr]
        # get flag-emojis from list
        up = self.allflags[flagstart % 7]
        left = self.allflags[(flagstart + 1) % 7]
        down = self.allflags[(flagstart + 2) % 7]
        right = self.allflags[(flagstart + 3) % 7]
        # update infoboard
        self.infoboards[duo_nr][(4, 0)] = up
        self.infoboards[duo_nr][(5, 0)] = up
        self.infoboards[duo_nr][(0, 4)] = left
        self.infoboards[duo_nr][(0, 5)] = left
        self.infoboards[duo_nr][(4, 9)] = down
        self.infoboards[duo_nr][(5, 9)] = down
        self.infoboards[duo_nr][(9, 4)] = right
        self.infoboards[duo_nr][(9, 5)] = right
        # save new flags as current
        self.currentflags[duo_nr][up] = "up"
        self.currentflags[duo_nr][left] = "left"
        self.currentflags[duo_nr][down] = "down"
        self.currentflags[duo_nr][right] = "right"

    async def _changeColors_(self, duo_nr):
        # shuffle colors
        all_colors = self.colors.copy()
        random.shuffle(all_colors)
        # save new color mapping
        for i in range(7):
            self.colormappings[i][duo_nr] = all_colors[i]
        # change infoboard
        for color_nr, spots in self.colorspots.items():
            color = self.colormappings[color_nr][duo_nr]
            for spot in spots:
                self.infoboards[duo_nr][spot] = color

    async def _updateBoards_(self, duo_nr, gameplayer):
        message_game = await self._createMessage_(duo_nr, "game")
        message_info = await self._createMessage_(duo_nr, "info")
        gameplayer.currentRoom.send(message_game)
        infoplayer = self.duos[duo_nr]
        infoplayer.currentRoom.send(message_info)

    # global methods

    async def enter(self, player):
        self.lock.acquire()
        if self.unfilledroom:
            # Spieler 2 zu Voicechannel hinzufügen
            await self.game.show_room(self.unfilledroom, player, text=False, voice=True)
            # privaten Raum kofigurieren Spieler 2
            private = PrivateRoom(self, " 2")
            await self._placeNewFlags_(self.duo_counter)
            await self._changeColors_(self.duo_counter)
            message = await self._createMessage_(self.duo_counter, "info")
            self.duos[self.duo_counter] = player
            self.duo_counter += 1
        else:
            # Voicechannel für Spieler 1 und 2 erstellen
            self.unfilledroom = PrivateRoom(self, " Voice")
            await self.unfilledroom.setup()
            # Spieler 1 zu Voicechannel hinzufügen
            await self.game.show_room(self.unfilledroom, player, text=False, voice=True)
            # privaten Raum kofigurieren Spieler 1
            private = PrivateRoom(self, " 1")
            message = await self._createMessage_(self.duo_counter, "game")
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

    async def moveKey(self, player, command, content):
        # collect needed infos
        flag = content
        duo_nr = self.duos[player]
        direction = self.currentflags[duo_nr][flag]
        change = self.directions[direction]
        old_key_position = self.key_positions[duo_nr]
        new_key_position = (change[0] + old_key_position[0], change[1] + old_key_position[1])
        new_key_position_infoboard = (9 - new_key_position[0], new_key_position[1])
        # check if move allowed
        if 0 in new_key_position or 9 in new_key_position:
            self.gametext[duo_nr] = "Ist der Rand nicht eindeutig genug?"
            self.infotext[duo_nr] = "Versuche: " + str(self.unlock_tries[duo_nr])
        elif self.infoboards[duo_nr][new_key_position_infoboard] == ":skull:":
            # reset key to start on gameboard
            self.gametext[duo_nr] = "Wer hat's versaut? Du oder dein Gegenüber?"
            self.gameboards[duo_nr][old_key_position] = self.behind_key[duo_nr]
            self.behind_key[duo_nr] = ":black_circle:"
            self.key_positions[duo_nr] = (6, 2)
            self.gameboards[duo_nr][(6, 2)] = ":key:"
            # change flags on infoboard
            self.infotext[duo_nr] = "Wer hat's versaut? Du oder dein Gegenüber?"
            await self._placeNewFlags_(duo_nr)
        # set new emojis for valid move
        else:
            self.gameboards[duo_nr][old_key_position] = self.behind_key[duo_nr]
            self.behind_key[duo_nr] = self.gameboards[duo_nr][new_key_position]
            self.key_positions[duo_nr] = new_key_position
            if self.behind_key[duo_nr] == ":black_circle:":
                self.gameboards[duo_nr][new_key_position] = ":key:"
            else:
                self.gameboards[duo_nr][new_key_position] = ":closed_lock_with_key:"
            self.gametext[duo_nr] = "Hmm..."
            self.infotext[duo_nr] = "Versuche: " + str(self.unlock_tries[duo_nr])
        # send updated boards
        await self._updateBoards_(duo_nr, player)

    async def openLock(self, player, command, content):
        duo_nr = self.duos[player]
        key_color = content
        lock_position = self.key_positions[duo_nr]
        lock_number = self.locks[lock_position]
        lock_color = self.colormappings[lock_number][duo_nr]
        # key on field with closed lock
        if self.behind_key == ":lock:":
            # key matches lock
            if key_color == lock_color:
                # correct lock order
                if lock_number == self.locksopened[duo_nr]:
                    self.locksopened[duo_nr] += 1
                    self.gametext[duo_nr] = "Passt perfekt!"
                    self.infotext[duo_nr] = "Schloss " + str(self.locksopened[duo_nr]) + "/7 geöffnet. Versuche: 2"
                    self.behind_key[duo_nr] = ":unlock:"
                    # last lock opened
                    if self.locksopened[duo_nr] == 7:
                        await self.rewardPlayers(player)
                # wrong lock order
                else:
                    self.unlock_tries[duo_nr] -= 1
                    self.gametext[duo_nr] = "Da passt irgendwas nicht."
                    # restart
                    if self.unlock_tries[duo_nr] == 0:
                        # reset locks
                        self.unlock_tries[duo_nr] = 2
                        self.locksopened[duo_nr] = 0
                        for (x, y) in self.locks.keys():
                            self.gameboards[duo_nr][(x, y)] = ":lock:"
                        self.infotext[duo_nr] = "Alle Schlösser zurückgesetzt. Das war ein Fehler zu viel"
                        # reset key
                        self.behind_key[duo_nr] = ":black_circle:"
                        self.key_positions[duo_nr] = (6, 2)
                        self.gameboards[duo_nr][(6, 2)] = ":key:"
                    # 1 try left
                    else:
                        self.infotext[duo_nr] = "Falsche Schlossreihenfolge. Versuche: " + str(self.unlock_tries[duo_nr])
            # key doesnt match lock
            else:
                self.unlock_tries[duo_nr] -= 1
                self.gametext[duo_nr] = "Da passt irgendwas nicht."
                # restart
                if self.unlock_tries[duo_nr] == 0:
                    # reset locks
                    self.unlock_tries[duo_nr] = 2
                    self.locksopened[duo_nr] = 0
                    for (x, y) in self.locks.keys():
                        self.gameboards[duo_nr][(x, y)] = ":lock:"
                    self.infotext[duo_nr] = "Tür zurückgesetzt. Das war ein Fehler zu viel"
                    # reset key
                    self.behind_key[duo_nr] = ":black_circle:"
                    self.key_positions[duo_nr] = (6, 2)
                    self.gameboards[duo_nr][(6, 2)] = ":key:"
                # 1 try left
                else:
                    self.infotext[duo_nr] = "Falsche Schlüsselfarbe. Versuche: " + str(self.unlock_tries[duo_nr])
        # key on field with open lock
        elif self.behind_key == ":open_lock:":
            self.gametext[duo_nr] = "Dieses Schloss ist schon offen"
            self.infotext[duo_nr] = "Versuche: " + str(self.unlock_tries[duo_nr])
        # key on field without lock
        else:
            self.gametext[duo_nr] = "Du weißt schon, dass hier kein Schloss ist?"
            self.infotext[duo_nr] = "Versuche: " + str(self.unlock_tries[duo_nr])
        await self._updateBoards_(duo_nr, player)

    async def rewardPlayers(self, player):
        self.send("Nachricht am Ende des Raumes")  #TODO
        for player in list(self.get_players()):
            await self.leave(player)
            nextroom = self.game.get_room("Eingangshalle")
            await nextroom.enter(player)