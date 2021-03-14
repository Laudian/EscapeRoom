from Room import Room


class PrivateRoom(Room):
    def __init__(self, parent: Room, nameappend=""):
        super().__init__(parent.name+nameappend, parent.game)
        self.parent = parent
        self.topic = parent.topic

    async def setup(self):
        await self.parent.game.setup_room(self, self.parent.category, self.parent)

    # This Method is called if the command used is unavailable in this room. It will inform the player
    # of this by whispering to him
    async def handle_invalid_command(self, caller, command, content):
        await self.parent.handle_invalid_command(caller, command, content)
        return

    # This method handles commands that players use and should be called by the game commandHandler
    # Usually,  every command should have it's own function which is accessed via a dictionary
    async def handle_command(self, caller, command, content=None):
        await self.parent.handle_command(caller, command, content)
        return

    def __repr__(self) -> str:
        return self.parent.name

    def log(self, message: str):
        self.parent.log(message)
