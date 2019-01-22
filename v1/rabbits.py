import pygame
import math
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep
import numpy as np

class BoxesGame(ConnectionListener):
    def initSound(self):
#        pygame.mixer.music.load("music.wav")
        self.winSound = pygame.mixer.Sound('win.wav')
        self.loseSound = pygame.mixer.Sound('lose.wav')
        self.placeSound = pygame.mixer.Sound('place.wav')
#        pygame.mixer.music.play()
        
    def Network_close(self, data):
        exit()
        
    def Network_yourturn(self, data):
        #torf = short for true or false
        self.turn = data["torf"]
        
    def Network_startgame(self, data):
        self.running=True
        self.num=data["player"]
        self.gameid=data["gameid"]
        self.loc=data["loc0"] if self.num==0 else data['loc1'] 
        self.loc_opp=data["loc1"] if self.num==0 else data['loc0']
        self.xpos, self.ypos = self.loc
        self.xpos_opp, self.ypos_opp = self.loc_opp
        print(data, 'start_gme')
        self.board[self.loc] = self.num
       
    def Network_movePlayer(self, data):
        self.placeSound.play()
        #get attributes
        x = data["x"]
        y = data["y"]
        self.board[x,y] = data['num']
        if data['num']==self.num:
            self.board[self.xpos,self.ypos]=-1
            self.xpos, self.ypos = x, y
            self.loc = x,y
        else: 
            self.board[self.xpos_opp,self.ypos_opp]=-1
            self.xpos_opp, self.ypos_opp = x, y
            self.loc_opp = x,y

    def __init__(self):
        pygame.init()
        pygame.font.init()
        width, height = 389, 489

        #initialize the screen
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Rabbits")

        #initialize pygame clock
        self.clock=pygame.time.Clock()
        #initialize the graphics
        self.initGraphics()
        self.turn = True
        self.board = np.zeros((6,6))-1
        self.didiwin=False
        self.didoppwin=False
        self.initSound()
        
        self.running=False
        try:
            host, port="localhost", 8000
            self.Connect((host, int(port)))
        except Exception as e:
            print(e)
            exit()
        print("Boxes client started")
        self.running=False
        
        while not self.running:
            self.Pump()
            connection.Pump()
            sleep(0.01)
        
        #determine attributes from player #
        if self.num==0:
            self.turn=True
            self.marker = self.hunter
            self.othermarker = self.rabbit
        else:
            self.turn=False
            self.marker=self.rabbit
            self.othermarker = self.hunter
            
    def drawBoard(self):
        for x in range(6):
            for y in range(6):
                if self.board[x,y]==self.num:
                    self.screen.blit(self.marker, (x*64+5, y*64+5))
                elif self.board[x,y]!=self.num and self.board[x,y]!=-1 and \
                    (abs(x - self.xpos)<=1 and abs(y - self.ypos)<=1):
                    self.screen.blit(self.othermarker, (x*64+5, y*64+5))
                else:
                    self.screen.blit(self.background, (x*64+5, y*64+5))

    def drawHUD(self):
        #draw the background for the bottom:
        self.screen.blit(self.score_panel, [0, 389])
        #create font
        myfont = pygame.font.SysFont(None, 32)
         
        #create text surface
        label = myfont.render("Your Turn:", 1, (255,255,255))
         
        #draw surface
        self.screen.blit(label, (10, 400))
        self.screen.blit(self.greenindicator if self.turn else self.redindicator, (130, 395))
        self.screen.blit(self.marker, (10, 425))
        #same thing here
#        myfont64 = pygame.font.SysFont(None, 64)
#        myfont20 = pygame.font.SysFont(None, 20)

#        scoreme = myfont64.render(str(self.me), 1, (255,255,255))
#        scoreother = myfont64.render(str(self.otherplayer), 1, (255,255,255))
#        scoretextme = myfont20.render("You", 1, (255,255,255))
#        scoretextother = myfont20.render("Other Player", 1, (255,255,255))

