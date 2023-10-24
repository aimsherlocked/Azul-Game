from template import GameState, GameRule, Agent

import random
import numpy
import copy
import Azul.azul_utils as utils


class AzulState(GameState):
    NUM_FACTORIES = [5,7,9]
    NUM_TILE_TYPE = 20
    NUM_ON_FACTORY = 4


    class TileDisplay:
        def __init__(self):
            # Map between tile colour and number in the display
            self.tiles = {}

            # Total number of tiles in the display
            self.total = 0

            for tile in utils.Tile:
                self.tiles[tile] = 0

        def ReactionTiles(self, number, tile_type):
            assert number > 0
            assert tile_type in utils.Tile
            assert tile_type in self.tiles

            self.tiles[tile_type] -= number
            self.total -= number

            assert self.tiles[tile_type] >= 0
            assert self.total >= 0

        def AddTiles(self, number, tile_type):
            assert number > 0
            assert tile_type in utils.Tile
            assert tile_type in self.tiles
            
            self.tiles[tile_type] += number
            self.total += number


    class AgentState:
        GRID_SIZE = 5
        FLOOR_SCORES = [-1,-1,-2,-2,-2,-3,-3]
        ROW_BONUS = 2
        COL_BONUS = 7
        SET_BONUS = 10

        def __init__(self, _id):
            self.id = _id
            self.score = 0
            self.lines_number = [0]*self.GRID_SIZE
            self.lines_tile = [-1]*self.GRID_SIZE

            self.agent_trace = utils.AgentTrace(_id)

            #self.grid_scheme = [
            #    [Tile.BLUE,Tile.YELLOW,Tile.RED,Tile.BLACK,Tile.WHITE],
            #    [Tile.WHITE,Tile.BLUE,Tile.YELLOW,Tile.RED,Tile.BLACK],
            #    [Tile.BLACK,Tile.WHITE,Tile.BLUE,Tile.YELLOW,Tile.RED],
            #    [Tile.RED,Tile.BLACK,Tile.WHITE,Tile.BLUE,Tile.YELLOW],
            #    [Tile.YELLOW,Tile.RED,Tile.BLACK,Tile.WHITE,Tile.BLUE]
            #]
            self.grid_scheme = numpy.zeros((self.GRID_SIZE,self.GRID_SIZE))
            self.grid_scheme[0][utils.Tile.BLUE] = 0
            self.grid_scheme[1][utils.Tile.BLUE] = 1
            self.grid_scheme[2][utils.Tile.BLUE] = 2
            self.grid_scheme[3][utils.Tile.BLUE] = 3
            self.grid_scheme[4][utils.Tile.BLUE] = 4

            self.grid_scheme[1][utils.Tile.WHITE] = 0
            self.grid_scheme[2][utils.Tile.WHITE] = 1
            self.grid_scheme[3][utils.Tile.WHITE] = 2
            self.grid_scheme[4][utils.Tile.WHITE] = 3 
            self.grid_scheme[0][utils.Tile.WHITE] = 4
            
            self.grid_scheme[2][utils.Tile.BLACK] = 0 
            self.grid_scheme[3][utils.Tile.BLACK] = 1
            self.grid_scheme[4][utils.Tile.BLACK] = 2
            self.grid_scheme[0][utils.Tile.BLACK] = 3
            self.grid_scheme[1][utils.Tile.BLACK] = 4

            self.grid_scheme[3][utils.Tile.RED] = 0
            self.grid_scheme[4][utils.Tile.RED] = 1
            self.grid_scheme[0][utils.Tile.RED] = 2
            self.grid_scheme[1][utils.Tile.RED] = 3
            self.grid_scheme[2][utils.Tile.RED] = 4

            self.grid_scheme[4][utils.Tile.YELLOW] = 0
            self.grid_scheme[0][utils.Tile.YELLOW] = 1
            self.grid_scheme[1][utils.Tile.YELLOW] = 2
            self.grid_scheme[2][utils.Tile.YELLOW] = 3
            self.grid_scheme[3][utils.Tile.YELLOW] = 4

            # Matrix representing state of the agent's grid (ie. which
            # slots have tiles on them -- 1s -- and which don't -- 0s).
            self.grid_state = numpy.zeros((self.GRID_SIZE,self.GRID_SIZE))

            # State of the agent's floor line, a 1 indicates there is
            # a tile sitting in that position in their floor line.
            self.floor = [0,0,0,0,0,0,0]
            self.floor_tiles = []

            # Record of the number of tiles of each colour the agent
            # has placed in their grid (useful for end-game scoring)
            self.number_of = {}
            for tile in utils.Tile:
                self.number_of[tile] = 0


        # Add given tiles to the agent's floor line. After calling this 
        # method, 'tiles' will contain tiles that could not be added to
        # the agent's floor line.
        def AddToFloor(self, tiles):
            number = len(tiles)
            for i in range(len(self.floor)):
                if self.floor[i] == 0:
                    self.floor[i] = 1
                    tt = tiles.pop(0)
                    self.floor_tiles.append(tt)
                    number -= 1
                if number == 0:
                    break

        # Add given number of given tile type to the specified pattern line
        def AddToPatternLine(self, line, number, tile_type):
            assert line >= 0 and line < self.GRID_SIZE

            assert (self.lines_tile[line] == -1 or 
                self.lines_tile[line] == tile_type)

            self.lines_number[line] += number
            self.lines_tile[line] = tile_type

            assert self.lines_number[line] <= line + 1 


        # Assign first agent token to this agent
        def GiveFirstAgentToken(self):
            for i in range(len(self.floor)):
                if self.floor[i] == 0:
                    self.floor[i] = 1
                    break

        # Compute number of completed rows in the agent's grid
        def GetCompletedRows(self):
            completed = 0
            for i in range(self.GRID_SIZE):
                allin = True
                for j in range(self.GRID_SIZE):
                    if self.grid_state[i][j] == 0:
                        allin = False
                        break
                if allin:
                    completed += 1
            return completed

        # Compute number of completed columns in the agent's grid
        def GetCompletedColumns(self):
            completed = 0
            for i in range(self.GRID_SIZE):
                allin = True
                for j in range(self.GRID_SIZE):
                    if self.grid_state[j][i] == 0:
                        allin = False
                        break
                if allin:
                    completed += 1
            return completed

        # Compute the number of completed tile sets in the agent's grid
        def GetCompletedSets(self):
            completed = 0
            for tile in utils.Tile:
                if self.number_of[tile] == self.GRID_SIZE:
                    completed += 1
            return completed
            
        # Complete scoring process for agent at round end: 
        # 1. Action tiles across from pattern lines to the grid and score each;
        #
        # 2. Clear remaining tiles on pattern lines (where appropriate) and
        # return to be added to "used" tiles bag;
        #
        # 3. Score penalties for tiles in floor line and return these tiles
        # to be added to the "used" tiles bag.
        #
        # Returns a pair: the change in the agent's score; and the set of 
        # tiles to be returned to the "used" tile bag. The agents internal
        # representation of their score is updated in the process. 
        def ScoreRound(self):
            used_tiles = []

            score_inc = 0

            # 1. Action tiles across from pattern lines to the wall grid
            for i in range(self.GRID_SIZE):
                # Is the pattern line full? If not it persists in its current
                # state into the next round.
                if self.lines_number[i] == i+1:
                    tc = self.lines_tile[i]
                    col = int(self.grid_scheme[i][tc])

                    # Record that the agent has placed a tile of type 'tc'
                    self.number_of[tc] += 1

                    # Clear the pattern line, add all but one tile into the
                    # used tiles bag. The last tile will be placed on the 
                    # agents wall grid.  
                    for j in range(i):
                        used_tiles.append(tc)

                    self.lines_tile[i] = -1
                    self.lines_number[i] = 0

                    # Tile will be placed at position (i,col) in grid
                    self.grid_state[i][col] = 1

                    # count the number of tiles in a continguous line
                    # above, below, to the left and right of the placed tile.
                    above = 0
                    for j in range(col-1, -1, -1):
                        val = self.grid_state[i][j]
                        above += val
                        if val == 0:
                            break
                    below = 0
                    for j in range(col+1,self.GRID_SIZE,1):
                        val = self.grid_state[i][j]
                        below +=  val
                        if val == 0:
                            break
                    left = 0
                    for j in range(i-1, -1, -1):
                        val = self.grid_state[j][col]
                        left += val
                        if val == 0:
                            break
                    right = 0
                    for j in range(i+1, self.GRID_SIZE, 1):
                        val = self.grid_state[j][col]
                        right += val
                        if val == 0:
                            break

                    # If the tile sits in a contiguous vertical line of 
                    # tiles in the grid, it is worth 1*the number of tiles
                    # in this line (including itself).
                    if above > 0 or below > 0:
                        score_inc += (1 + above + below)

                    # In addition to the vertical score, the tile is worth
                    # an additional H points where H is the length of the 
                    # horizontal contiguous line in which it sits.
                    if left > 0 or right > 0:
                        score_inc += (1 + left + right)

                    # If the tile is not next to any already placed tiles
                    # on the grid, it is worth 1 point.                
                    if above == 0 and below == 0 and left == 0 \
                        and right == 0:
                        score_inc += 1

            # Score penalties for tiles in floor line
            penalties = 0
            for i in range(len(self.floor)):
                penalties += self.floor[i]*self.FLOOR_SCORES[i]
                self.floor[i] = 0
                
            used_tiles.extend(self.floor_tiles)
            self.floor_tiles = []
            
            # Agents cannot be assigned a negative score in any round.
            score_change = score_inc + penalties
            if score_change < 0 and self.score < -score_change:
                score_change = -self.score
            
            self.score += score_change
            self.agent_trace.round_scores[-1] = score_change

            return (self.score, used_tiles) 

        # Complete additional end of game scoring (add bonuses). Return
        # computed bonus, and add to internal score representation.
        def EndOfGameScore(self):
            rows = self.GetCompletedRows()
            cols = self.GetCompletedColumns()
            sets = self.GetCompletedSets()

            bonus = (rows * self.ROW_BONUS) + (cols * self.COL_BONUS) + \
                (sets * self.SET_BONUS)

            self.agent_trace.bonuses = bonus
            self.score += bonus
            return bonus 


    def __init__(self, num_agents):
        # Create agent states
        self.agents = []
        for i in range(num_agents):
            ps = self.AgentState(i)
            self.agents.append(ps)
            
        # Tile bag contains NUM_TILE_TYPE of each tile colour
        self.bag = []
        for i in range(self.NUM_TILE_TYPE):
            self.bag.append(utils.Tile.BLUE)
            self.bag.append(utils.Tile.YELLOW)
            self.bag.append(utils.Tile.RED)
            self.bag.append(utils.Tile.BLACK)
            self.bag.append(utils.Tile.WHITE)

        # Shuffle contents of tile bag
        random.shuffle(self.bag)

        # "Used" bag is initial empty
        self.bag_used = []

        # In a 2/3/4-agent game, 5/7/9 factory displays are used
        self.factories = []
        for i in range(self.NUM_FACTORIES[num_agents-2]):
            td = self.TileDisplay()
            
            # Initialise factory display: add NUM_ON_FACTORY randomly
            # drawn tiles to the factory (if available). 
            self.InitialiseFactory(td)
            self.factories.append(td)

        self.centre_pool = self.TileDisplay()
        self.first_agent_taken = False
        self.first_agent = random.randrange(num_agents)
        self.next_first_agent = -1


    def TilesRemaining(self):
        if self.centre_pool.total > 0:
            return True
        for fac in self.factories:
            if fac.total > 0:
                return True
        return False

    # Place tiles from the main bag (and used bag if the main bag runs
    # out of tiles) onto the given factory display.
    def InitialiseFactory(self, factory):
        # Reset contents of factory display
        factory.total = 0
        for tile in utils.Tile:
            factory.tiles[tile] = 0

        # If there are < NUM_ON_FACTORY tiles in the bag, shuffle the 
        # tiles in the "used" bag and add them to the main bag (we still
        # want the tiles that were left in the main bag to be drawn first).
        # Fill the factory display with tiles, up to capacity, if possible.
        # If there are less than NUM_ON_FACTORY tiles available in both
        # bags, the factory will be left at partial capacity.
        if len(self.bag) < self.NUM_ON_FACTORY and len(self.bag_used) > 0:
            random.shuffle(self.bag_used)
            self.bag.extend(self.bag_used)
            self.bag_used = []

        for i in range(min(self.NUM_ON_FACTORY,len(self.bag))):
            # take tile out of the bag
            tile = self.bag.pop(0)
            factory.tiles[tile] += 1
            factory.total += 1

    # Execute end of round actions (scoring and clean up)
    def ExecuteEndOfRound(self):
        # Each agent scores for the round, and we add tiles to the 
        # used bag (if appropriate).
        for plr in self.agents:
            _,used = plr.ScoreRound()
            self.bag_used.extend(used)


