# INFORMATION -------------------------------------------------------------------------- #
# This is a bfs agent based on the example_bfs provided by the teaching team.
# This agent uses the structure of the example_bfs, with modifications on the goal state 
# and actions returned when no goal was found in the time limit.

import time, random, copy
from Azul.azul_model import AzulGameRule as GameRule
from copy import deepcopy
from collections import deque

THINKTIME   = 0.9
NUM_PLAYERS = 2

# Defines this agent.
class myAgent():
    def __init__(self, _id):
        self.id = _id 
        self.game_rule = GameRule(NUM_PLAYERS) 

    # Generates actions from current state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)
    
    # Carry out a given action on this state and return True if goal is reached received.
    def DoAction(self, state, action):
        old_state = copy.deepcopy(state)
        old_score = old_state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        
        # goal: score is higher after action applied, and the number of floor line blocks are controlled
        goal_reached = False 
        if state.agents[self.id].score > old_score:
            if not isinstance(action, str) and action.tg.num_to_floor_line < 2:
                goal_reached = True
        return goal_reached

    # perform bfs within time limit.
    # Return the first action that leads to goal, if any was found.
    def SelectAction(self, actions, rootstate):
        start_time = time.time()
        queue      = deque([ (deepcopy(rootstate),[]) ]) # Initialise queue. First node = root state and an empty path.
        
        # Conduct BFS starting from rootstate.
        while len(queue) and time.time()-start_time < THINKTIME:
            state, path = queue.popleft()
            new_actions = self.GetActions(state)
            
            for a in new_actions:
                next_state = deepcopy(state)
                next_path  = path + [a]
                goal     = self.DoAction(next_state, a)
                if goal:
                    return next_path[0]
                else:
                    queue.append((next_state, next_path)) 
        
        return actions[0] #If no goal was found in the time limit
        
# python3 general_game_runner.py -g Azul -a agents.t_030.ASTAR,agents.t_030.BFS