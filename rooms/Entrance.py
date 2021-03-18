from Room import Room
import logging

# noinspection PyUnreachableCode
if False:
    from EscapeRoom import EscapeRoom

class Entrance(Room):
    def __init__(self, game: "EscapeRoom"):
        super().__init__("Eingangshalle", game)
