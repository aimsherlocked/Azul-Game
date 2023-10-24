# INFORMATION ------------------------------------------------------------------------------------------------------- #

# Author:  Steven Spratley
# Date:    04/01/2021
# Purpose: Implements an example breadth-first search agent for the COMP90054 competitive game environment.

# Modify: change bfs to A* algorithm


import agents.t_030.myutil as myutil
import time, random
from Azul.azul_model import AzulGameRule as GameRule
from copy import deepcopy
from collections import Counter

THINKTIME   = 0.9
NUM_PLAYERS = 2

# Defines this agent.
class myAgent():
    def __init__(self, _id):
        self.id = _id
        self.game_rule = GameRule(NUM_PLAYERS)

    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)

    #Calculate the grid score
    #reference: azul_model.py
    def gridScore(self, next_state, i):

        score_inc = 0
        cur_agent = next_state.agents[self.id]

        tc = cur_agent.lines_tile[i]
        col = int(cur_agent.grid_scheme[i][tc])

        if cur_agent.lines_number[i] == i + 1:
        # count the number of tiles in a contiguous line
        # above, below, to the left and right of the placed tile.
            above = 0
            for j in range(col - 1, -1, -1):
                val = cur_agent.grid_state[i][j]
                above += val
                if val == 0:
                    break
            below = 0
            for j in range(col + 1, cur_agent.GRID_SIZE, 1):
                val = cur_agent.grid_state[i][j]
                below += val
                if val == 0:
                    break
            left = 0
            for j in range(i - 1, -1, -1):
                val = cur_agent.grid_state[j][col]
                left += val
                if val == 0:
                    break
            right = 0
            for j in range(i + 1, cur_agent.GRID_SIZE, 1):
                val = cur_agent.grid_state[j][col]
                right += val
                if val == 0:
                    break

            # If the tile sits in a contiguous vertical line of
            # tiles in the grid, it is worth 1*the number of tiles
            # in this line (including itself)
            if above > 0 or below > 0:
                score_inc += (1 + above + below)

            # In addition to the vertical score, the tile is worth
            # an additional H points where H is the length of the
            # horizontal contiguous line in which it sits.
            if left > 0 or right > 0:
                score_inc += (1 + left + right)

        penalties = 0
        for floor_i in range(len(cur_agent.floor)):
            penalties += cur_agent.floor[floor_i] * cur_agent.FLOOR_SCORES[floor_i]

        return score_inc, penalties

    # calculate the score of action. -left unfilled-floor+potential score in grid
    def get_h_value (self, state, action):

        next_state = deepcopy(state)

        #action is string when start and end
        if (action != "STARTROUND") and (action != "ENDROUND"):

            line_num = action[2].pattern_line_dest # action acts on line number(th) line
            delta_unfilled = (line_num + 1 - action[2].num_to_pattern_line) #number of unfilled in the line
            score_inc, penalties = self.gridScore(next_state,line_num) #get the score and penalties

            # reward for action not fill the line but supplement the existing line
            reward_same_line=0
            if state.agents[self.id].lines_number[line_num] != action[2].num_to_pattern_line:
                reward_same_line = 5

            #h value equal to unfilled blocks in the line + grid score + floor penalty + reward of supplement the line
            h_value = -delta_unfilled + score_inc + penalties + reward_same_line

            return h_value

        return 0

    # return True if current state is one of the goals
    def is_goal(self, state):

        cur_state = deepcopy(state)
        line_tile = [tile for tile in cur_state.agents[self.id].lines_tile if tile != -1] #line which has the tile
        tile_category = Counter(line_tile).keys() #line which has unique tile

        #at least one of the line is fulfilled and no tiles on the floor
        for i in range(5):
            if cur_state.agents[self.id].lines_number[i] == i + 1 and cur_state.agents[self.id].floor[0] == 0:
                return True

        # only one pattern in the lines and at least one of line is fulfilled and grid score + floor penalty greater than 0
        for i in range(5):
            if len(line_tile) == len(tile_category) and state.agents[self.id].lines_number[i] == i + 1:
                score_inc, penalties = self.gridScore(state, i)
                return score_inc + penalties > 0

        #when no tiles in the centre and factory, the score of my agent is higher than the score of opponent
        score_self = cur_state.agents[self.id].score #self score
        score_opp = cur_state.agents[-self.id + 1].score #opponent score
        if score_self > score_opp and all(i == 0 for i in state.centre_pool.tiles.values())\
                and all(j == 0 for i in state.factories for j in i.tiles.values()):
            return True

        #base case of the goal: no line is empty
        for i in range(5):
            if cur_state.agents[self.id].lines_number[i] > 0:
                return True

        return False


    # Take a list of actions and an initial state, and perform breadth-first search within a time limit.
    # Return the first action that leads to goal, if any was found.
    def SelectAction(self, actions, rootstate):
        start_time = time.time()
        queue      = myutil.PriorityQueue()
        start_node = (deepcopy(rootstate),[],0)
        queue.push(start_node,0) # node consists of state, path and cost
        visited = set() # visited states
        best_g = dict()

        # Conduct modified A* starting from rootstate.
        while not queue.isEmpty() and time.time() - start_time < THINKTIME:
            node = queue.pop() # Pop the next node
            state, path, cost = node

            if (not state in visited) or cost < best_g.get(state):
                new_actions = self.GetActions(state)  # Obtain new actions available to the agent in this state.
                visited.add(state) #add state to visited list
                best_g[state] = cost

                if self.is_goal(state) and path:
                    return path[0]  # If the current action reached the goal, return the initial action that led there.
                for a in new_actions:
                    next_path = path + [a] # add this action to the path.
                    next_state = self.game_rule.generateSuccessor(deepcopy(state), a, self.id) #get next successor
                    h_value = self.get_h_value(next_state,a)
                    queue.push((next_state, next_path, cost+1),cost+1-h_value) # add state and path to the queue.

        return path[0] # If no goal was found in the time limit, return a random action.


# END FILE -----------------------------------------------------------------------------------------------------------#