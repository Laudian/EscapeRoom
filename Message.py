import logging
import Settings_local as Settings
from enum import Enum

class MessageType(Enum):
    CHANNEL = 1
    PLAYER = 2

class Message(object):
    def __init__(self, target, content):
        self.target = target
        self.content = content
        return
