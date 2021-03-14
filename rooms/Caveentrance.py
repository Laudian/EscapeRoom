from Room import Room
import logging

class Caveentrance(Room):
    def __init__(self, game):
        super().__init__("Höhleneingang", game)
        self.game = game
        # variables
        self.torches = {0: 2, 1: 0, 2: 0, 3: 2,
                        4: 0, 5: 0, 6: 2, 7: 0}
        self.buttons = {0: [0, 1, 2, 3, 4], 1: [0, 1, 2, 3, 5], 2: [0, 1, 2, 3, 6], 3: [0, 1, 2, 3, 7],
                        4: [4, 5, 6, 7, 0], 5: [4, 5, 6, 7, 1], 6: [4, 5, 6, 7, 2], 7: [4, 5, 6, 7, 3]}
        self.empty = True
        # register commands
        self.register_command("button", self.pushButton, "Eigenen Knopf drücken - Höhleneingang")
        self.register_command("skiproom", self.skipRoom, "Raum überspringen")

    async def printTorches(self):
        message = ""
        for x in range(8):
            if self.torches[x] == 0:
                message += ":menorah:"
            elif self.torches[x] == 1:
                message += ":gemini:"
            else:
                message += ":libra:"
            if x % 4 == 3:
                message += "\n"
        self.send(message)

    async def enter(self, player):
        await super().enter(player)
        if self.empty:
            self.empty = False
            await self.printTorches()
        await self.game.show_room(self, player, True, True)

    async def pushButton(self, player, command, content):
        if content:
            await self.pushAnyButton(player, command, content)
        else:
            button_number = self.players.index(player)
            changing_torches = self.buttons[button_number]
            for torch in changing_torches:
                self.torches[torch] += 1
                self.torches[torch] %= 3
            if 1 not in self.torches.values() and 0 not in self.torches.values():
                await self.printTorches()
                await self.rewardPlayers()
            else:
                await self.printTorches()

    @Room.requires_mod
    async def pushAnyButton(self, player, command, content):
        button_number = int(content) + 1
        changing_torches = self.buttons[button_number]
        for torch in changing_torches:
            self.torches[torch] += 1
            self.torches[torch] %= 3
        if 1 not in self.torches.values() and 0 not in self.torches.values():
            await self.printTorches()
            await self.rewardPlayers()
        else:
            await self.printTorches()

    @Room.requires_admin
    async def skipRoom(self, player, command, content):
        await self.rewardPlayers()

    async def rewardPlayers(self):
        self.send("Nachricht am Ende des Raumes")  #TODO
        for player in list(self.get_players()):
            await self.leave(player)
            nextroom = self.game.get_room("Zwei Türen")
            await nextroom.enter(player)
