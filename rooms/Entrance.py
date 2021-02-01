from Room import Room
import logging

if False:
    from Player import Player

class Entrance(Room):
    def __init__(self, game):
        super().__init__("Eingangshalle", game)
        self.registerCommand("test", self.test, "This method is used to test commands - Entrance")
        self.registerCommand("start", self.start, "This method starts the game.")
        return

    def test(self, caller, command, content):
        logging.debug("Test was called in Entrance")
        self.send("Ich habe den !test Command erfolgreich erkannt.")
        return

    def leave(self, player):
        super().leave(player)
        nextroom = self.game.get_room("Quiz")
        nextroom.enter(player)

    def start(self, caller: "Player", command, content):
        self.log("start called by " + caller.name)
        # move all players from Entrance to Their starting room
        for player in self.getPlayers():
            self.leave(player)
