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
        self.passwords = {1: "000000000040000", 2: "passwort", 3: "qvypam", 4: "🇷🇪"}
        # startmessages
        self.startmessage = {1: "Du gehst in einen Raum, bei dem die Wand links von dir eine große Glasscheibe ist,"
                                " durch die du deinen Partner von eben sehen kannst. Sie scheint Schalldicht zu sein,"
                                " dein Partner gibt dir aber zu verstehen, dass er an deinen Lippen ablesen kann, was"
                                " du sagst.. An der Wand geradeaus hängt eine Tafel, du kannst aber nichts finden um"
                                " auf der Tafel zu schreiben. An der Wand rechts von dir ist wieder eine Art "
                                "Eingabefeld in das du ein Passwort eingeben kannst, indem du !passwort benutzt."
                                " Zudem findest du noch einige Hinweise in den Boden eingeritzt:\n"
                                "Passwort 1: 14 Kreise\n"
                                "Passwort 2: Cnffjbeg\n"
                                "Passwort 3: QV...\n"
                                "Passwort 4: :xxxx_xx:\n",
                             2: "Der Raum der sich neu für dich öffnet hat rechts von dir eine große Glasscheibe "
                                "als Wand. Dort siehst du deinen Partner von eben, kannst ihn aber nicht hören. Was"
                                " dich nicht weiter stört, da du lippenlesen kannst. Du verstehst also alles, die "
                                "Schalldichte Scheibe verhindert aber, dass du ihm antworten kannst. An der Wand, "
                                "dir gegenüber hängt eine Tafel und dabei liegen einige Stücke Kreide. An der Wand "
                                "links von dir ist wieder eine Art Eingabefeld in das du ein Passwort eingeben kannst,"
                                " indem du !passwort benutzt. Zudem findest du noch einige Hinweise in den Boden "
                                "eingeritzt:\n"
                                "Passwort 1: beinhaltet 0\n"
                                "Passwort 2: Rot\n"
                                "Passwort 3: ...Y...A...\n"
                                "Passwort 4: re\n",
                             3: "Ermutigt gehst du weiter in den neuen Raum und blickst zuerst geradeaus auf eine Wand "
                                "mit einer großen Tafel. Links von dir ist ein riesiges Panoramafenster hinter dem du"
                                " deinen Partner vom Rätsel vorher wiederfindest. Hören tut ihr aber absolut nichts "
                                "voneinander, es muss also anders funktionieren: Du kannst einzelne Nachrichten"
                                " “weiterleiten” an ihn, indem du sie ihm pantomimisch darstellst. In Discord"
                                " übersetzt bedeutet das, dass du auf die Nachrichten reagieren kannst und"
                                " dabei allerlei mögliche Reaktionen verwenden kannst, einzelne Buchstaben,"
                                " Flaggen, diverse Zeichen, Essen, Tiere und natürlich auch Smileys. So kannst "
                                "du zu der Nachricht auch deine Eigenen Inhalte vermitteln. An der Wand rechts"
                                " von dir ist wieder eine Art Eingabefeld in das du ein Passwort eingeben kannst,"
                                " indem du !passwort benutzt. Zudem findest du noch einige Hinweise in den Boden"
                                " eingeritzt:\n"
                                "Passwort 1: 15 Ziffern\n"
                                "Passwort 2: A\n"
                                "Passwort 3: 6 Buchstaben\n"
                                "Passwort 4: Flagge\n",
                             4: "Du betrittst den neuen Raum und kannst zumindest mal durch die große "
                                "Panoramafensterscheibe rechts von dir deinen vorherigen Partner zur Gänze sehen."
                                " An der Wand geradeaus siehst du eine Tafel mit einigen Stücken Kreide mit denen du"
                                " an der Tafel schreiben kannst. An der Wand links von dir ist wieder eine Art"
                                " Eingabefeld in das du ein Passwort eingeben kannst, indem du !passwort benutzt."
                                " Zudem findest du noch einige Hinweise in den Boden eingeritzt:\n"
                                "Passwort 1: 4 an 11.\n"
                                "Passwort 2: Tion13\n"
                                "Passwort 3: ...P...M\n"
                                "Passwort 4: Emoji\n"}
        # register commands
        self.register_command("skip", self.skip, "Raum überspringen")
        self.register_command("password", self.checkPassword, "eingebebenes Passwort auf Richtigkeit überprüfen")
        self.register_command(None, self.passOnMessage, "Nachricht von Text 2-3 in Text 3-4 weiterleiten")

    async def enter(self, player):
        self.lock.acquire()
        self.players.append(player)
        player_nr = len(self.players)
        # fill group 1
        if player_nr <= 4:
            self.player_group1.append(player)
            await self.createAndShowPersonalRoom(player, player_nr)
            # start group 1
            if player_nr == 4:
                await self.createPrivateRooms(self.channels_group1)
                await self.showPrivateRooms(1)
        # fill group 2
        else:
            self.player_group2.append(player)
            await self.createAndShowPersonalRoom(player, player_nr - 4)
            # start group 2
            if player_nr == 8:
                await self.createPrivateRooms(self.channels_group2)
                await self.showPrivateRooms(2)
        self.lock.release()

    # create all channels incl. startmessages
    async def createPrivateRooms(self, group_channels_dict):
        # create private rooms
        group_channels_dict["voice_1_2"] = PrivateRoom(self, " 1-2")
        group_channels_dict["text_2_3"] = PrivateRoom(self, " 2-3")
        group_channels_dict["text_3_4"] = PrivateRoom(self, " 3-4")
        group_channels_dict["text_4_1"] = PrivateRoom(self, " 4-1")
        await group_channels_dict["voice_1_2"].setup()
        await group_channels_dict["text_2_3"].setup()
        await group_channels_dict["text_3_4"].setup()
        await group_channels_dict["text_4_1"].setup()

    async def createAndShowPersonalRoom(self, player, in_group_nr, group):
        group_channels_dict = self.channels_group1 if group == 1 else self.channels_group2
        in_group_nr_str = str(in_group_nr)
        group_channels_dict["player_" + in_group_nr_str] = PrivateRoom(self, " " + in_group_nr_str + " " + player.name)
        await group_channels_dict["player_" + in_group_nr_str].setup()
        group_channels_dict["player_" + in_group_nr_str].send(self.startmessage[in_group_nr])
        await group_channels_dict["player_" + in_group_nr_str].enter(player)
        await self.game.show_room(group_channels_dict["player_" + in_group_nr_str], player, text=True)

    async def showPrivateRooms(self, group):
        group_channels = self.channels_group1 if group == 1 else self.channels_group2
        group_players_list = self.player_group1 if group == 1 else self.player_group2
        player1 = group_players_list[0]
        player2 = group_players_list[1]
        player3 = group_players_list[2]
        player4 = group_players_list[3]
        # player 1
        await self.game.show_room(group_channels["text_4_1"], player1, text=True, voice=False, write=False, react=False)
        await self.game.show_room(group_channels["voice_1_2"], player1, text=False, voice=True)
        # player 2
        await self.game.show_room(group_channels["voice_1_2"], player2, text=False, voice=True, speak=False)
        await self.game.show_room(group_channels["text_2_3"], player2, text=True, voice=False, react=False)
        # player 3
        await self.game.show_room(group_channels["text_2_3"], player3, text=True, voice=False, write=False, react=False)
        await self.game.show_room(group_channels["text_3_4"], player3, text=True, voice=False, write=False)
        # player 4
        await self.game.show_room(group_channels["text_3_4"], player4, text=True, voice=False, write=False, react=False)
        await self.game.show_room(group_channels["text_4_1"], player4, text=True, voice=False)

    async def hidePrivateRooms(self, group):
        group_channels = self.channels_group1 if group == self.player_group1 else self.channels_group2
        player1 = group[0]
        player2 = group[1]
        player3 = group[2]
        player4 = group[3]
        # player 1
        await self.game.hide_room(group_channels["text_4_1"], player1)
        await self.game.show_room(group_channels["voice_1_2"], player1)
        # player 2
        await self.game.show_room(group_channels["voice_1_2"], player2)
        await self.game.show_room(group_channels["text_2_3"], player2)
        # player 3
        await self.game.show_room(group_channels["text_2_3"], player3)
        await self.game.show_room(group_channels["text_3_4"], player3)
        # player 4
        await self.game.show_room(group_channels["text_3_4"], player4)
        await self.game.show_room(group_channels["text_4_1"], player4)

    # pass message from player 2 to player 4 without 4 knowing i comes from 2
    async def passOnMessage(self, player, command, content):
        if player == self.player_group1[1]:
            await self.channels_group1["text_3_4"].send(content)
        elif player == self.player_group2[1]:
            await self.channels_group2["text_3_4"].send(content)

    # check password for each player
    async def checkPassword(self, player, command, content):
        group = 0
        if player in self.player_group1:
            player_nr = self.player_group1.index(player)
            group = 1
        else:
            player_nr = self.player_group2.index(player)
            group = 2
        if content.lower() == self.passwords[player_nr + 1]:
            if group == 1:
                self.progress_group1 += 1
                player.currentRoom.send("Korrekt!\n" + str(self.progress_group1) + "/4 Passwörtern richtig eingegeben")
                if self.progress_group1 == 4:
                    await self.rewardGroup(self.player_group1)
            elif group == 2:
                self.progress_group2 += 1
                player.currentRoom.send("Korrekt!\n" + str(self.progress_group1) + "/4 Passwörtern richtig eingegeben")
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
