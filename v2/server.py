import PodSixNet.Channel
import PodSixNet.Server
from time import sleep
import numpy as np
import random

class ClientChannel(PodSixNet.Channel.Channel):
    def Network(self, data):
        print (data)
        
    def Network_movePlayer(self, data):
        #deconsolidate all of the data from the dictionary
        #x,y of placed, player number (1 or 0)
        print(data)
        loc = data["loc"]
        num = data["num"]     
        self.gameid = data["gameid"]
        self._server.movePlayer(loc, data, self.gameid, num)
    
    def Close(self):
        self._server.close(self.gameid)
        
class BoxesServer(PodSixNet.Server.Server):
 
    channelClass = ClientChannel
    def __init__(self, *args, **kwargs):
        PodSixNet.Server.Server.__init__(self, *args, **kwargs)
        self.games = []
        self.queue = None
        self.currentIndex=0
        
    def Connected(self, channel, addr):
        print( 'new connection:', channel)
        if self.queue==None:
            self.currentIndex+=1
            channel.gameid=self.currentIndex
            self.queue=Game(channel, self.currentIndex)
        else:
            channel.gameid=self.currentIndex
            self.queue.player1=channel
            self.queue.player0.Send({"action": "startgame","player":0, "gameid": self.queue.gameid, 'loc0':self.queue.loc0, 'loc1':self.queue.loc1, 'loc2':self.queue.loc2})
            self.queue.player1.Send({"action": "startgame","player":1, "gameid": self.queue.gameid, 'loc0':self.queue.loc0, 'loc1':self.queue.loc1, 'loc2':self.queue.loc2})
            self.games.append(self.queue)
            self.queue=None
            
    def movePlayer(self, loc, data, gameid, num):
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].movePlayer(loc, data, num)
            
    def close(self, gameid):
        try:
            game = [a for a in self.games if a.gameid==gameid][0]
            game.player0.Send({"action":"close"})
            game.player1.Send({"action":"close"})
        except:
            pass
    def tick(self):
        # Check for any wins
        # Loop through all of the squares
        index=0
        for game in self.games:
            game.player1.Send({"action":"yourturn", "torf":self.games[index].turn==1})
            game.player0.Send({"action":"yourturn", "torf":self.games[index].turn==0})
            index+=1
        self.Pump()
        
class Game:
    def __init__(self, player0, currentIndex):
        # whose turn (1 or 0)
        self.turn = 0
        n = 8
        self.n = n
        #owner map
        self.board = np.zeros((n,n)) - 1
        self.loc0 = (random.randint(0,n-1),random.randint(0,n-1))
        self.loc1 = (random.randint(0,n-1),random.randint(0,n-1))
        self.loc2 = (random.randint(0,n-1),random.randint(0,n-1))
        
        while self.loc1==self.loc0:
            self.loc1 = (random.randint(0,5),random.randint(0,n-1))
        while self.loc2==self.loc0 or self.loc2==self.loc1:
            self.loc2 = (random.randint(0,5),random.randint(0,n-1))
        
        self.board[self.loc0] = 0
        self.board[self.loc1] = 1
        self.board[self.loc2] = 2
        
        #initialize the players including the one who started the game
        self.player0=player0
        self.player1=None
        #gameid of game
        self.gameid=currentIndex
        
    def movePlayer(self, loc, data, num):
        #make sure it's their turn
        if num==self.turn:
            self.turn = 0 if self.turn else 1
            self.player1.Send({"action":"yourturn", "torf":self.turn==1})
            self.player0.Send({"action":"yourturn", "torf":self.turn==0})
            # in game
            if num==0: self.board[self.loc0] = -1
            else:      self.board[self.loc1] = -1
            self.board[loc] = num
            if num==0: self.loc0 = loc
            else:      self.loc1 = loc
            self.loc1 = loc
            
            #update rabbit
            loc2 = int((self.loc2[0] - np.sign(loc[0] - self.loc2[0]))%(self.n)),\
                   int((self.loc2[1] - np.sign(loc[1] - self.loc2[1]))%(self.n))
            self.board[self.loc2] = -1
            self.board[loc2] = 2 
            self.loc2 = loc2
            data['loc_rab'] = loc2
           
            #send data and turn data to each player
            self.player0.Send(data)
            self.player1.Send(data)
            
print ("STARTING SERVER ON LOCALHOST")
host, port="localhost", 8000
boxesServe = BoxesServer(localaddr=(host, int(port)))
while True:
    boxesServe.tick()
    sleep(0.01)
