from template import Displayer
from Azul.azul_utils import *
import tkinter
import os
import copy
import time
import traceback

class BoardTile:
    def __init__(self,x,y,index):
        self.empty = True
        self.x = x
        self.y = y
        self.content = 7
        self.index = index

class BoardRow:
    def __init__(self,index):
        self.tiles = []
        if index == 0:
            self.tiles.append(BoardTile(154,3,0))
        elif index == 1:
            self.tiles.append(BoardTile(154,40,0))
            self.tiles.append(BoardTile(116,40,1))
        elif index == 2:
            self.tiles.append(BoardTile(154,78,0))
            self.tiles.append(BoardTile(116,78,1))
            self.tiles.append(BoardTile(78,78,2))
        elif index == 3:
            self.tiles.append(BoardTile(154,116,0))
            self.tiles.append(BoardTile(116,116,1))
            self.tiles.append(BoardTile(78,116,2))
            self.tiles.append(BoardTile(40,116,3))
        elif index == 4:
            self.tiles.append(BoardTile(154,155,0))
            self.tiles.append(BoardTile(116,155,1))
            self.tiles.append(BoardTile(78,155,2))
            self.tiles.append(BoardTile(40,155,3))
            self.tiles.append(BoardTile(2,155,4))
        elif index == 5:
            self.tiles.append(BoardTile(3,220,0))
            self.tiles.append(BoardTile(44,220,0))
            self.tiles.append(BoardTile(85,220,0))
            self.tiles.append(BoardTile(126,220,0))
            self.tiles.append(BoardTile(167,220,0))
            self.tiles.append(BoardTile(208,220,0))
            self.tiles.append(BoardTile(249,220,0))
        else:
            for x in range(5):
                self.tiles.append(BoardTile(211+38*x,38*(index-6)+3,x))
        


class AgentBoard:
    def __init__(self, agent_id, canvas, label):
        # Agent ID
        self.agent_id = agent_id
        self.agent_name = ""
        self.display_board = canvas 
        self.playing_board = []
        self.scoring_board = []
        self.naming = label
        
        for x in range(6):
            self.playing_board.append(BoardRow(x))
        
        for x in range(6,11):
            self.scoring_board.append(BoardRow(x))

class BoardFactory:
    def __init__(self,factory_id):
        self.id = factory_id
        self.factory_displayer = None
        self.tile_displayer = []
        self.tile_num = []
        self.tile_num_displayer = []




