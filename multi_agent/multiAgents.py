# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from game import Directions


class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in
                  legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if
                       scores[index] == bestScore]
        chosenIndex = random.choice(
            bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]


    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (oldFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        oldFood = currentGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in
                          newGhostStates]

        if currentGameState.isWin() or currentGameState.isLose():
            return currentGameState.getScore()

        food_xy = currentGameState.data.food.asList()
        food_num_left = len(food_xy)

        scared = 0
        min_ghost_dist = 999
        for ghost in newGhostStates:
            if min_ghost_dist > util.manhattanDistance(newPos,
                                                   ghost.getPosition()) and ghost.scaredTimer != 0:
                min_ghost_dist = util.manhattanDistance(newPos,
                                                    ghost.getPosition())
        sum = 0
        for i in range(len(newScaredTimes)):
            sum += newScaredTimes[i]
        if sum == 0:
            min_ghost_dist = -5

        min_food_dist = 999
        for food in food_xy:
            if min_food_dist > util.manhattanDistance(newPos, food):
                min_food_dist = util.manhattanDistance(newPos, food)

        food_dist = total_distance_from_list(newPos, food_xy)
        #food_dist = dist_from_list(newPos, food_xy)


        stop_reduction = 0
        if action == "Stop":
            stop_reduction = -5

        # if food_dist == 0 or min_ghost_dist == 0 or successorGameState.getScore() == 0 or food_num_left == 0 or stop_reduction == 0:
        #     return successorGameState.getScore()
        score = 0.7*successorGameState.getScore() \
                - 0.5*food_dist \
                 + 6* min_ghost_dist \
                 - 0.3*food_num_left\
                 + stop_reduction \

        print(successorGameState.getScore())
        return score


def dist_from_list(pos, object_list):
    "manhattern distance from pos to all other coordinates"
    dist = 0
    for object in object_list:
        dist += util.manhattanDistance(pos, object)
    return dist


def total_distance_from_list(pos, object_list):
    totalDistance = 0
    pos = pos, 0
    while not len(object_list) == 0:
        pos = find_min_and_remove(pos, object_list)
        totalDistance += pos[1]
    return totalDistance


def find_min_and_remove(pos, foodList):
    """
    helper function
    returns the node with the minumum distance from pos and its distance
    also removes node from list
    """

    minDist = 999999
    nodeToRemove = ()

    for food in foodList:
        dist = abs(pos[0][0] - food[0]) + abs(pos[0][1] - food[1])
        if dist < minDist:
            minDist = dist
            nodeToRemove = food

    foodList.remove(nodeToRemove)
    return nodeToRemove, minDist


def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    ans = currentGameState.getScore()
    print(ans)
    return ans


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          Directions.STOP:
            The stop direction, which is always legal

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """

        action, score = self.get_action(gameState, 0, self.depth)
        return action

    def get_action(self, game_state, agent, depth):
        actions = game_state.getLegalActions(agent)
        actions = [action for action in actions if action != Directions.STOP]

        action_scores = []
        for action in actions:
            new_state = game_state.generateSuccessor(agent, action)

            if new_state.isWin() or new_state.isLose():
                action_scores.append((action, self.evaluationFunction(new_state)))
                continue
            if agent != game_state.getNumAgents() - 1:
                result = self.get_action(new_state, agent + 1, depth)
                action_scores.append((action, result[1]))
            else:
                if depth != 1:
                    result = self.get_action(new_state, 0, depth - 1)
                    action_scores.append((action, result[1]))
                else:
                    action_scores.append((action, self.evaluationFunction(new_state)))

        return get_agent_action(agent, action_scores)


def get_agent_action(agent, action_scores):
    if agent == 0:
        best_score = max(score[1] for score in action_scores)
    else:
        best_score = min(score[1] for score in action_scores)
    best_actions = [action_score for action_score in action_scores if action_score[1] == best_score]
    return best_actions[0]


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        action_score = self.get_action(gameState, 0, float('-inf'), float('inf'), self.depth)
        return action_score[0]

    def get_action(self, game_state, agent, alpha, beta, depth):
        actions = game_state.getLegalActions(agent)
        actions = [action for action in actions if action != Directions.STOP]

        action_scores = []
        for action in actions:
            new_state = game_state.generateSuccessor(agent, action)

            if new_state.isWin() or new_state.isLose():
                score = self.evaluationFunction(new_state)
            else:
                if agent != game_state.getNumAgents() - 1:
                    result = self.get_action(new_state, agent + 1, alpha, beta, depth)
                    score = result[1]
                else:
                    if depth != 1:
                        result = self.get_action(new_state, 0, alpha, beta, depth - 1)
                        score = result[1]
                    else:
                        score = self.evaluationFunction(new_state)

            if agent == 0:
                alpha = max(alpha, score)
                action_scores.append((action, alpha))
                if alpha >= beta:
                    return action, alpha
            else:
                beta = min(beta, score)
                action_scores.append((action, beta))
                if beta <= alpha:
                    return action, beta

        return get_agent_action(agent, action_scores)


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction


class ContestAgent(MultiAgentSearchAgent):
    """
      Your agent for the mini-contest
    """

    def getAction(self, gameState):
        """
          Returns an action.  You can use any method you want and search to any depth you want.
          Just remember that the mini-contest is timed, so you have to trade off speed and computation.

          Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
          just make a beeline straight towards Pacman (or away from him if they're scared!)
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

