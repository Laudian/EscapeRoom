from Room import Room
import logging


class Caveentrance(Room):
    def __init__(self, game):
        super().__init__("Höhleneingang", game)
        # variables
        self.torches = {0: False, 1: False, 2: False,
                        3: False, 4: False, 5: False,
                        6: False, 7: False, 8: False}
        self.buttons = {0: [0, 1, 2, 3, 6], 1: [0, 1, 2, 4, 7], 2: [0, 1, 2, 5, 8],
                        3: [3, 4, 5, 0, 6], 4: [3, 4, 5, 1, 7], 5: [3, 4, 5, 2, 8],
                        6: [6, 7, 8, 0, 3], 7: [6, 7, 8, 1, 4], 8: [6, 7, 8, 2, 5]}
        self.player_list = []

        # register commands
        self.register_command("button", self.pushButton, "Eigenen Knopf drücken - Höhleneingang")

    async def printTorches(self, player):
        message = ""
        for x in range(9):
            if self.torches[x]:
                message += ":orange_circle:"
            else:
                message += ":black_circle:"
            if x % 3 == 2:
                message += "\n"
        player.send(message)

    async def enter(self, player):
        self.player_list.append(player)
        if len(self.player_list) == 8:
            player.currentRoom.send()

    async def pushButton(self, player, command, content):
        button_number = self.player_list.index(player)
        changing_torches = self.buttons[button_number]
        for torch in changing_torches:
            self.torches[torch] = not self.torches[torch]
        await self.printTorches(player)