class AzulGameRule(GameRule):
    def __init__(self,num_of_agent):
        super().__init__(num_of_agent)
        self.private_information = None # Azul is a perfect-information game.
        
    def validAction(self, m, actions):
        return utils.ValidAction(m, actions)

    def initialGameState(self):
        self.current_agent_index = self.num_of_agent
        return AzulState(self.num_of_agent)

    def generateSuccessor(self, state, action, agent_id):
        if action == "ENDROUND":
            for plr in state.agents:
                _,used = plr.ScoreRound()
                state.bag_used.extend(used)

            state.first_agent_taken = False
            state.first_agent = state.next_first_agent
            state.next_first_agent = -1
        elif action == "STARTROUND":
            for plr in state.agents:
                plr.agent_trace.StartRound()
            for fd in state.factories:
                state.InitialiseFactory(fd)

            for tile in utils.Tile:
                state.centre_pool.tiles[tile] = 0
        else:
            plr_state = state.agents[agent_id]
            plr_state.agent_trace.actions[-1].append(action)

            # The agent is taking tiles from the centre
            if action[0] == utils.Action.TAKE_FROM_CENTRE: 
                tg = action[2]

                if not state.first_agent_taken:
                    plr_state.GiveFirstAgentToken()
                    state.first_agent_taken = True
                    state.next_first_agent = agent_id

                if tg.num_to_floor_line > 0:
                    ttf = []
                    for i in range(tg.num_to_floor_line):
                        ttf.append(tg.tile_type)
                    plr_state.AddToFloor(ttf)
                    state.bag_used.extend(ttf)

                if tg.num_to_pattern_line > 0:
                    plr_state.AddToPatternLine(tg.pattern_line_dest, 
                        tg.num_to_pattern_line, tg.tile_type)

                # Reaction tiles from the centre
                state.centre_pool.ReactionTiles(tg.number, tg.tile_type)

            elif action[0] == utils.Action.TAKE_FROM_FACTORY:
                tg = action[2]
                if tg.num_to_floor_line > 0:
                    ttf = []
                    for i in range(tg.num_to_floor_line):
                        ttf.append(tg.tile_type)
                    plr_state.AddToFloor(ttf)
                    state.bag_used.extend(ttf)

                if tg.num_to_pattern_line > 0:
                    plr_state.AddToPatternLine(tg.pattern_line_dest, 
                        tg.num_to_pattern_line, tg.tile_type)

                # Reaction tiles from the factory display
                fid = action[1]
                fac = state.factories[fid]
                fac.ReactionTiles(tg.number,tg.tile_type)

                # All remaining tiles on the factory display go into the 
                # centre!
                for tile in utils.Tile:
                    num_on_fd = fac.tiles[tile]
                    if num_on_fd > 0:
                        state.centre_pool.AddTiles(num_on_fd, tile)
                        fac.ReactionTiles(num_on_fd, tile)
        return state
    
    def getNextAgentIndex(self):
        if not self.current_game_state.TilesRemaining():
            return self.num_of_agent
        if self.current_agent_index == self.num_of_agent:
            return self.current_game_state.first_agent
        return (self.current_agent_index + 1) % self.num_of_agent

    def gameEnds(self):
        for plr_state in self.current_game_state.agents:
            completed_rows = plr_state.GetCompletedRows()
            if completed_rows > 0:
                return True
        return False

    def calScore(self, game_state,agent_id):
        game_state.agents[agent_id].EndOfGameScore()
        return game_state.agents[agent_id].score

    def getLegalActions(self, game_state, agent_id):
        actions = []

        if not game_state.TilesRemaining() and not game_state.next_first_agent == -1:
            return ["ENDROUND"]
        elif agent_id == self.num_of_agent:
            return ["STARTROUND"]
        else: 
            agent_state = game_state.agents[agent_id]

            # Look at each factory display with available tiles
            fid = 0
            for fd in game_state.factories:
                # Look at each available tile set
                for tile in utils.Tile:
                    num_avail = fd.tiles[tile]
                
                    if num_avail == 0:
                        continue

                    # A agent can always take tiles, as they can be 
                    # added to their floor line (if their floor line is 
                    # full, the extra tiles are placed in the used bag).

                    # First look through each pattern line, create actions 
                    # that place the tiles in each appropriate line (with
                    # those that cannot be placed added to the floor line).
                    for i in range(agent_state.GRID_SIZE):
                        # Can tiles be added to pattern line i?
                        if agent_state.lines_tile[i] != -1 and \
                            agent_state.lines_tile[i] != tile:
                            # these tiles cannot be added to this pattern line
                            continue

                        # Is the space on the grid for this tile already
                        # occupied?
                        grid_col = int(agent_state.grid_scheme[i][tile])
                        if agent_state.grid_state[i][grid_col] == 1:
                            # It is, so we cannot place this tile type
                            # in this pattern line!
                            continue

                        slots_free = (i+1) - agent_state.lines_number[i]
                        tg = utils.TileGrab()
                        tg.number = num_avail
                        tg.tile_type = tile
                        tg.pattern_line_dest = i
                        tg.num_to_pattern_line = min(num_avail, slots_free)
                        tg.num_to_floor_line = tg.number - tg.num_to_pattern_line

                        actions.append((utils.Action.TAKE_FROM_FACTORY, fid, tg))
            
                    # Default action is to place all the tiles in the floor line
                    tg = utils.TileGrab()
                    tg.number = num_avail
                    tg.tile_type = tile
                    tg.num_to_floor_line = tg.number
                    actions.append((utils.Action.TAKE_FROM_FACTORY, fid, tg))

                fid += 1    

            # Alternately, the agent could take tiles from the centre pool.
            # Note that we do not include the first agent token in the 
            # collection of tiles recorded in each utils.TileGrab. This is managed
            # by the game running class. 
            for tile in utils.Tile:
                # Number of tiles of this type in the centre
                num_avail = game_state.centre_pool.tiles[tile]

                if num_avail == 0:
                    continue

                # First look through each pattern line, create actions 
                # that place the tiles in each appropriate line (with
                # those that cannot be placed added to the floor line).
                for i in range(agent_state.GRID_SIZE):
                    # Can tiles be added to pattern line i?
                    if agent_state.lines_tile[i] != -1 and \
                        agent_state.lines_tile[i] != tile:
                        # these tiles cannot be added to this pattern line
                        continue

                    # Is the space on the grid for this tile already
                    # occupied?
                    grid_col = int(agent_state.grid_scheme[i][tile])
                    if agent_state.grid_state[i][grid_col] == 1:
                        # It is, so we cannot place this tile type
                        # in this pattern line!
                        continue

                    slots_free = (i+1) - agent_state.lines_number[i]
                    tg = utils.TileGrab()
                    tg.number = num_avail
                    tg.tile_type = tile
                    tg.pattern_line_dest = i
                    tg.num_to_pattern_line = min(num_avail, slots_free)
                    tg.num_to_floor_line = tg.number - tg.num_to_pattern_line

                    actions.append((utils.Action.TAKE_FROM_CENTRE, -1, tg))
            
                # Default action is to place all the tiles in the floor line
                tg = utils.TileGrab()
                tg.number = num_avail
                tg.tile_type = tile
                tg.num_to_floor_line = tg.number
                actions.append((utils.Action.TAKE_FROM_CENTRE, -1, tg))

            return actions
