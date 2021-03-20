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
        self.voice_channels = {}
        self.reset_voice = False
        self.startmessage = (
                            "Durch das nun offene Schiebefenster kannst du deinen Gegenüber hören! Endlich mal ein "
                            "Erfolg! Und es tut sich noch mehr:\n Es flammen nun auch die restlichen Fackeln auf und "
                            "du fra**g**st dich so langsam auf was du dich hier eingelassen hast. Die Geschehnisse "
                            "wandeln sich hier so langsam vom wunde**r**samen zum a**b**surden und unwirklichen. "
                            "Außerdem ist neben dem kleinen Fenster ein riesiges Bedienfeld erschienen. Du kannst sogar"
                            " wenn du drauf schaust, Umrisse deines Gegenüber ausmachen. Es erinnert schon fast an "
                            "einen alten Arcade Automaten. Fehlt nur noch der Jo**y**stick und los gehts. Es erinnert "
                            "dich an die guten alten Zeiten, wie du mit deinen Freunden in die Arcadehalle gefahren "
                            "bist um Wreck-it-Ralph, Turb**o**, Super Mario oder Space Invaders zu spielen. Nur leider "
                            "macht das hier nicht ganz so viel S**p**aß. Du sitzt in einem Kerker tief "
                            "in einer Höhle und hast noch keinen blassen Schimmer wie du hier wieder rauskommen willst."
                             )
        # flags
        self.allflags = ["🇨🇺", "🇲🇿", "🇸🇸", "🇯🇴", "🇬🇾", "🇵🇸", "🇸🇹"]
        self.flagstarts = [0, 0, 0, 0]
        self.currentflags = [{}, {}, {}, {}]

        # left and right switched because of mirrored gameboard
        self.directions = {"up": (0, -1), "left": (1, 0), "down": (0, 1), "right": (-1, 0)}

        # colors
        self.colors = ["🔴", "🟣", "🔵",    # rot, lila, blau
                       "🟢", "🟠", "🟡"]  # grün, orange, gelb

        self.colorspots = {0 : [(8, 2), (2, 1), (3, 2), (6, 3), (7, 6), (1, 7), (5, 8)],
                           1 : [(5, 5), (5, 2), (1, 4), (3, 4), (8, 4), (8, 7), (2, 8)],
                           2 : [(7, 8), (6, 1), (1, 2), (8, 3), (4, 4), (1, 6), (4, 8)],
                           3 : [(4, 2), (8, 1), (2, 4), (5, 4), (6, 6), (8, 6), (4, 7)],
                           4 : [(3, 8), (1, 1), (5, 1), (7, 3), (3, 5), (5, 6), (8, 8)],
                           5 : [(1, 8), (3, 1), (7, 1), (6, 4), (1, 5), (3, 6), (6, 8)]}

        self.colororder = ("🟢", "🔴", "🔵",    # grün, rot, blau
                           "🟡", "🟠", "🟣")  # gelb, orange, lila

        self.colormappings = {0: ["", "", "", ""],
                              1: ["", "", "", ""],
                              2: ["", "", "", ""],
                              3: ["", "", "", ""],
                              4: ["", "", "", ""],
                              5: ["", "", "", ""]}
        # locks mirrored
        self.locks = {(7, 1): 0, (8, 4): 1, (1, 3): 2, (5, 7): 3, (4, 6): 4, (3, 4): 5}
        self.locksopened = [0, 0, 0, 0]

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
            # add locks and the key
            for (x, y) in self.locks.keys():
                self.gameboards[i][(x, y)] = ":lock:"
            self.gameboards[i][self.key_positions[i]] = ":key:"

        # textpanels
        self.infotext = ["Hmm...",
                         "Hmm...",
                         "Hmm...",
                         "Hmm..."]

        self.gametext = ["Um auf einen der Knöpfe zu drücken reagiere mit dem entsprechenend Emoji",
                         "Um auf einen der Knöpfe zu drücken reagiere mit dem entsprechenend Emoji",
                         "Um auf einen der Knöpfe zu drücken reagiere mit dem entsprechenend Emoji",
                         "Um auf einen der Knöpfe zu drücken reagiere mit dem entsprechenend Emoji"]

        # register commands
        self.register_command("move", self.moveKey, "bewegt etwas jenachdem was hinter !move steht")
        self.register_command("unlock", self.openLock, "öffnet das Schloss wenn die Farbe passt")
        self.register_command("skip", self.skip, "Raum überspringen")
        self.register_command("reaction", self.handleButtons, "Knöpfe unter Gameboard drücken")

    # privat methods

    async def _createMessage_(self, duo_nr, board):
        if board == "info":
            boarddict = self.infoboards[duo_nr]
            string = self.infotext[duo_nr]
            buttons = ""
        else:
            boarddict = self.gameboards[duo_nr]
            string = self.gametext[duo_nr]
            buttons = "\n🇨🇺     🇲🇿     🇸🇸     🇯🇴     🇬🇾     🇵🇸     🇸🇹" \
                      "\n🔴       🟣       🔵       🟢       🟡       🟠"
        string += "\n"
        for y in range(10):
            for x in range(10):
                string += boarddict[(x, y)]
                string += "."
            string = string[:-1]
            string += "\n"
        string += buttons
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
        for i in range(6):
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
            # privaten Raum kofigurieren Spieler 2
            private = PrivateRoom(self, " " + player.name)
            await self._placeNewFlags_(self.duo_counter)
            await self._changeColors_(self.duo_counter)
            boardmessage = await self._createMessage_(self.duo_counter, "info")
            self.duos[self.duo_counter] = player
            self.duo_counter += 1
            self.reset_voice = True
        else:
            # Voicechannel für Spieler 1 und 2 erstellen
            self.unfilledroom = PrivateRoom(self, " Voice")
            await self.unfilledroom.setup()
            # privaten Raum kofigurieren Spieler 1
            private = PrivateRoom(self, " " + player.name)
            boardmessage = await self._createMessage_(self.duo_counter, "game")
            self.duos[player] = self.duo_counter
        # Spieler zu Voicechannel hinzufügen
        await self.game.show_room(self.unfilledroom, player, text=False, voice=True)
        self.voice_channels[player] = self.unfilledroom
        # voicechannel zurücksetzen
        if self.reset_voice:
            self.reset_voice = False
            self.unfilledroom = False
        # privaten Raum erstellen
        await private.setup()
        await private.enter(player)
        await self.game.show_room(private, player, text=True, voice=False, write=False)
        player.currentRoom.send(self.startmessage)
        player.currentRoom.send(boardmessage)
        self.players.append(player)
        self.lock.release()
        return

    async def handleButtons(self, player, command, content):
        if content["emoji"] in self.allflags:
            await self.moveKey(player, command, content["emoji"])
        elif content["emoji"] in self.colors:
            await self.openLock(player, command, content["emoji"])
        else:
            duo_nr = self.duos[player]
            self.gametext[duo_nr] = "Um auf einen der Knöpfe zu drücken reagiere mit dem entsprechenend Emoji."
            self.infotext[duo_nr] = "Diesen Knopf gibt es nicht."

    async def moveKey(self, player, command, content):
        # collect needed infos
        flag = content
        duo_nr = self.duos[player]
        # check if flag currently active
        if flag in self.currentflags[duo_nr]:
            direction = self.currentflags[duo_nr][flag]
            change = self.directions[direction]
            old_key_position = self.key_positions[duo_nr]
            new_key_position = (change[0] + old_key_position[0], change[1] + old_key_position[1])
            new_key_position_infoboard = (9 - new_key_position[0], new_key_position[1])
            # check if move allowed
            if 0 in new_key_position or 9 in new_key_position:
                self.gametext[duo_nr] = "Ist der Rand nicht eindeutig genug?"
                self.infotext[duo_nr] = "Ist der Rand nicht eindeutig genug?"
            elif self.infoboards[duo_nr][new_key_position_infoboard] == ":skull:":
                # reset key to start on gameboard
                self.gametext[duo_nr] = "Da solltest du besser nicht hin..."
                self.gameboards[duo_nr][old_key_position] = self.behind_key[duo_nr]
                self.behind_key[duo_nr] = ":black_circle:"
                self.key_positions[duo_nr] = (6, 2)
                self.gameboards[duo_nr][(6, 2)] = ":key:"
                # change flags on infoboard
                self.infotext[duo_nr] = "Da solltest du besser nicht hin..."
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
                self.gametext[duo_nr] = "Um auf einen der Knöpfe zu drücken reagiere mit dem entsprechenend Emoji."
                self.infotext[duo_nr] = "Um auf einen der Knöpfe zu drücken reagiere mit dem entsprechenend Emoji."
        else:
            self.gametext[duo_nr] = "Dieser Knopf hat wohl gerade keine Auswirkung..."
        # send updated boards
        await self._updateBoards_(duo_nr, player)

    async def openLock(self, player, command, content):
        done = False
        duo_nr = self.duos[player]
        key_color = str(content)
        # key on field with closed lock
        if self.behind_key[duo_nr] == ":lock:":
            # key matches lock
            lock_position = self.key_positions[duo_nr]
            lock_number = self.locks[lock_position]
            lock_color = self.colormappings[lock_number][duo_nr]
            if key_color == lock_color:
                # correct lock order
                if lock_color == self.colororder[self.locksopened[duo_nr]]:
                    self.locksopened[duo_nr] += 1
                    self.gametext[duo_nr] = "Passt perfekt!"
                    self.infotext[duo_nr] = "Schloss " + str(self.locksopened[duo_nr]) + "/6 geöffnet."
                    self.behind_key[duo_nr] = ":unlock:"
                    # last lock opened
                    if self.locksopened[duo_nr] == 6:
                        done = True
                # wrong lock order
                else:
                    self.gametext[duo_nr] = "Da passt irgendwas nicht."
                    self.infotext[duo_nr] = "Falsche Schlossreihenfolge."
            # key doesnt match lock
            else:
                self.gametext[duo_nr] = "Da passt irgendwas nicht."
                self.infotext[duo_nr] = "Schlüssel passt nicht."
        # key on field with open lock
        elif self.behind_key[duo_nr] == ":open_lock:":
            self.gametext[duo_nr] = "Dieses Schloss ist schon offen"
            self.infotext[duo_nr] = "Dieses Schloss ist schon offen"
        # key on field without lock
        else:
            self.gametext[duo_nr] = "Du weißt schon, dass hier kein Schloss ist?"
            self.infotext[duo_nr] = "Du weißt schon, dass hier kein Schloss ist?"
        await self._updateBoards_(duo_nr, player)
        if done:
            await self.rewardPlayers(player, duo_nr)

    @Room.requires_mod
    async def skip(self, player, command, content):
        for gameplayer, duo_nr in self.duos.items():
            if type(duo_nr) == int:
                await self.rewardPlayers(gameplayer, duo_nr)

    async def leave(self, player):
        await self.game.hide_room(player.currentRoom, player)
        await player.currentRoom.leave(player)
        self.players.remove(player)

    async def rewardPlayers(self, gameplayer, duo_nr):
        infoplayer = self.duos[duo_nr]
        for player in [gameplayer, infoplayer]:
            await self.leave(player)
            await self.game.hide_room(self.voice_channels[player], player)
            nextroom = self.game.get_room("Vier Wände")
            await nextroom.enter(player)