#        self.screen.blit(scoretextme, (10, 425))
#        self.screen.blit(scoreme, (10, 435))
#        self.screen.blit(scoretextother, (280, 425))
#        self.screen.blit(scoreother, (340, 435))

    def update(self):
        if self.loc == self.loc_opp:
            if self.num==0:
                self.didiwin=True #num=0 is the hunter
                self.didoppwin=False
            else:
                self.didiwin=False
                self.didoppwin=True
            return 1

        #sleep to make the game 60 fps
        self.clock.tick(60)
        connection.Pump()
        self.Pump()
        #clear the screen
        self.screen.fill(0)
        self.drawBoard()
        self.drawHUD()
#        self.drawOwnermap()

        for event in pygame.event.get():
            #quit if the quit button was pressed
            if event.type == pygame.QUIT:
                exit()
     
        #update the screen
        mouse = pygame.mouse.get_pos()
        xpos = int(math.floor((mouse[0]-5)/64.0))
        ypos = int(math.floor((mouse[1]-5)/64.0))
        isoutofbounds = xpos>5 or ypos>5 or xpos<0 or ypos<0 \
                        or not ((abs(self.xpos - xpos)<=1 and abs(self.ypos - ypos)<=1)
                             or (abs(self.xpos - xpos)==5 and abs(self.ypos - ypos)<=1)
                             or (abs(self.ypos - ypos)==5 and abs(self.xpos - xpos)<=1))
                        
        
        if pygame.mouse.get_pressed()[0] and not isoutofbounds and self.turn:
            self.Send({"action": "movePlayer", "x":xpos, "y":ypos, "num": self.num, "gameid": self.gameid})
        pygame.display.flip()
        
    def Network_win(self, data):
#        self.owner[data["x"]][data["y"]]="win"
#        self.boardh[data["y"]][data["x"]]=True
#        self.boardv[data["y"]][data["x"]]=True
#        self.boardh[data["y"]+1][data["x"]]=True
#        self.boardv[data["y"]][data["x"]+1]=True
        #add one point to my score
        self.winSound.play()
#        self.me+=1
        
    def Network_lose(self, data):
#        self.owner[data["x"]][data["y"]]="lose"
#        self.boardh[data["y"]][data["x"]]=True
#        self.boardv[data["y"]][data["x"]]=True
#        self.boardh[data["y"]+1][data["x"]]=True
#        self.boardv[data["y"]][data["x"]+1]=True
        #add one to other players score
        self.loseSound.play()
#        self.otherplayer+=1
        
    def initGraphics(self):
        self.redindicator=pygame.image.load("redindicator.png")
        self.greenindicator=pygame.image.load("greenindicator.png")
        self.background=pygame.image.load("grass.png")
        self.hunter=pygame.transform.scale(pygame.image.load("hunter.png"),(64,64))
        self.rabbit=pygame.transform.scale(pygame.image.load("rabbit.jpg"),(64,64))
        self.winningscreen=pygame.image.load("youwin.png")
        self.gameover=pygame.image.load("gameover.png")
        self.score_panel=pygame.image.load("score_panel.png")
    
#        self.hunter = self.hunter_orig.convert_alpha().copy()
#        self.hunter.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
        
#    def drawOwnermap(self):
#        for x in range(6):
#            for y in range(6):
#                if self.owner[x][y]!=0:
#                    if self.owner[x][y]=="win":
#                        self.screen.blit(self.marker, (x*64+5, y*64+5))
#                    if self.owner[x][y]=="lose":
#                        self.screen.blit(self.othermarker, (x*64+5, y*64+5))
                        
    def finished(self):
        if self.didiwin:
            self.screen.blit(self.winningscreen, (0,0))
        elif self.didoppwin:
            self.screen.blit(self.gameover, (0,0))
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            pygame.display.flip()
            
bg=BoxesGame() #__init__ is called right here
print("initialised")
while 1:
    try:
        if bg.update()==1:
            break
    except KeyboardInterrupt:
        break
bg.finished()