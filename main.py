import csv
import re

CSVFilename = "lesson1.csv"

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


def csvFileToDiagnostics(filename):
    diagnostics = []
    with open(filename) as f:
        reader = csv.reader(f)
        reader.__next__()
        for i, row in enumerate(reader):
            d = Diagnostic(row[2], row[3], row[4])
            if i != 0:
                diagnostics[i - 1].next = d
            diagnostics.append(d)
    return diagnostics


class ProblemContext(object):
    def __init__(self, problem, startingDiagnostic, evalFunc):
        self.problem = problem
        self.current = startingDiagnostic
        self.evalFunc = evalFunc

    def poseProblem(self):
        self.answer = askQuestion(self.problem)
        askQuestion("How did you get that?")
        if not self.evalFunc(self.answer):
            self.current = traverse(self.current)
            self.reaskProblem()
        else:
            showLesson("Pat yourself on the back!")

    def reaskProblem(self):
        refinedAnswer = askQuestion(self.problem)
        if not self.evalFunc(refinedAnswer):
            self.current = traverse(self.current.next)
        else:
            showLesson("Pat yourself on the back!")

    def finalAskProblem(self):
        askQuestion(self.problem)
        #ZPD doo dah


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
        showLesson(d.lesson)
        return d

    traverse(d.next)


if __name__ == "__main__":
  
    problem = "What fraction of the balloons are popped?\n u u O u"
    diagnostics = csvFileToDiagnostics(CSVFilename)
    diagonstic = diagnostics[0]
    answerEval = "3/4"

    context = ProblemContext(problem, diagonstic,
                             regexEvalFunc(answerEval))

    context.poseProblem()
