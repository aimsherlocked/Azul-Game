from template import Agent
import random, time
from Azul.azul_model import AzulGameRule as GameRule
from copy import deepcopy
from collections import deque
from Azul.azul_utils import *

THINKTIME = 0.9
NUM_PLAYERS = 2
DISCOUNT_FACTOR = 0.8
EPSILON = 0.6

class myAgent(Agent):
    def __init__(self, _id):
        self.id = _id
        self.count = 0
        self.game_rule = GameRule(NUM_PLAYERS)
    
    def GetActions(self, state, _id):
        actions = self.game_rule.getLegalActions(state, _id)
        if not actions:
            actions = self.game_rule.getLegalActions(state, NUM_PLAYERS)
        return actions
    
    def DoAction(self, state, action, _id):
        if action == "ENDROUND":
            state.next_first_agent = self.id
        state = self.game_rule.generateSuccessor(state, action, _id)

    def GetScore(self, state, _id):
        return self.game_rule.calScore(state, _id)
    
    def GameOver(self, state):
        for plr_state in state.agents:
            completed_rows = plr_state.GetCompletedRows()
            if completed_rows > 0:
                return True
        return False
    
    def TransformState(self, state, _id):
        return AgentToString(_id, state.agents[_id]) + BoardToString(state)
    
    def ActionInList(self, action, action_list):
        if isinstance(action, str):
            return action in action_list
        else:
            return ValidAction(action, action_list)
    
    def SelectAction(self, actions, game_state):
        start_time = time.time()
        self.count += 1

        best_action = random.choice(actions)
        optional_actions = []
        for action in actions:
            if not isinstance(action, str):
                if action[2].num_to_floor_line == 0:
                    optional_actions.append(action)
                elif best_action[2].num_to_floor_line > action[2].num_to_floor_line:
                    best_action = action
        if optional_actions:
            best_action = random.choice(optional_actions)
            matched_line = -1

            for action in optional_actions:
                current_line = action[2].pattern_line_dest
                if current_line >= 0 and game_state.agents[self.id].lines_number[current_line] + action[2].num_to_pattern_line == current_line + 1:
                    matched_line = max(matched_line, current_line)
                    best_action = action
        if self.count <= 25:
            return best_action
        else:
            #MCT
            v_state = dict()
            best_act_state = dict()
            expanded_act_state = dict()
            tsf_r_state = self.TransformState(game_state, self.id)
            count = 0

            def FullyExpanded(tsf_state, actions):
                if tsf_state in expanded_act_state:
                    available_actions = []
                    for action in actions:
                        if not self.ActionInList(action, expanded_act_state[tsf_state]):
                            available_actions.append(action)
                    return available_actions
                else:
                    return actions
                
            while time.time() - start_time < THINKTIME:
                count += 1
                state = deepcopy(game_state)
                new_actions = actions
                tsf_crt_state = tsf_r_state
                queue = deque([])
                reward = 0
                tsf_crt_state = self.TransformState(state, self.id)

                #Selection
                while not FullyExpanded(tsf_crt_state, new_actions) and not self.GameOver(state):
                    if time.time() - start_time >= THINKTIME:
                        return best_action
                    tsf_crt_state = self.TransformState(state, self.id)
                    if (random.uniform(0,1) < EPSILON) and (tsf_crt_state in best_act_state) and (self.ActionInList(best_act_state[tsf_crt_state], new_actions)):
                        crt_action = best_act_state[tsf_crt_state]
                    else:
                        crt_action = random.choice(new_actions)

                    queue.append((tsf_crt_state, crt_action))

                    next_state = deepcopy(state)
                    self.DoAction(next_state,crt_action, self.id)
                    tsf_crt_state = self.TransformState(state, self.id)
                    new_actions = self.GetActions(next_state, self.id)
                    state = next_state

                #Expandsion
                tsf_crt_state = self.TransformState(state, self.id)
                available_actions = FullyExpanded(tsf_crt_state, new_actions)
                if not available_actions:
                    continue
                else:
                    action = random.choice(available_actions)
                if tsf_crt_state in expanded_act_state:
                    expanded_act_state[tsf_crt_state].append(action)
                else:
                    expanded_act_state[tsf_crt_state] = [action]
                queue.append((tsf_crt_state, action))
                next_state = deepcopy(state)
                self.DoAction(next_state, action, self.id)
                new_actions = self.GetActions(next_state, self.id)
                state = next_state

                #Simulation
                length = 0
                while not self.GameOver(state):
                    length += 1
                    if time.time() - start_time >= THINKTIME:
                        return best_action
                    crt_action = random.choice(new_actions)
                    tsf_crt_state = self.TransformState(state, self.id)
                    next_state = deepcopy(state)
                    self.DoAction(next_state, crt_action, self.id)
                    new_actions = self.GetActions(next_state, self.id)
                    state = next_state
                reward = self.GetScore(state, self.id)

                #Back Propagatation
                crt_value = reward * (DISCOUNT_FACTOR ** length)
                while queue and time.time() - start_time < THINKTIME:
                    tsf_state, crt_action = queue.pop()
                    if tsf_state in v_state:
                        if crt_value > v_state[tsf_state]:
                            v_state[tsf_state] = crt_value
                            best_act_state[tsf_state] = crt_action
                    else:
                        v_state[tsf_state] = crt_value
                        best_act_state[tsf_state] = crt_action
                    crt_value *= DISCOUNT_FACTOR

        return best_action