import logging
from Message import *

class Player(object):
    id = 0
    def __init__(self, name, game):
        self.id = Player.getId()
        self.name = name
        self.current_room = None
        self.message_type = MessageType.PLAYER
        logging.info("Player {name} has joined the game, ID is {id).".format(name=self.name, id=self.id))
        self.game = game
        return

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self == other

    # Sends a message to this player, me be string or an image
    def send(self, message):
        self.game.sendMessage(self, message)
        return

    @staticmethod
    def getId():
        id += 1
        return id