from Room import Room
from .PrivateRoom import PrivateRoom
import logging


class FourWalls(Room):
    def __init__(self, game):
        super().__init__("Vier Wände", game)

        # players
        self.player_group1 = []
        self.player_group2 = []
        self.progress_group1 = 0
        self.progress_group2 = 0
        # channel
        self.channels_group1 = {}
        self.channels_group2 = {}
        # passwords
        self.passwords = {0: "Eigentlich sollte man diese Nachricht nicht sehen",
                          1: "333333333343333", 2: "#1aff11", 3: "qvypam", 4: ":flag_re:"}
        # startmessages
        self.startmessage = {1: "Passwort 1: 28 Halbkreise\n"
                                "Passwort 2: Twitter\n"
                                "Passwort 3: QV...\n"
                                "Passwort 4: :xxxx_xx:\n",
                             2: "Passwort 1: beinhaltet 3\n"
                                "Passwort 2: startet perfekt Hexadezimal\n"
                                "Passwort 3: ...V...A...\n"
                                "Passwort 4: re\n",
                             3: "Passwort 1: 15 Ziffern\n"
                                "Passwort 2: FF11, 1D47, BD13, A2A3, 3BC5\n"
                                "Passwort 3: 6 Buchstaben\n"
                                "Passwort 4: Flagge\n",
                             4: "Passwort 1: 4 an 11.\n"
                                "Passwort 2: sehr grüne Farbe\n"
                                "Passwort 3: ...Y...M\n"
                                "Passwort 4: Emoji\n"}
        # register commands
        self.register_command("skip", self.skip, "Raum überspringen")
        self.register_command("password", self.checkPassword, "eingebebenes Passwort auf Richtigkeit überprüfen")

    async def enter(self, player):
        self.lock.acquire()
        self.players.append(player)
        in_group_nr = len(self.players)
        # fill group 1
        if in_group_nr < 4:
            self.player_group1.append(player)
            self.channels_group1["player_" + str(in_group_nr)] = PrivateRoom(self, " " + str(in_group_nr) +
                                                                             " " + player.name)
            await self.channels_group1["player_" + str(in_group_nr)].setup()
            self.channels_group1["player_" + str(in_group_nr)].send(self.startmessage[in_group_nr])
            await self.channels_group1["player_" + str(in_group_nr)].enter(player)
        # start group 1
        elif in_group_nr == 4:
            self.player_group1.append(player)
            self.channels_group1["player_" + str(in_group_nr)] = PrivateRoom(self, " " + str(in_group_nr) +
                                                                             " " + player.name)
            await self.channels_group1["player_" + str(in_group_nr)].setup()
            self.channels_group1["player_" + str(in_group_nr)].send(self.startmessage[in_group_nr])
            await self.channels_group1["player_" + str(in_group_nr)].enter(player)
            await self.createPrivateRooms(self.channels_group1)
            await self.setPermissions(1)
            await self.showPrivateRooms(1)
        # fill group 2
        elif in_group_nr < 8:
            self.player_group2.append(player)
            self.channels_group2["player_" + str(in_group_nr - 4)] = PrivateRoom(self, " " + str(in_group_nr) +
                                                                                 " " + player.name)
            await self.channels_group2["player_" + str(in_group_nr - 4)].setup()
            self.channels_group2["player_" + str(in_group_nr - 4)].send(self.startmessage[in_group_nr - 4])
            await self.channels_group2["player_" + str(in_group_nr - 4)].enter(player)
        # start group 2
        else:
            self.player_group2.append(player)
            self.channels_group2["player_" + str(in_group_nr - 4)] = PrivateRoom(self, " " + str(in_group_nr) +
                                                                                 " " + player.name)
            await self.channels_group2["player_" + str(in_group_nr - 4)].setup()
            self.channels_group2["player_" + str(in_group_nr - 4)].send(self.startmessage[in_group_nr - 4])
            await self.channels_group2["player_" + str(in_group_nr - 4)].enter(player)
            await self.createPrivateRooms(self.channels_group2)
            await self.setPermissions(2)
            await self.showPrivateRooms(2)
        self.lock.release()

    # create all channels incl. startmessages
    async def createPrivateRooms(self, group_channels_dict):
        # create private rooms
        group_channels_dict["voice_1_2"] = PrivateRoom(self, " 1 2")
        group_channels_dict["text_2_3"] = PrivateRoom(self, " 2 3")
        group_channels_dict["text_3_4"] = PrivateRoom(self, " 3 4")
        group_channels_dict["text_4_1"] = PrivateRoom(self, " 4 1")
        await group_channels_dict["voice_1_2"].setup()
        await group_channels_dict["text_2_3"].setup()
        await group_channels_dict["text_3_4"].setup()
        await group_channels_dict["text_4_1"].setup()

    async def setPermissions(self, group):
        group_channels_dict = self.channels_group1 if group == 1 else self.channels_group2
        group_players_list = self.player_group1 if group == 1 else self.player_group2
        # get discord users and channels
        discord_player1 = self.game.player_to_discord(group_players_list[0])
        discord_player2 = self.game.player_to_discord(group_players_list[1])
        discord_player3 = self.game.player_to_discord(group_players_list[2])
        discord_player4 = self.game.player_to_discord(group_players_list[3])
        discord_voice_1_2 = self.game.room_to_voicechannel(group_channels_dict["voice_1_2"])
        discord_text_2_3 = self.game.room_to_voicechannel(group_channels_dict["text_2_3"])
        discord_text_3_4 = self.game.room_to_voicechannel(group_channels_dict["text_3_4"])
        discord_text_4_1 = self.game.room_to_voicechannel(group_channels_dict["text_4_1"])
        # set permissions voice 1 2
        await discord_voice_1_2.set_permissions(target=discord_player2, speak=False)
        # set permissions text 2 3
        await discord_text_2_3.set_permissions(target=discord_player2, add_reactions=False)
        await discord_text_2_3.set_permissions(target=discord_player3, add_reactions=False)
        await discord_text_2_3.set_permissions(target=discord_player3, send_messages=False)
        # set permissions text 3 4
        await discord_text_3_4.set_permissions(target=discord_player4, add_reactions=False)
        await discord_text_3_4.set_permissions(target=discord_player4, send_messages=False)
        await discord_text_3_4.set_permissions(target=discord_player3, send_messages=False)
        # set permissions text 4 1
        await discord_text_4_1.set_permissions(target=discord_player4, add_reactions=False)
        await discord_text_4_1.set_permissions(target=discord_player1, add_reactions=False)
        await discord_text_4_1.set_permissions(target=discord_player1, send_messages=False)

    async def showPrivateRooms(self, group):
        group_channels_dict = self.channels_group1 if group == 1 else self.channels_group2
        group_players_list = self.player_group1 if group == 1 else self.player_group2
        player1 = group_players_list[0]
        player2 = group_players_list[1]
        player3 = group_players_list[2]
        player4 = group_players_list[3]
        # player 1
        await self.game.show_room(group_channels_dict["text_4_1"], player1, text=True, voice=False)
        await self.game.show_room(group_channels_dict["voice_1_2"], player1, text=False, voice=True)
        # player 2
        await self.game.show_room(group_channels_dict["voice_1_2"], player2, text=False, voice=True)
        await self.game.show_room(group_channels_dict["text_2_3"], player2, text=True, voice=False)
        # player 3
        await self.game.show_room(group_channels_dict["text_2_3"], player3, text=True, voice=False)
        await self.game.show_room(group_channels_dict["text_3_4"], player3, text=True, voice=False)
        # player 4
        await self.game.show_room(group_channels_dict["text_3_4"], player4, text=True, voice=False)
        await self.game.show_room(group_channels_dict["text_4_1"], player4, text=True, voice=False)

    async def hidePrivateRooms(self, group):
        group_channels_dict = self.channels_group1 if group == self.player_group1 else self.channels_group2
        player1 = group[0]
        player2 = group[1]
        player3 = group[2]
        player4 = group[3]
        # player 1
        await self.game.hide_room(group_channels_dict["text_4_1"], player1)
        await self.game.show_room(group_channels_dict["voice_1_2"], player1)
        # player 2
        await self.game.show_room(group_channels_dict["voice_1_2"], player2)
        await self.game.show_room(group_channels_dict["text_2_3"], player2)
        # player 3
        await self.game.show_room(group_channels_dict["text_2_3"], player3)
        await self.game.show_room(group_channels_dict["text_3_4"], player3)
        # player 4
        await self.game.show_room(group_channels_dict["text_3_4"], player4)
        await self.game.show_room(group_channels_dict["text_4_1"], player4)

    # pass message from player 2 to player 4 without 4 knowing i comes from 2
    async def passOnMessage(self, player, command, content):
        if player == self.player_group1[1]:
            await self.channels_group1["text_3_4"].send(content)
        if player == self.player_group2[1]:
            await self.channels_group2["text_3_4"].send(content)

    # check password for each player
    async def checkPassword(self, player, command, content):
        player_nr = -1
        group = 0
        if player in self.player_group1:
            player_nr = self.player_group1.index(player)
            group = 1
        elif player in self.player_group2:
            player_nr = self.player_group2.index(player)
            group = 2
        if content.lower() == self.passwords[player_nr + 1]:
            if group == 1:
                self.progress_group1 += 1
                if self.progress_group1 == 4:
                    await self.rewardGroup(self.player_group1)
            elif group == 2:
                self.progress_group2 += 1
                if self.progress_group2 == 4:
                    await self.rewardGroup(self.player_group2)
        else:
            player.currentRoom.send("Das passt leider nicht")

    @Room.requires_mod
    async def skip(self, player, command, content):
        await self.rewardGroup(self.player_group1)
        await self.rewardGroup(self.player_group2)

    # end of the room
    async def rewardGroup(self, group):
        for player in group:
            await self.hidePrivateRooms(group)
            await self.leave(player)
            await self.game.hide_room()
            nextroom = self.game.get_room("Globglogabgalab")
            await nextroom.enter(player)

    async def leave(self, player):
        await self.game.hide_room(player.currentRoom, player)
        await player.currentRoom.leave(player)
        self.players.remove(player)
