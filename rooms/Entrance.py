from Room import Room
import logging

# noinspection PyUnreachableCode
if False:
    from Player import Player
    from EscapeRoom import EscapeRoom

class Entrance(Room):
    def __init__(self, game: "EscapeRoom"):
        super().__init__("Eingangshalle", game)
        self.register_command("test", self.test, "This method is used to test commands - Entrance")
        self.register_command("start", self.start, "This method starts the game.")
        return

    async def test(self, caller: "Player", command: str, content: str):
        logging.debug("Test was called in Entrance")
        self.send("Ich habe den !test Command erfolgreich erkannt.")
        return

    async def start(self, caller: "Player", command: str, content: str):
        self.log("Players: " + str(self.get_players()))
        self.log("start called by " + caller.name)
        # move all players from Entrance to Their starting room
        for player in list(self.get_players()):
            await self.leave(player)
            nextroom = self.game.get_room("Höhleneingang")
            await nextroom.enter(player)
