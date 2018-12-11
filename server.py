import socket
import select
import pickle
import Sprites
import pygame
import threading
import time

# Constants
MAX_PLAYERS = 4
ADDRESS = "localhost"
PORT = 3000
STARTING_POS = [(288, 128), (320, 320), (480, 288)]
MAPS = ["map.txt"]

class GameServer(object):
  def __init__(self):
    self.clock = pygame.time.Clock()
    # Server Socket Initialization
    self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.SERVER.bind((ADDRESS, PORT))

    # Holds the game data 
    self.clientList = [] #addresses of the player
    self.clientHandlers = []
    self.playerList = []
    self.arrowList = {}
    self.playerCount = -1 #easier in terms of indexing
    self.map = []
    self.solids = []
    self.gameStart = [False]

  def addConnectedPlayer(self, pos, address, number):
    self.clientList.append(address)
    player = "player" + str(number+1) + ".png"
    self.playerList.append(Sprites.Player(pos[0], pos[1],number, ["dead.png", player]))
    print(len(self.playerList))
    self.SERVER.sendto(pickle.dumps(("ACK", self.playerList[number])), self.clientList[number])
    ch = ClientHandler(PORT+number+1, address, number, self)
    self.clientHandlers.append(ch)

  def loadMap(self, chosenMap):
    gameHandler = open(chosenMap, "r")
    tileMap = []
    for lines in gameHandler:
      line = lines.split(",")
      tileMap.append(line)
    return tileMap
  
  def broadcast(self, num):
    for ch in self.clientHandlers:
      if(ch.playerNumber != num):
        ch.sendGameUpdate()

  def sendShotArrows(self, data, num):
    for ch in self.clientHandlers:
      if(ch.playerNumber != num):
        ch.sendNewArrow(data, num)

  def sendArrowPickUp(self, data, num):
    self.arrowList.pop(data)
    for ch in self.clientHandlers:
      if(ch.playerNumber != num):
        ch.sendPickUpArrowId(self.arrowList)

  def updatePlayerPos(self, pos, player):
    self.playerList[player].x = pos[0]
    self.playerList[player].y = pos[1]

  def updatePlayerDir(self, direction, player):
    self.playerList[player].direction = direction

  def updateArrowList(self, data):
    self.arrowList[data[3]] = Sprites.Arrow.ALIVE

  def getPlayerList(self):
    return self.playerList

  def getSolids(board):
    solid = []
    for i in range(0, 20):
      for j in range(0, 20):
        if(board[i][j] == '1'):
          solid.append(pygame.Rect(160+ 32*j, 32*i, 32, 32))
    return solid

  def sendToClient(self, data, clientAddress):
    self.SERVER.sendto(pickle.dumps(data), clientAddress)

  def waitClients(self):
    startGame = True
    while not startGame:
      x = input("Choice - wait - start: ")
      if x == "start":
        break
      
    data, clientAddress = self.SERVER.recvfrom(8192)
    data = pickle.loads(data)
    print(data, " ", clientAddress)
    
    if (data == "CONNECTING" and self.playerCount != 3):
      print("A player has joined")
      self.playerCount += 1
      self.addConnectedPlayer(STARTING_POS[self.playerCount], clientAddress, self.playerCount)

    for ch in self.clientHandlers:
      ch.sendNewPlayer()
    
    time.sleep(2)
    for ch in self.clientHandlers:
      ch.start()
    
    self.gameStart[0] = True
    while not startGame:
      self.clock.tick(60)
      x = input("Choice - end: ")
      if x == "end":
        break

    self.SERVER.close()

# Client Handler is class that is a socket specifically incharge of recieving and sending data to its assigned client
class ClientHandler(threading.Thread, socket.socket):
  def __init__(self, port, client_add, player_number, server):
    socket.socket.__init__(self,type = socket.SOCK_DGRAM)
    threading.Thread.__init__(self, name='ClientHandler')
    self.settimeout(30)
    self.bind((ADDRESS, port))
    self.setDaemon(True)
    self.clientAddress = client_add
    self.playerNumber = player_number
    self.server = server

  def sendGameUpdate(self):
    players = self.server.getPlayerList()[:]
    players.pop(self.playerNumber)
    playerInfo = []
    if len(players) != 0:
      for x in players:
        info = (x.x, x.y, x.direction)
        playerInfo.append(info)
    self.sendto(pickle.dumps(("ACTION", playerInfo)), self.clientAddress)
  
  def sendNewArrow(self, data, num):
    data.append(num)
    self.sendto(pickle.dumps(("NEW_ARROW", data)), self.clientAddress)

  def sendPickUpArrowId(self, data):
    self.sendto(pickle.dumps(("PICKUP", data)), self.clientAddress)
  
  def recieveClientInfo(self):
    data, address = self.recvfrom(8192)
    data = pickle.loads(data)
    if data:
      if(data[0] == "ACTION"):
        self.server.updatePlayerPos(data[1], self.playerNumber)
        self.server.updatePlayerDir(data[2], self.playerNumber)
        self.server.broadcast(self.playerNumber)
      elif (data[0] == "ARROW_SHOT"):
        self.server.updateArrowList(data)
        self.server.sendShotArrows([data[1], data[2], data[3]], self.playerNumber)
      elif (data[0] == "PICKUP"):
        self.server.sendArrowPickUp(data[1], self.playerNumber)

  def sendNewPlayer(self):
    players = self.server.playerList[:]
    if len(players) != 0:
      players.pop(self.playerNumber)
      self.sendto(pickle.dumps(players), self.clientAddress)

  def run(self):
    while True:
      self.recieveClientInfo()

  def join(self, timeout=None):
    super().join(timeout=10)
    self.close() 

server = GameServer()
server.waitClients()