import csv
import re
import random
import math

CSVFilename = "lesson2.csv"

def getString(prompt):
    if prompt == None:
        stringPrompt = ""
    if callable(prompt):
        stringPrompt = prompt()
    else:
        stringPrompt = prompt
    stringPrompt += "\n"

    return stringPrompt


def askQuestion(prompt):
    stringPrompt = getString(prompt)
    answer = input(stringPrompt)
    return answer


def showLesson(prompt):
    stringPrompt = getString(prompt)
    print(stringPrompt)


class ProblemContext(object):
    def __init__(self, problem, file):
        self.problem = problem
        self.evalFunc = problem.evalAnswer()
        self.current = None
        self.file = file

        self.csvFileToDiagnostics()

    def csvFileToDiagnostics(self):
        diagnostics = []
        with open(self.file) as f:
            reader = csv.reader(f)
            reader.__next__()
            for i, row in enumerate(reader):
                regex = self.evalToCreateRegex(row[3])
                d = Diagnostic(row[2], regex, row[4])
                if i != 0:
                    diagnostics[i - 1].next = d
                diagnostics.append(d)
        self.current = diagnostics[0]

    def evalToCreateRegex(self,stringToEval):
        total = self.problem.total
        numerator = self.problem.numerator
        regexString = str(eval(stringToEval))
        return regexString

    def poseProblem(self):
        self.answer = askQuestion(self.problem.generate())
        askQuestion("How did you get that?")
        if not self.evalFunc(self.answer):
            self.current = traverse(self.current)
            self.reaskProblem()
        else:
            showLesson("Pat yourself on the back!")

    def reaskProblem(self):
        refinedAnswer = askQuestion(self.problem.generate())
        if not self.evalFunc(refinedAnswer):
            self.current = traverse(self.current.next)
        else:
            showLesson("Pat yourself on the back!")

    def finalAskProblem(self):
        askQuestion(self.problem.generate())
        #ZPD doo dah


class SoccerProblem(object):
    def __init__(self, scored, total):
        self.total = total
        self.scored = scored
        self.numerator = self.scored

    def generateBallstring(self, ballsToPlace):
        ballsPlaced = 0
        ballstring = ''
        totalSlots = ballsToPlace * 2
        for i in range(0, totalSlots):
            slotsLeft = totalSlots - i
            ballsLeft = ballsToPlace - ballsPlaced
            percentage = ballsLeft / slotsLeft
            if random.random() < percentage:
                ballstring += 'o'
                ballsPlaced += 1
            else:
                ballstring += ' '

        return ballstring

    def generate(self):
        notScored = self.generateBallstring(self.total - self.scored)
        scored = self.generateBallstring(self.scored)

        halfIndex = math.floor(len(notScored) / 2)

        topString = " " * halfIndex + "_" * (len(scored) + 2)
        bottomString = notScored[0:halfIndex] + "|" + scored + "|" + notScored[
            halfIndex:]

        question = "What fraction of the soccer balls are in the goal?\n\n" + topString + "\n" + bottomString

        return question

        #        __________
        # o o oo |  o oo o| o o
    
    def evalAnswer(self):
        return regexEvalFunc(str(self.numerator) + "/" + str(self.total))


class Diagnostic(object):
    def __init__(self, question, regex, lesson, nextDiagnostic=None):
        self.question = question
        self.lesson = lesson
        self.eval = regexEvalFunc(regex)
        self.next = nextDiagnostic


def regexEvalFunc(regex):
    p = re.compile(regex)
    return p.match


def traverse(d):
    if d is None:
        showLesson(
            "The robot can't figure out how to help you learn. Raise your hand and ask a real human :)"
        )
        return d

    answer = askQuestion(d.question)
    if not d.eval(answer):
        askQuestion(d.lesson)
        return d

    traverse(d.next)


#What fraction of the soccer balls made it in the goal?

if __name__ == "__main__":

    numProblems = 5
    maxValue = 10

    while (numProblems > 0):
        randomTotal = random.randint(4, maxValue)
        randomScored = random.randint(1, randomTotal-1)

        problem = SoccerProblem(randomScored, randomTotal)
        context = ProblemContext(problem, CSVFilename)
        context.poseProblem()
        
        numProblems -= 1
