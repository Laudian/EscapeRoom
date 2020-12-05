from Room import Room
import logging

class Entrance(Room):
    def __init__(self, game):
        super().__init__("Eingangshalle", game)
        self.setPermission("textchannel_available", True)
        self.setPermission("voicechannel_available", True)
        self.registerCommand("test", self.test, "This method is used to test commandsv - Entrance")
        return

    def test(self):
        logging.debug("Test was called in Entrance")
        return