import logging

class Player(object):
    id = 0
    def __init__(self, name):
        self.id = Player.getId()
        self.name = name
        self.current_room = None
        logging.info("Player {name} has joined the game, ID is {id).".format(name=self.name, id=self.id))
        return

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self == other

    def getId():
        id += 1
        return id