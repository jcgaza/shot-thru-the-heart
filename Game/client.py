import pygame
import math
import time
import socket
import pickle
import Sprites
import threading
block = pygame.image.load("block.png")

class GameClient(object):
  def __init__(self):
    pygame.init()
    self.ADDRESS = "localhost"
    self.PORT = 3000
    self.gameDisplay = pygame.display.set_mode((960, 640))
    self.clock = pygame.time.Clock()
    self.players = []
    self.arrows = []
    self.clientPlayer = 0
    self.gameMap = self.loadMap()
    self.solids = self.getSolids(self.gameMap)
    self.CLIENT = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  def sendToServer(self, data):
    self.CLIENT.sendto(pickle.dumps(data), (self.ADDRESS, self.PORT))

  def loadPlayer(self, data):
    self.clientPlayer = data
    self.clientPlayer.currSprite = pygame.image.load(self.clientPlayer.image)
    self.clientPlayer.image = pygame.image.load(self.clientPlayer.image)

  def loadPlayers(self):
    for player in self.players:
      player.currSprite = pygame.image.load(player.image)
      player.image = pygame.image.load(player.image)

  def updatePlayers(self,data):
    for i in range (0, len(self.players)):
      self.players[i].x = data[i][0]
      self.players[i].y = data[i][1]
      self.players[i].direction = data[i][2]
      self.players[i].rotate(270)

  #Redrawing of Map
  def redrawMap(self, board):
    for i in range(0, 20):
      for j in range(0, 20):
        if(board[i][j] == '1'):
          self.gameDisplay.blit(block, (32*j, 32*i))

  #Load map - TODO, pass filename for multple different maps
  def loadMap(self):
    gameHandler = open("map.txt", "r")
    tileMap = []
    for lines in gameHandler:
      line = lines.split(",")
      tileMap.append(line)

    return tileMap

  def getSolids(self, board):
    solid = []
    for i in range(0, 20):
      for j in range(0, 20):
        if(board[i][j] == '1'):
          solid.append(pygame.Rect( 32*j, 32*i, 32, 32))
    return solid
  
  # Redrawing of game, passed are the players and the arrows
  def redrawGameWindow(self):
    self.gameDisplay.fill((255,255,255)) #This will be removed once all tile designs have been made

    self.redrawMap(self.gameMap)
    self.clientPlayer.redraw(self.gameDisplay)
    for player in self.players:
      player.redraw(self.gameDisplay)

    pygame.display.update()
  
  def recieveServerInfo(self):
    running = True
    while running:
      data, address = self.CLIENT.recvfrom(8192)
      data = pickle.loads(data)
      self.updatePlayers(data)

  def gameLoop(self):
    run = True
    listener = threading.Thread(target = self.recieveServerInfo, args=())
    listener.daemon = True
    listener.start()
    while run:
      self.clock.tick(60)

      # Loop for quitting and mouse event
      events = pygame.event.get()
      for event in events:
        if event.type == pygame.QUIT:
          run = False

      if(self.clientPlayer.isAlive == Sprites.Player.ALIVE):
        self.clientPlayer.dashCooldown()

        keys = pygame.key.get_pressed()

        self.clientPlayer.getDirection(pygame.mouse.get_pos())
        self.clientPlayer.rotate(270)

        if keys[pygame.K_SPACE] and self.clientPlayer.dashReady:
          self.clientPlayer.step = 64
          self.clientPlayer.dashReady = False

        if keys[pygame.K_a]:
          self.clientPlayer.move("l", self.solids, self.arrows)
        if keys[pygame.K_d]:
          self.clientPlayer.move("r", self.solids, self.arrows)
        if keys[pygame.K_w]:
          self.clientPlayer.move("u", self.solids, self.arrows)
        if keys[pygame.K_s]:
          self.clientPlayer.move("d", self.solids, self.arrows)

        self.sendToServer([(self.clientPlayer.x,self.clientPlayer.y), self.clientPlayer.direction])

      # Update window screen
      self.redrawGameWindow()

    # Exit the game

  def main(self):
    self.sendToServer("CONNECTING")
    data, serverAddress = self.CLIENT.recvfrom(8192)
    data = pickle.loads(data)
    self.loadPlayer(data[1])
    self.PORT = self.PORT + self.clientPlayer.number + 1

    data, serverAddress = self.CLIENT.recvfrom(8192)
    data = pickle.loads(data)
    self.players = data
    self.loadPlayers()

    self.gameLoop()
    pygame.quit()

client = GameClient()
client.main()