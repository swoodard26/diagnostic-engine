import re

DONUTS_REGEX = '[0oO@]+'
ONE_DONUT_REGEX = '[0oO@]'
GROUP_DIVIDER_REGEX = "[\s\+]+"
START_REGEX = '^\s*'
END_REGEX = '\s*$'

def GetString(prompt):
    if prompt == None:
        stringPrompt = ""
    if callable(prompt):
        stringPrompt = prompt()
    else:
        stringPrompt = prompt
    stringPrompt += "\n"

    return stringPrompt

def AskQuestion (prompt):
    stringPrompt = GetString(prompt)
    answer = input(stringPrompt)
    return answer

def ShowMessage(prompt):
    stringPrompt = GetString(prompt)
    print(stringPrompt)

class Node:
    def __init__(self, output, parentNode = None, parentEvalFunc = lambda x: True, isQuestion = True):
        self.output = output
        self.answer = None
        self.edges = []
        self.isQuestion = isQuestion
        if parentNode != None:
            parentNode.CreateEdge(self,parentEvalFunc)
        
    def CreateEdge(self,end,evalFunc = lambda x: True):
        self.edges.append(Edge(end, evalFunc))

    def Run(self):
        if self.output == None:
            pass
        elif self.isQuestion:
            answer = AskQuestion(self.output)
            self.answer = answer
        else:
            ShowMessage(self.output)
        return self.EvalAnswer()
    
    def EvalAnswer(self):
        if len(self.edges) == 0:
            return EndNode(self)
        for edge in self.edges:
            if edge.Eval(self.answer):
                return edge.end
        return self

class EndNode(Node):
    def __init__(self, parentNode):
        Node.__init__(self, "", parentNode)

class Edge:
    def __init__(self, end, evalFunc):
        self.end = end
        self.Eval = evalFunc

def RunGraph(root):
    finished = False
    currentNode = root
    while not finished:
        nextNode = currentNode.Run()
        if type(nextNode) == EndNode:
            finished = True
        currentNode = nextNode

def CheckIfMadeDonut(answer):
    return re.compile(DONUTS_REGEX).match(answer)

def CheckIfMadeOnlyDonut(answer):
    # Answer ONLY contains a donut symbol
    p = re.compile(START_REGEX + DONUTS_REGEX + END_REGEX)
    return p.match(answer)

def CheckIfTwoGroups(answer):
    p = re.compile(START_REGEX + DONUTS_REGEX + GROUP_DIVIDER_REGEX + DONUTS_REGEX + END_REGEX)
    return p.match(answer)

def mentionAddMatch(answer):
    matches = re.findall('addition|adding|adder|add|plus', answer)
    if len(matches) == 0:
        return None
    return matches[0]
    
def didMentionAdd(answer):
    return mentionAddMatch(answer) != None

def CountDonuts(answer):
    if answer == None:
        return 0
    return len(re.findall(ONE_DONUT_REGEX,answer))

