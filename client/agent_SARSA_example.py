#!/usr/bin/env python3
import time
import ast
import random
import middleware.connection as connection
import middleware.constants
from constants import EXPLORATIONS
from constants import VISUALIZATION
class Agent:
    def __init__(self,HOST,PORT):
        # Connection
        self.c = connection.Connection(HOST, PORT)
        self.c.connect()
        print("Initializing parameters...")
        # Initialize parameters...
        # -- Get goal position and max_cood
        self.goal = self.getGoal()
        self.max_coord = self.getMaxCoord()
        self.obstacles = self.getObstaclesList()
        print("Obstacles:",self.obstacles)
        # -- Get targets
        self.targetsL = self.getListTargets(self.getTargets(),self.max_coord)
        # -- Get reward
        self.rewards = self.convertReward(self.getReward(),self.max_coord)
        # Test
        print("Rewards:",self.rewards)
        # Initialize QTable
        self.qTable = self.initializeQTable(self.max_coord)
        # Test
        print("Starting QTable:",self.qTable)
        # Get the initial position
        self.initial_pos = self.getPos()
        self.pos = self.initial_pos

    def print_message(self,data):
        print("Data:",data)

    def execute(self,action,value,sleep_t = 0.5):
        '''Sending action-value to server and receive the return...'''
        msg = self.c.snd_rcv_msg(action,value,sleep_t)
        return msg

    def getMaxCoord(self):
        '''Return the max coordinates'''
        msg = self.execute("info", "maxcoord")
        max_coord = ast.literal_eval(msg)
        # test
        # print('Received maxcoord', max_coord)
        return max_coord

    def getReward(self):
        '''Return the matrix of rewards'''
        msg = self.execute("info", "rewards")
        res = ast.literal_eval(msg)
        # test
        # print('Received rewards:', res)
        return res

    def getObstacles(self):
        '''The map of obstacles returned has the following characteristics:
        - it is a list of lists (matrix) where the first list corresponds to the first column
        - obst[0] - first column, obst[0][5] corresponds to y = 5 and x = 0
        - obst[1] - second column, obst[1][5] corresponds to y = 5 and x = 1'''
        msg = self.execute("info","obstacles")
        obst =ast.literal_eval(msg)
        # test
        #print('Received map of obstacles:', obst)
        return obst

    def getObstaclesList(self):
        obstacles =[]
        obst = self.getObstacles()
        col = 0
        for column in obst:
            row = 0
            # test
            #print("Column:", column)
            for pos in column:
                # test
                #print("Position:", pos)
                if pos == 1: #There is an obstacle
                    # col corresponds to x-axis while rows corresponds y-axis
                    obstacles.append((col,row))
                row += 1
            col += 1
            # test - the list of obstacles
            # print("List of obstacles:",obstacles)
        return obstacles

    def convertReward(self,rewards,max_coord):
        '''Return a dictionary of rewards'''
        rewards_dict = {}
        print("Max Coordinates x_max=",max_coord[0]," y_max=",max_coord[1])
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                rewards_dict[str((x,y))]=rewards[x][y]
        #print("Rewards converted: ", rewards_dict)
        return rewards_dict

    def initializeQTable(self,max_coord):
        '''Initialize QTable dict where
        - each coordinate has a value for each action
        - [n,e,s,w] n = north, e = east, s = south, w = west'''
        q_table ={}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                q_table[str((x,y))]=[0,0,0,0]
        #Test
        #print("QTable initialized: ", q_table)
        return q_table

    def getPos(self):
        '''Return the actual position of the agent. '''
        msg = self.execute("info", "position",0.01)
        pos = ast.literal_eval(msg)
        # Test
        #print('Received agent\'s position:', pos)
        return pos

    def getGoal(self):
        '''Return the position of the goal'''
        msg = self.execute("info", "goal")
        goal = ast.literal_eval(msg)
        # Test
        #print('Received agent\'s goal:', goal)
        return goal

    def getTargets(self):
        ''' Return the targets defined in the world.'''
        msg = self.execute("info", "targets")
        res = ast.literal_eval(msg)
        # Test
        # print('Received targets:', res)
        return res

    def getListTargets(self,targets,max_coord):
        targets_list =[]
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                if targets[x][y] == 1:
                    targets_list.append((x,y))
        # Test
        #print("Targets List:",targets_list)
        return targets_list


    def printQTable(self):
        '''Print QTable'''
        for i in range(self.max_coord[1]):
            row_str_n =  "|"
            row_str_w =  "|"
            row_str_s =  "|"
            for j in range(self.max_coord[0]):
                coordinates = (j,i)
                f_str_n = '(%3.1f)'%(self.qTable.get(str(coordinates))[0])
                f_str_s = '(%3.1f)'%(self.qTable.get(str(coordinates))[2])
                f_str_w = '(%3.1f)'%(self.qTable.get(str(coordinates))[3])
                f_str_e = '(%3.1f)'%(self.qTable.get(str(coordinates))[1])
                row_str_n = row_str_n + "    " + f_str_n + "    |"
                row_str_s = row_str_s + "    " + f_str_s + "    |"
                row_str_w = row_str_w + f_str_w + "   " + f_str_e + "|"
            print(row_str_n)
            print(row_str_w)
            print(row_str_s)
            print()


    def addServerQtableArrows(self):
        '''Add arrows for qTable'''
        self.printQTable()
        arrow =""
        for i in range(self.max_coord[1]):
            for j in range(self.max_coord[0]):
                coordinates = (j,i)
                if coordinates not in self.obstacles and coordinates != self.goal and coordinates not in self.targetsL:
                    coord_list = [self.qTable.get(str(coordinates))[0], self.qTable.get(str(coordinates))[1],
                                  self.qTable.get(str(coordinates))[2], self.qTable.get(str(coordinates))[3]]

                    #test
                    print("(",j,",",i,")=",coord_list)
                    #max
                    if coord_list != None:
                        max_elem = max(coord_list)
                        if max_elem == coord_list[0] == coord_list[1] == coord_list[2] == coord_list[3]:
                            print("all directions")
                            arrow ="north_east_south_west"
                            #msg = self.execute("marrow", "north_south_east_west" + "," + str(i) + "," + str(j), 0.05)
                        # Three equal
                        elif max_elem == coord_list[0] == coord_list[1] == coord_list[2]:
                            arrow ="north_east_south"
                        elif max_elem == coord_list[0] == coord_list[2] == coord_list[3]:
                            arrow ="north_south_west"
                        elif max_elem == coord_list[1] == coord_list[2] == coord_list[3]:
                            arrow ="east_south_west"
                        elif max_elem == coord_list[0] == coord_list[1] == coord_list[3]:
                            arrow ="north_east_west"
                        #Two equal
                        elif max_elem == coord_list[0] == coord_list[1]:
                            arrow = "north_east"
                        elif max_elem == coord_list[0] == coord_list[2]:
                            arrow = "north_south"
                        elif max_elem == coord_list[0] == coord_list[3]:
                            arrow = "north_west"
                        elif max_elem == coord_list[1] == coord_list[2]:
                            arrow = "east_south"
                        elif max_elem == coord_list[1] == coord_list[3]:
                            arrow = "east_west"
                        elif max_elem == coord_list[2] == coord_list[3]:
                            arrow = "south_west"
                        #The highest
                        else:
                          idx = coord_list.index(max_elem)
                          if  idx == 0:
                            #north
                            arrow = "north"
                          elif idx == 1:
                            # east
                            arrow = "east"
                          elif idx == 2:
                            # south
                            arrow = "south"
                          else:
                            # west
                            arrow = "west"
                        msg = self.execute("marrow", arrow+","+str(i)+","+str(j), 0.05)

    def convertToDirection(self,v:int):
        '''Convert to values (north,east,south,west)'''
        if v==0:
            return "north"
        elif v==1:
            return "east"
        elif v==2:
            return "south"
        else:
            return "west"

    # Epsilon-Greedy
    def epsilon_greedy(self, pos, epsilon:float):
        # Para todas as possíveis ações a selecionar em S (n,e,s,w):
        # (1 - epsilon): max
        # epsilon: random
        if random.random() <= epsilon:
            # Random
            direction = random.randint(0, 3)
            # Test
            #print("Selected a random value:",direction)
        else:
            # Select the max
            values = self.qTable[str(pos)]
            i = 1
            value ="north"
            direction = 0
            max = values[0]
            for i in range(1,4):
                if values[i] > max:
                    max = values[i]
                    direction = i

            # Test
            #print("Selected the max value:",max," direction:",direction)
        return direction

    def running(self):
        print("Start running...")
        for i in range(EXPLORATIONS):
            findGoal = False
            findTarget = False
            path = []  # Keep the path to the goal
            path.append(self.initial_pos)

            # SARSA
            alpha = 0.8
            gama = 0.9
            eps_greedy = 0.8
            # SARSA_ First action
            action = "command"
            # Return a number between 0 and 3 (n,e,s,w)
            direction = self.epsilon_greedy(self.pos,eps_greedy)
            # Return north,east,so
            value = self.convertToDirection(direction)
            # Execute action
            # Test
            # print("Action Value pair:", action, ":", value)
            msg = self.execute(action,value,0.02)
            path.append(self.pos) # Add sequence of actions
            # previous_pos and previous_direction
            previous_pos = self.pos
            previous_direction = direction
            #new_pos
            self.pos = self.getPos()
            # New direction selected (in the new position, if none obstacle)
            direction = self.epsilon_greedy(self.pos,eps_greedy)
            # Only if previous_pos != pos (there is no obstacle) it makes the calculus
            if self.pos != previous_pos:
                # Calculus
                #
                # Four qTable values from the previous position and selecting the previous_direction
                qTable_values = self.qTable[str(previous_pos)]
                            # The value of the action selected (direction) in the new position
                qTable_value_action = self.qTable[str(self.pos)][direction]
                # Calculate the new value for the previous direction
                qTable_values[previous_direction] = qTable_values[previous_direction] + alpha * ( self.rewards[str(self.pos)] +  qTable_value_action - qTable_values[previous_direction])
                # Actualize the qTable
                self.qTable[str(previous_pos)] = qTable_values
            # Test if it is already in the goal...
            if self.pos == self.goal:
                findGoal = True
            if self.pos in self.targetsL:
                findTarget = False
            while findGoal == False and findTarget == False:
                # _SARSA
                action = "command"
                value = self.convertToDirection(direction)
                # Test
                # print("Action Value pair:", action, ":", value)
                msg = self.execute(action,value,0.02)
                path.append(self.pos) # Add sequence of actions
                #old_pos and old_direction
                previous_pos = self.pos
                previous_direction = direction
                #new_pos
                self.pos = self.getPos()
                direction = self.epsilon_greedy(self.pos,eps_greedy)
                # Only if previous_pos != pos (not an obstacle) it makes the calculus
                if self.pos != previous_pos:
                    # Calculus
                    #
                    # Four qTable values from the previous position and selecting the previous_direction
                    qTable_values = self.qTable[str(previous_pos)]
                    # The value of the action selected (direction) in the new position
                    qTable_value_action = self.qTable[str(self.pos)][direction]
                    # Calculate the new value for the previous direction

                    qTable_values[previous_direction] = qTable_values[previous_direction] + alpha * ( self.rewards[str(self.pos)] +  qTable_value_action - qTable_values[previous_direction])
                    # Actualize the qTable
                    self.qTable[str(previous_pos)] = qTable_values
                # Test the end of the search
                if self.pos == self.goal:
                    findGoal = True
                if self.pos in self.targetsL:
                    findTarget = True

            # Test
            if (self.pos == self.goal):
                print("Found the goal!\n")
            else:
                print("Found the target!\n")
            #print("Path:",path)
            path_reversed = path[::-1]
            last_pos = path_reversed[0]
            del path_reversed[0] # Remove the last element (goal!)
            #print("The new values for qTable are:")
            #self.printQTable()
            # Set the agent to initial position
            # Test
            action = "command"
            value = "home"
            # print("Action Value pair:", action, ":", value)
            msg = self.execute(action,value,0.02)


        self.addServerQtableArrows()
        input()

if __name__=="__main__":
    agent = Agent(middleware.constants.HOST,middleware.constants.PORT)
    agent.running()
