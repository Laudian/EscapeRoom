from Room import Room
import logging


class Quizroom(Room):
    def __init__(self, game):
        super().__init__("Quiz", game)
        # variables
        self.progress = {}
        self.mistakes = {}
        self.starttext = "Herzlich Willkommen im Quizroom"
        self.roomreward = ""  # TODO: add str(reward) for completing

        # questions
        self.questions = ("Hier ist deine erste Frage:\n" + "789 + 212 =",
                          "Nächste Frage:\n" + "13 x 3=",
                          "Nächste Frage:\n" + "Salz  in Wasser ist eine",
                          "Nächste Frage:\n" + "In welchem englischen Buch kann man sein Gesicht mit anderen teilen?",
                          "Nächste Frage:\n" + "Wie viele Stunden hat der vierte Monat eines Jahres?",
                          "Letzte Frage:\n" + "Welches Wort versteckt sich in diesem Anagram: settinggenus :grin:",
                          "Herzlichen Glückwunsch! Du hast das Quiz abgeschlossen :partying_face: \n" + self.roomreward)

        # answers
        self.answers = ("1001",
                        "39",
                        "Lösung",
                        "Facebook",
                        "720",
                        "Eignungstest")

        # register commands
        self.registerCommand("progress", self.getProgress, "Fortschritt anzeigen - Quizroom")
        self.registerCommand("question", self.getQuestion, "Frage anzeigen - Quizroom")
        self.registerCommand("answer", self.giveAnswer, "Antwort eingeben - Quizroom")

    # private
    # starting test at player joining
    def enter(self, player):
        super().enter(player)
        player.send(self.starttext)
        self.progress[player] = 0
        self.mistakes[player] = 0
        self.getQuestion(player, None, None)

    def completed(self, player):
        self.getProgress(player, None, None)
        # TODO: add rewards for completing like e.g. permission for next roomk
        self.progress[player] = 0
        self.mistakes[player] = 0

    # public
    # get progress
    def getProgress(self, player, command, content):
        progress = self.progress[player]
        player.send("Du hast " + str(progress) + " von " + str(len(self.questions) - 1) + " Aufgaben gelöst" +
                    " und bisher " + str(self.mistakes[player]) + "-mal falsch geantwortet.")

    # show current question
    def getQuestion(self, player, command, content):
        progress = self.progress[player]
        question = self.questions[progress]
        player.send(question)

    # give an answer
    def giveAnswer(self, player, command, content):
        progress = self.progress[player]
        given_answer = (str(content).lower()).replace(" ", "")
        right_answer = self.answers[progress]
        right_answer = (str(right_answer).lower()).replace(" ", "")
        if given_answer == right_answer:
            self.progress[player] += 1
            nextquestion = self.questions[progress + 1]
            player.send("Korrekt.\n" + nextquestion)
            if self. progress[player] + 1 == len(self.questions):
                self.completed(player)
        else:
            self.mistakes[player] += 1
            player.send("Das ist leider nicht richtig :frowning: oder vielleicht falsch eingeben? :thinking:\n" +
                        "Probiers nochmal")
