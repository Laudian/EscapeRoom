from Room import Room
import logging


class Quizroom(Room):
    def __init__(self, game):
        super().__init__("Quiz", game)

        # variables
        self.progress = {}
        self.mistakes = {}
        self.starttext = ""
        self.roomreward = ""  # TODO: add reward for completing

        # questions
        self.questions = ("Hier ist deine erste Frage:\n" + "789 + 212 =",
                          "Nächste Frage:\n" + "13 x 3=",
                          "Nächste Frage:\n" + "Salz  in Wasser ist eine",
                          "Nächste Frage:\n" + "In welchem englischen Buch kann man sein Gesicht mit anderen teilen?",
                          "Nächste Frage:\n" + "Wie viele Stunden hat der vierte Monat eines Jahres?",
                          "Letzte Frage:\n" + "Welches Wort versteckt sich in diesem Anagram: settinggenus :grin:",
                          "Du hast bereits alle Fragen richtig beantwortet")

        # answers should be lowercase and without spaces
        self.answers = ("1001",
                        "39",
                        "lösung",
                        "facebook",
                        "720",
                        "eignungstest")

        # register commands
        self.registerCommand("progress", self.getProgress, "Fortschritt anzeigen - Quizroom")
        self.registerCommand("question", self.getQuestion, "Frage anzeigen - Quizroom")
        self.registerCommand("answer", self.giveAnswer, "Antwort eingeben - Quizroom")

    # private
    # starting test at player joining
    def enter(self, player):
        player.send(self.starttext)
        self.progress[player] = 0
        self.mistakes[player] = 0
        self.getQuestion(self, "", player, "")

    # public
    # get progress
    def getProgress(self, command, player, content):
        progress = self.progress[player]
        player.send("Du hast " + str(progress) + " von " + str(len(self.questions) - 1) + " Aufgaben gelöst" + \
                  " und bisher " + str(self.mistakes[player]) + "-mal falsch geantwortet.")

    # show current question
    def getQuestion(self, command, player, content):
        progress = self.progress[player]
        question = self.questions[progress]
        player.send(question)

    # give an answer
    def giveAnswer(self, command, player, content):
        progress = self.progress[player]
        answer_given = (str(content).lower()).replace(" ", "")
        answer_right = self.answers[progress]
        if answer_given == answer_right:
            if len(self.questions) == self.progress[player]:
                player.send("Herzlichen Glückwunsch! Du hast das Quiz abgeschlossen :partying_face: \n" +
                          self.roomreward)
            else:
                self.progress[player] += 1
                nextquestion = self.questions[progress + 1]
                player.send("Korrekt.\n" + nextquestion)
        else:
            self.mistakes[player] += 1
            player.send("Das ist leider nicht richtig :frowning: oder vielleicht falsch eingeben? :thinking:\n" +
                      "Probiers nochmal")