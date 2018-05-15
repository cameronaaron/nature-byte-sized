"""
    64x64 grid
    Agent-based evo sim

    Agent
        Traits
            Strength
            Speed
            Intelligence
            Postition
            Health
            "Genetic signature"
        Similar agents overlap -> chance of new agent with mixed genetic code
        Different agents overlap -> fight
"""
import random, curses,time
class Agent(object):
    defaultSignature = 23
    def __init__(self, parentOne, parentTwo, x, y, environment, starter, lifespan=30, defaultSignature=defaultSignature):
        if not starter:
            self.strength = abs(random.choice([parentOne.strength,parentTwo.strength]) + random.randint(-2,2))
            #self.speed = abs(random.choice([parentOne.speed,parentTwo.speed]) + random.randint(-2,2))
            self.intelligence = abs(random.choice([parentOne.intelligence,parentTwo.intelligence]) + random.randint(-2,2))
            self.signature = parentOne.signature
            if random.randint(0,19) == 19:
                modifier = random.randint(0,1)
                if modifier == 0:
                    modifier = -1
                self.signature += modifier
        else:
            self.strength = random.randint(1,12)
            self.intelligence = random.randint(1,12)
            self.signature = random.randint(0,25)
        if self.signature < 0:
            self.signature = 25
        elif self.signature > 25:
            self.signature = 0
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.isAlive = True
        self.symbol = letters[self.signature]
        self.lifespan = lifespan
        self.age = 0
        self.x = x
        self.y = y
        environment[y][x].append(self)
    def move(self, environment, scr):
        direction = self.detect(environment)
        if len(direction) > 1:
            self.hide(environment,scr)
            environment[self.y][self.x].pop(environment[self.y][self.x].index(self))
            direction = random.choice(direction)
            if direction == "u":
                if self.y > 0:
                    self.y -= 1
                else:
                    self.y = 31
            elif direction == "d":
                if self.y < 31:
                    self.y += 1
                else:
                    self.y = 0
            elif direction == "l":
                if self.x > 0:
                    self.x -= 1
                else:
                    self.x = 63
            elif direction == "r":
                if self.x < 63:
                    self.x += 1
                else:
                    self.x = 0
            environment[self.y][self.x].append(self)
            self.show(scr)
        #Left off with this?
    def detect(self,environment):
        outs = ""
        if self.intelligence > 5:
            surroundings = {}
            if x == 0:
                surroundings["l"] = environment[self.y][63]
            else:
                surroundings["l"] = environment[self.y][self.x-1]
            if x == 63:
                surroundings["r"] = environment[self.y][0]
            else:
                surroundings["r"] = environment[self.y][self.x+1]
            if y == 0:
                surroundings["u"] = environment[31][self.x]
            else:
                surroundings["u"] = environment[self.y-1][self.x]
            if y == 31:
                surroundings["d"] = environment[0][self.x]
            else:
                surroundings["d"] = environment[self.y+1][self.x]
            for direction in surroundings:
                if len(surroundings[direction]) > 0 and self.intelligence > 7:
                    if surroundings[direction][-1].signature == self.signature:
                        outs += direction
                    elif surroundings[direction][-1].strength < self.strength:
                        outs += direction
                else:
                    outs += direction
        else:
            outs = "udlr"
        return outs
    def interact(self, environment, newAgents, agents):
        if len(environment[self.y][self.x]) > 1:
            canDuplicate = True
            for agent in environment[self.y][self.x]:
                if agent.signature != self.signature:
                    if agent.strength > self.strength:
                        self.die(environment,scr)
                    elif agent.strength < self.strength:
                        agent.die(environment,scr)
                else:
                    if len(agents) < 400 and random.randint(0,20) == 2 and canDuplicate:
                        newAgents.append(Agent(self,agent,self.x,self.y,environment,False,int((agent.lifespan+self.lifespan)/2)+random.randint(-1,1)))
                        canDuplicate = False
    def show(self,scr):
        if self.age > int(self.lifespan/4.0)*3:
            scr.addstr(self.y,self.x,self.symbol,curses.color_pair(1))
        elif self.age < int(self.lifespan/4.0):
            scr.addstr(self.y,self.x,self.symbol,curses.color_pair(2))
        else:
            scr.addstr(self.y,self.x,self.symbol)
    def hide(self,environment,scr):
        scr.addstr(self.y,self.x," ")
    def die(self,environment,scr):
        self.hide(environment,scr)
        self.isAlive = False
scr = curses.initscr()
scr.keypad(True)
curses.noecho()
scr.nodelay(1)
curses.curs_set(0)
curses.start_color()
curses.init_pair(1,curses.COLOR_WHITE,curses.COLOR_RED)
curses.init_pair(2,curses.COLOR_BLACK,curses.COLOR_GREEN)
scr.clear()
scr.refresh()
sim = -1
pause = 0#.5
while True:
    scr.clear()
    sim += 1
    environment = [[[] for x in range(64)] for y in range(32)]
    scr.addstr(0,65,"S"+str(sim))
    e = random.randint(90,110)
    newAgents = []
    agents = [Agent(None,None,random.randint(0,63),random.randint(0,31),environment,True,random.randint(45,105)) for f in range(e)]
    year = 0
    while True:
        k = scr.getch()
        if k == ord('.'):
            pause += 0.05
        elif k == ord(','):
            pause -= 0.05
        elif k == ord('0'):
            pause = 0
        elif k == ord('e'):
            break
        if pause < 0:
            pause = 0
        oldMap = environment[:]
        year += 1
        c = 0
        a = 0
        while a < len(agents):
            if not agents[a].isAlive or agents[a].age >= agents[a].lifespan or a > 500:
                agents[a].die(environment,scr)
                del environment[agents[a].y][agents[a].x][environment[agents[a].y][agents[a].x].index(agents[a])]
                del agents[a]
            else:
                a += 1
        for agent in agents:
            agent.move(oldMap,scr)
            agent.show(scr)
            agent.age += 1
            c += 1
        for agent in agents:
            agent.interact(environment,newAgents,agents)
            agent.show(scr)
        if len(newAgents) > 0:
            agents += newAgents
            newAgents = []
        if len(agents) > 0:
            boardCount = 0
            for l in range(32):
                for m in range(64):
                    boardCount += len(environment[l][m])
            scr.addstr(33,0,str(len(agents)) + ", B" + str(boardCount) + ", Y" + str(year) + ", P" + str(pause) + "                            ")
            scr.refresh()
            time.sleep(pause)
        else:
            scr.addstr(33,0,str(len(agents)) + ", B" + str(boardCount) + ", Y" + str(year) + ", P" + str(pause) + "                            ")
            scr.refresh()
            time.sleep(0.25)
            break
