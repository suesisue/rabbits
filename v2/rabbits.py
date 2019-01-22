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
        self.num=data["player"]
        self.gameid=data["gameid"]
        self.loc=data["loc0"] if self.num==0 else data['loc1'] 
        self.loc_opp=data["loc1"] if self.num==0 else data['loc0']
        self.loc_rab=data["loc2"]
        print(data, 'start_game')
        self.board[data['loc0']] = 0
        self.board[data['loc1']] = 1
        self.board[data['loc2']] = 2
        self.running=True
       
    def Network_movePlayer(self, data):
        self.placeSound.play()
        #get attributes
        loc = data["loc"]
        if data['num']==self.num:
            self.board[self.loc]=-1
            self.loc = loc
        else: 
            self.board[self.loc_opp]=-1
            self.loc_opp = loc
        self.board[loc] = data['num']

        loc_rab = data["loc_rab"]
        self.board[self.loc_rab]=-1
        self.board[loc_rab]=2
        self.loc_rab = loc_rab

    def __init__(self):
        pygame.init()
        pygame.font.init()
#        width, height = 389, 489
        n = 8 
        self.n = n
        self.width, self.height = 64*n + 5, 64*n + 105

        #initialize the screen
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Rabbits")

        #initialize pygame clock
        self.clock=pygame.time.Clock()
        #initialize the graphics
        self.initGraphics()
        self.turn = True
        self.board = np.zeros((n,n))-1
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
        self.turn = (self.num==0)
            
    def drawBoard(self):
        #print(self.board)
        for x in range(self.n):
            for y in range(self.n):
                if self.board[x,y]==0:
                    self.screen.blit(self.hunter0, (x*64+5, y*64+5))
                elif self.board[x,y]==1:
                    self.screen.blit(self.hunter1, (x*64+5, y*64+5))
                elif self.board[x,y]==2:
#                    and (abs(x - self.loc[0])<=1 and abs(y - self.loc[1])<=1):
                    self.screen.blit(self.rabbit, (x*64+5, y*64+5))
                else:
                    self.screen.blit(self.background, (x*64+5, y*64+5))

    def drawHUD(self):
        #draw the background for the bottom:
        self.screen.blit(self.score_panel, [0, self.width])
        #create font
        myfont = pygame.font.SysFont(None, 32)         
        #create text surface
        label = myfont.render("Your Turn:", 1, (255,255,255))
         
        #draw surface
        self.screen.blit(label, (10, self.n*64 + 15))
        self.screen.blit(self.greenindicator if self.turn else self.redindicator, (130, self.width))
        self.screen.blit(self.hunter0 if self.num==0 else self.hunter1, (10, self.n*64 + 30))
        #same thing here

    def update(self):
        if self.loc == self.loc_rab:
            self.didiwin=True #num=0 is the hunter
            self.didoppwin=False
            return 1
        if self.loc_opp == self.loc_rab:
            self.didiwin=False #num=0 is the hunter
            self.didoppwin=True

        #sleep to make the game 60 fps
        self.clock.tick(60)
        connection.Pump()
        self.Pump()
        #clear the screen
        self.screen.fill(0)
        self.drawBoard()
        self.drawHUD()

        for event in pygame.event.get():
            #quit if the quit button was pressed
            if event.type == pygame.QUIT:
                exit()
     
        #update the screen
        mouse = pygame.mouse.get_pos()
        xpos = int(math.floor((mouse[0]-5)/64.0))
        ypos = int(math.floor((mouse[1]-5)/64.0))
        isoutofbounds = xpos>(self.n-1) or ypos>(self.n-1) or xpos<0 or ypos<0 \
                        or (xpos==self.loc_opp[0] and ypos==self.loc_opp[1]) \
                        or not ((abs(self.loc[0] - xpos)<=1 and abs(self.loc[1] - ypos)<=1)
                             or (abs(self.loc[0] - xpos)==(self.n-1) and abs(self.loc[1] - ypos)<=1)
                             or (abs(self.loc[1] - ypos)==(self.n-1) and abs(self.loc[0] - xpos)<=1))
        
        if pygame.mouse.get_pressed()[0] and not isoutofbounds and self.turn:
            self.Send({"action": "movePlayer", "loc": (xpos,ypos), "num": self.num, "gameid": self.gameid})
        pygame.display.flip()
        
    def Network_win(self, data):
        self.winSound.play()
        
    def Network_lose(self, data):
        self.loseSound.play()
        
    def initGraphics(self):
        self.redindicator=pygame.image.load("redindicator.png")
        self.greenindicator=pygame.image.load("greenindicator.png")
        self.background=pygame.image.load("grass.png")
        self.hunter0=pygame.transform.scale(pygame.image.load("hunter0.png"),(64,64))
        self.hunter1=pygame.transform.scale(pygame.image.load("hunter1.png"),(64,64))
        self.rabbit=pygame.transform.scale(pygame.image.load("rabbit.jpg"),(64,64))
        self.winningscreen=pygame.image.load("youwin.png")
        self.gameover=pygame.image.load("gameover.png")
        self.score_panel=pygame.image.load("score_panel.png")
    
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