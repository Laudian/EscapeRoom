from Room import Room
import logging


class Caveentrance(Room):
    def __init__(self, game):
        super().__init__("Höhleneingang", game)
        # variables
        self.torches = {0: False, 1: False, 2: False, 3: False,
                        4: False, 5: False, 6: False, 7: False}
        self.buttons = {0: [0, 1, 2, 3, 4], 1: [0, 1, 2, 3, 5], 2: [0, 1, 2, 3, 6], 3: [0, 1, 2, 3, 7],
                        4: [4, 5, 6, 7, 0], 5: [4, 5, 6, 7, 1], 6: [4, 5, 6, 7, 2], 7: [4, 5, 6, 7, 3]}

        # register commands
        self.register_command("button", self.pushButton, "Eigenen Knopf drücken - Höhleneingang")

    async def printTorches(self):
        message = ""
        for x in range(8):
            if self.torches[x]:
                message += "O"
            else:
                message += "X"
            if x % 4 == 3:
                message += "\n"
        self.send(message)

    async def enter(self, player):
        await super().enter(player)
        if len(self.players) == 8:
            await self.printTorches()
        else:
            self.send("Warte auf weitere Spieler")

    async def pushButton(self, player, command, content):
        button_number = self.players.index(player)
        changing_torches = self.buttons[button_number]
        for torch in changing_torches:
            self.torches[torch] = not self.torches[torch]
        if (True in self.torches.values()) != (False in self.torches.values()):
            await self.printTorches()
            await self.rewardPlayers()
        else:
            await self.printTorches()

    async def rewardPlayers(self):
        self.send("Nachricht am Ende des Raumes")  #TODO
        nextroom = self.game.get_room("Eingangshalle")
        for player in self.players:
            await self.leave(player)
            await nextroom.enter(player)
