import logging

class Player(object):
    __id = 1
    def __init__(self, name):
        self.id = __id
        __id += 1
        self.name = name
        self.current_room = None
        logging.info("Player {name} has joined the game, ID is {id).".format(name=self.name, id=self.id))
        return

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self == other
