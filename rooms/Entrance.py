from Room import Room
import logging

# noinspection PyUnreachableCode
if False:
    from Player import Player

class Entrance(Room):
    def __init__(self, game):
        super().__init__("Eingangshalle", game)
        self.registerCommand("test", self.test, "This method is used to test commands - Entrance")
        self.registerCommand("start", self.start, "This method starts the game.")
        return

    async def test(self, caller, command, content):
        logging.debug("Test was called in Entrance")
        self.send("Ich habe den !test Command erfolgreich erkannt.")
        return

    async def start(self, caller: "Player", command, content):
        self.log(str(self.getPlayers()))
        self.log("start called by " + caller.name)
        # move all players from Entrance to Their starting room
        for player in list(self.getPlayers()):
            await self.leave(player)
            nextroom = self.game.get_room("Quiz")
            await nextroom.enter(player)
