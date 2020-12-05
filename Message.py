import logging
import Settings_local as Settings
import enum

class MessageType(enum):
    CHANNEL = 1
    PLAYER = 2

class Message(object):
    def __init__(self, target, type : MessageType, content):
        self.target = target
        self.type = type
        self.content = content
        return