class GUIDisplayer(Displayer):
    def __init__(self, scale, delay=0.1):
        self.delay = delay

    def InitDisplayer(self,runner):
        self.root = tkinter.Tk()
        self.center_token = True
        self.root.title("AZUL ------ COMP90054 AI Planning for Autononmy")

        self.root.tk.call('wm', 'iconphoto', self.root._w, tkinter.PhotoImage(file='Azul/resources/azul_bpj_icon.png'))
        self.root.geometry("1300x700")
        # self.root.resizable(width=False, height=False)

        self.tile_images = []
        self.tile_images.append(tkinter.PhotoImage(file="Azul/resources/blue_tile_mini.png"))
        self.tile_images.append(tkinter.PhotoImage(file="Azul/resources/yellow_tile_mini.png"))
        self.tile_images.append(tkinter.PhotoImage(file="Azul/resources/red_tile_mini.png"))
        self.tile_images.append(tkinter.PhotoImage(file="Azul/resources/black_tile_mini.png"))
        self.tile_images.append(tkinter.PhotoImage(file="Azul/resources/white_tile_mini.png"))
        self.tile_images.append(tkinter.PhotoImage(file="Azul/resources/start_tile_mini.png"))
        self.tile_images.append(tkinter.PhotoImage(file="Azul/resources/penalty_tile_mini.png"))
        
        self.player_borad_img = tkinter.PhotoImage(file="Azul/resources/player_board_mini.png")
        self.m_img = tkinter.PhotoImage(file="Azul/resources/multiplication_mini.png")


        #factory
        self.fb_frame = tkinter.Frame(self.root)
        self.fb_frame.grid(row=0,column=0,sticky=tkinter.W+tkinter.E)

        self.board_factories = []
        self.ft_num = []
        for i in range(5):
            self.ft_num.append([tkinter.StringVar() for _ in range(5)])
        self.ft_num.append([tkinter.StringVar() for _ in range(6)])
        for row in self.ft_num:
            for var in row:
                var.set("0") 
        
        for i in range(5):
            factory = BoardFactory(i)
            factory.factory_displayer = tkinter.Frame(self.fb_frame,highlightbackground="black", highlightcolor="black", highlightthickness=3, borderwidth=2)
            factory.factory_displayer.grid(row=i,column=0)
            #factory.factory_displayer.grid_propagate(False)
            self._GenerateFactory(factory,i,5)
            self.board_factories.append(factory)
        self.cf_board = BoardFactory(6)
        self.cf_board.factory_displayer = tkinter.Frame(self.fb_frame,highlightbackground="black", highlightcolor="black", highlightthickness=3)
        self.cf_board.factory_displayer.grid(row=5,column=0)
        self._GenerateFactory(self.cf_board,5,6)

        
        #agent board
        self.pb_frame = tkinter.Frame(self.root)
        self.pb_frame.grid(row=0,column=1,sticky=tkinter.W+tkinter.E)

        self.player_board = []
        # assert(len(player_list) == 2)
        for i in range(2):
            name=tkinter.StringVar()
            name.set("Agent ("+str(i)+"): "+str(runner.agents_namelist[i])+"")
            pb1 = AgentBoard(i,tkinter.Canvas(self.pb_frame, width=405, height=265),tkinter.Entry(self.pb_frame, textvariable=name ,width=40))
            pb1.naming.grid(row=i*2,column=0)
            pb1.display_board.grid(row=i*2+1, column=0)
            pb1.display_board.create_image(0,0, anchor=tkinter.NW, image=self.player_borad_img) 

            self.player_board.append(pb1)
            

        #scoreboard
        self.sb_frame = tkinter.Frame(self.root)
        self.sb_frame.grid(row=0, column=2, sticky=tkinter.N+tkinter.E)

        self.scrollbar = tkinter.Scrollbar(self.sb_frame, orient=tkinter.VERTICAL)

        self.move_box=tkinter.Listbox(self.sb_frame,name="moves:", height=37, width=88, selectmode="single", borderwidth=4,yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.move_box.yview,troughcolor="white",bg="white")
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.move_box.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1)   
        # self.move_box.configure(exportselection=False)
        # self.move_box.configure(state=tkinter.DISABLED)

        # self.move_box.grid(row=0, column=3, rowspan=3, sticky=tkinter.N+tkinter.E)
        
        #self.fb_frame.grid_propagate(0)
        #self.root.grid_propagate(0)

        self.game_state_history=[]
        self.round_num = 0

    def _InsertState(self,text,game_state):
        text = text.replace("\n ","")
        self.game_state_history.append(copy.deepcopy(game_state))
        self.move_box.insert(tkinter.END,text)
        self.move_box.see(tkinter.END)
        self.move_box.selection_clear(0, last=None) 

    def _GenerateFactory(self,parent,index,size):
    
        for j in range(size):
            tf = tkinter.Frame(parent.factory_displayer,highlightbackground="grey", highlightcolor="grey", highlightthickness=2,borderwidth=2, width=39, height = 80)
            tf.grid(row=0,column=j)
            td = tkinter.Canvas(tf, width=35, height=35)
            td.create_image(0,0, anchor=tkinter.NW, image=self.tile_images[j]) 
            td.grid(row=0,column=0)
            m = tkinter.Canvas(tf, width=35, height=15)
            m.create_image(10,0, anchor=tkinter.NW, image=self.m_img) 
            m.grid(row=1,column=0)
            num = tkinter.Label(tf,textvariable=self.ft_num[index][j],borderwidth=4,relief=tkinter.SUNKEN)
            num.grid(row=2,column=0)

    def _UpdateFactory(self,game_state):
        inuses = [False] * 6

        #color
        for i in range(5):
            # tile num by factory
            for j in range(5):
                self.ft_num[j][i].set(str(game_state.factories[j].tiles[i]))
                if game_state.factories[j].tiles[i] > 0:
                    inuses[j] = True
            self.ft_num[5][i].set(str(game_state.centre_pool.tiles[i]))
            if game_state.centre_pool.tiles[i] > 0:
                inuses[-1] = True

        if game_state.next_first_agent!=-1:
            self.ft_num[5][5].set("0")
        else:
            self.ft_num[5][5].set("1")
        
        for i,inuse in enumerate(inuses[:-1]):
            if inuse:
                self.board_factories[i].factory_displayer.config(highlightbackground="red")
            else:
                self.board_factories[i].factory_displayer.config(highlightbackground="black")

        if inuses[-1]:
            self.cf_board.factory_displayer.config(highlightbackground="red")
        else:
            self.cf_board.factory_displayer.config(highlightbackground="black")

    def _UpdateLine(self,tile_num,play_board,line_id,tile_id):

        for i,tile in enumerate(play_board.playing_board[line_id].tiles):
            if not tile.empty:
                play_board.display_board.delete(tile.content)
                tile.empty = True
            if i < tile_num:
                tile.empty = False
                tile.content = play_board.display_board.create_image(tile.x,tile.y, anchor=tkinter.NW, image=self.tile_images[tile_id])
                play_board.display_board.update()
    
    def _UpdateScoringLine(self,play_board,index,cells):
        tt=0
        cc = 17 #circle center
        cs = 10 #circle size

        for x,(t,c) in enumerate(zip(play_board.scoring_board[index].tiles,cells)):
            if not t.empty:
                for content in t.content:
                    play_board.display_board.delete(content)
                t.empty = True

            if c != 0 and t.empty:
                t.empty = False
                tt = (5+x-index +1 ) % 5 - 1
                if tt < 0:
                    tt = tt + 5
                t.content = [
                    play_board.display_board.create_image(t.x,t.y, anchor=tkinter.NW, image=self.tile_images[tt]),
                    play_board.display_board.create_oval(t.x+cc-cs,t.y+cc-cs,t.x+cc+cs,t.y+cc+cs, fill = "lawn green")
                ]
                play_board.display_board.update()
    
    def _DisplayState(self,game_state):

        # update agent board one by one
        for _,(ps,pb) in enumerate(zip(game_state.agents,self.player_board)):

            # update playing board 
            for line_num in range(ps.GRID_SIZE):
                self._UpdateLine(ps.lines_number[line_num],pb,line_num,ps.lines_tile[line_num])
            
            # update floor line
            if game_state.next_first_agent != -1:
                self._UpdateLine(1,pb,5,5)
            else:
                 self._UpdateLine(0,pb,5,5)

            penalty = 0
            for i in ps.floor:
                if i == 1:
                    penalty = penalty + 1
            self._UpdateLine(penalty,pb,5,6)

            # update the scoring board

            for i in range(5):
                cells = [ps.grid_state[i][j] for j in range(5)]
                self._UpdateScoringLine(pb,i,cells)
        
        self._UpdateFactory(game_state)

    def StartRound(self,game_state):
        self._DisplayState(game_state)
        self.round_num = self.round_num +1
        self._InsertState("~~~~~~~~~~~~~~~Start of round: "+str(self.round_num)+"~~~~~~~~~~~~~~~",game_state)
        time.sleep(self.delay)

    def ExcuteAction(self,player_id,move, game_state):
        if move == "ENDROUND":
            self.EndRound(game_state)
        elif move == "STARTROUND":
            self.StartRound(game_state)
        else:
            movement = move[2]
            #print(movement.num_to_pattern_line)
            if movement.num_to_pattern_line > 0:
                self._UpdateLine(movement.num_to_pattern_line,self.player_board[player_id],movement.pattern_line_dest,movement.tile_type)

            if move[0] == 2 and self.center_token:
                self.center_token = False
                self._UpdateLine(1,self.player_board[player_id],5,5)

            if movement.num_to_floor_line > 0:
                self._UpdateLine(movement.num_to_floor_line,self.player_board[player_id],5,6)

            self._InsertState(ActionToString(player_id,move),game_state)

            self._UpdateFactory(game_state)
            
            time.sleep(self.delay)

    # this needed update
    def TimeOutWarning(self,runner,id):
        self._InsertState("Agent {} timed out. Assigning penalty {} out of {}. Choosing at random...".format(id, runner.warnings[id],runner.warning_limit),runner.game_rule.current_game_state)
        if id == 0:
            self.move_box.itemconfig(tkinter.END, {'bg':'red','fg':'blue'})
        else:
            self.move_box.itemconfig(tkinter.END, {'bg':'blue','fg':'yellow'})
        pass
    
    def IllegalWarning(self,runner,id,exception):
        self._InsertState("Agent {} requested illegal move, throwing exception: " +  str(repr(exception)) + ". Assigning penalty {} out of {}. Choosing at random...".format(id, runner.warnings[id],runner.warning_limit),runner.game_rule.current_game_state)
        if id == 0:
            self.move_box.itemconfig(tkinter.END, {'bg':'red','fg':'blue'})
        else:
            self.move_box.itemconfig(tkinter.END, {'bg':'blue','fg':'yellow'})
        pass    
    
    def EndRound(self,game_state):
        self.center_token = True
        self._DisplayState(game_state)
        self._InsertState("--------------End of round-------------",game_state)
        for i,plr_state in enumerate(game_state.agents):
            self._InsertState("Current score for Agent {}: {}".format(i,plr_state.score),game_state)
        time.sleep(self.delay)
        pass
    
    def EndGame(self,game_state,scores):
        self._InsertState("--------------End of game-------------",game_state)
        for i,plr_state in enumerate(game_state.agents):
            self._InsertState("Final score with bonus for Agent {}: {}".format(i,plr_state.score),game_state)
        
        # text display for multiple games
        # result = "Final score with bonus for"
        # for i,plr_state in enumerate(game_state.agents):
        #     result = result + " Agent "+str(i)+": "+str(plr_state.score)+"; "
        # print(result+"\n")

        self.focus = None
        def OnHistorySelect(event):
            w = event.widget
            self.focus = int(w.curselection()[0])
            if self.focus < len(self.game_state_history):
                self._DisplayState(self.game_state_history[self.focus])
        def OnHistoryAction(event):
            if event.keysym == "Up":
                if self.focus>0:
                    self.move_box.select_clear(self.focus)
                    self.focus -=1
                    self.move_box.select_set(self.focus)
                    if self.focus < len(self.game_state_history):
                        self._DisplayState(self.game_state_history[self.focus])
            if event.keysym == "Down":
                if self.focus<len(self.game_state_history)-1:
                    self.move_box.select_clear(self.focus)
                    self.focus +=1
                    self.move_box.select_set(self.focus)
                    self._DisplayState(self.game_state_history[self.focus])


        self.move_box.bind('<<ListboxSelect>>', OnHistorySelect)
        self.move_box.bind('<Up>', OnHistoryAction)
        self.move_box.bind('<Down>', OnHistoryAction)


    
        self.root.mainloop()
        pass    



class TextDisplayer(Displayer):
    def __init__(self):
        print ("--------------------------------------------------------------------")
        return

    def InitDisplayer(self,runner):
        pass

    def StartRound(self,game_state):
        pass   
    
    def  _DisplayState(self,game_state):
        pass

    def ExcuteAction(self,i,move, game_state):
        print(i)
        print(game_state.agents)
        plr_state = game_state.agents[i-1]
        print("\nAgent {} has chosen the following move:".format(i))
        print(ActionToString(i, move))
        print("\n")
        
        print("The new agent state is:")
        print(AgentToString(i, plr_state))
        print ("--------------------------------------------------------------------")
        
    def TimeOutWarning(self,runner,id):
        print ( "Agent {} Time Out, {} out of {}.".format(id,runner.warnings[id],runner.warning_limit))
    
    def EndRound(self,state):
        print("ROUND HAS ENDED")
        print ("--------------------------------------------------------------------")

    def EndGame(self,game_state,scores):
        print("GAME HAS ENDED")
        print ("--------------------------------------------------------------------")
        for plr_state in game_state.agents:
            print ("Score for Agent {}: {}".format(plr_state.id,plr_state.score))