if __name__ == "__main__":

    mathProblem = "What is 4+4?"
    correctAnswer = 8

    greetingNode = Node("What is your name?")
    niceToMeetYouNode = Node(lambda: "Great to meet you, " + greetingNode.answer, greetingNode, lambda x: x != "", isQuestion = False)

    whatIs4Plus4Node = Node(mathProblem, niceToMeetYouNode)
    howDidYouGetThatNode = Node("How did you get that?", whatIs4Plus4Node, lambda x: x != "")
    GotItRightNode = Node("Well done!", howDidYouGetThatNode, lambda x: int(whatIs4Plus4Node.answer) == correctAnswer)

    GotItWrongNode = Node("Why don't we try adding using donuts.", howDidYouGetThatNode, lambda x: int(whatIs4Plus4Node.answer) != correctAnswer, isQuestion = False)

    donutStartNode = Node("Look, a donut!\n\no\n\nCan you make a donut?",whatIs4Plus4Node,lambda x: x == "")
    GotItWrongNode.CreateEdge(donutStartNode)

    helpMakingDonutsNode = Node("Try using the \"o\" key on your keyboard to make a donut!", donutStartNode, lambda x: not CheckIfMadeOnlyDonut(x))
    
    donutSecondNode = Node("Make more donuts!", donutStartNode, lambda x :CheckIfMadeOnlyDonut(x))
    helpMakingDonutsNode.CreateEdge(donutSecondNode, lambda x: CheckIfMadeOnlyDonut(x))
    
    helpMakingOnlyDonutsNode = Node("Try making donuts with just o.",donutSecondNode,lambda x: CheckIfMadeDonut(x) and not CheckIfMadeOnlyDonut(x))
    helpMakingDonutsNode.CreateEdge(helpMakingOnlyDonutsNode,lambda x: CheckIfMadeDonut(x) and not CheckIfMadeOnlyDonut(x))

    donutRepresentationNode = Node("Try using donuts to represent this problem: " + mathProblem, donutSecondNode, lambda x: CheckIfMadeOnlyDonut(x))
    helpMakingOnlyDonutsNode.CreateEdge(donutRepresentationNode, lambda x: CheckIfMadeOnlyDonut(x))

    isThisARepresentationNode = Node(None, donutRepresentationNode, lambda x: CheckIfMadeDonut(x))
    
    howManyGroupsDoWeWantNode = Node("How many groups of donuts would we want to represent in this problem?", isThisARepresentationNode, lambda x: not CheckIfTwoGroups(donutRepresentationNode.answer))

    additionTeachingStartNode = Node("What is the + operator?", howManyGroupsDoWeWantNode, lambda x: x != 2)
    additionTeachingMentionAddNode = Node(lambda: "Great! That's right, like you said, " + mentionAddMatch(additionTeachingStartNode.answer) + ". '+' is the addition operator.", additionTeachingStartNode
                                          , lambda x: didMentionAdd(x),isQuestion = False)
    explainPlusOperatorNode = Node("The + operator is the 'addition' operator.", additionTeachingStartNode, lambda x: answer != "" and not didMentionAdd(answer), isQuestion = False)
    
    exampleOfAdditionNode = Node("In our donuts case, oooo + oooo becomes oooooooo.", explainPlusOperatorNode,isQuestion = False)
    additionTeachingMentionAddNode.CreateEdge(exampleOfAdditionNode)
    
    twoGroupsRepNode = Node("Type in a representation with two groups", howManyGroupsDoWeWantNode, lambda x: x == 2)
    notTwoGroupsRepNode = Node("I'm not sure if that is two groups. How did you separate your groups?", twoGroupsRepNode,lambda x: not CheckIfTwoGroups(x))

    countDonutNode = Node(None, isThisARepresentationNode, lambda x: CheckIfTwoGroups(donutRepresentationNode.answer))
    twoGroupsRepNode.CreateEdge(countDonutNode,lambda x: CheckIfTwoGroups(x))

    explainHowDonutsHelpNode = Node("How do donuts help you solve: " + mathProblem, countDonutNode,lambda x: CountDonuts(donutRepresentationNode.answer) == correctAnswer or CountDonuts(twoGroupsRepNode.answer) == correctAnswer)
    exampleOfAdditionNode.CreateEdge(donutRepresentationNode)
    
    checkRightAnswerNode = Node("Great, now let's solve the original problem with donuts: "+mathProblem,explainHowDonutsHelpNode)

    numberOfDonutsInRepresentationNode = Node("WELCOME TO THE TREE ABOUT REPRESENTING THE CORRECT NUMBER OF DONUTS",countDonutNode,lambda x: CountDonuts(donutRepresentationNode.answer) != correctAnswer or CountDonuts(twoGroupsRepNode.answer) != correctAnswer)
    numberOfDonutsInRepresentationNode.CreateEdge(donutRepresentationNode)

    RunGraph(greetingNode)
