import pygame
import math
import time
import socket
import pickle
import os
import Sprites
from threading import Thread
from pygame.locals import *
from os import listdir
from os.path import isfile, join
from ChatClient import ChatClient

block = pygame.image.load("./assets/block.png")

# Only read images ONCE
IMAGE_PATH = "./assets"
CHARACTERS_PATH = "./assets/characters"
images_dict = dict()

images = [ f for f in listdir(IMAGE_PATH) if isfile(join(IMAGE_PATH,f)) and f.endswith('png') ]
char_images = [ f for f in listdir(CHARACTERS_PATH) if isfile(join(CHARACTERS_PATH,f)) and f.endswith('png') ]

for filename in images:
  images_dict[os.path.splitext(filename)[0]] = pygame.image.load(join(IMAGE_PATH,filename))

for filename in char_images:
  images_dict[os.path.splitext(filename)[0]] = pygame.image.load(join(CHARACTERS_PATH,filename))

# CONSTANTS
HEIGHT = 640
WIDTH = 1280
TICK_RATE = 60

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

TEXT_BOX_COLOR = pygame.Color('#EBEBEB')
TEXT_COLOR = pygame.Color('#000000')
WHITE = pygame.Color("#FFFFFF")
RED = pygame.Color("#FF0000")
GREEN = pygame.Color("#00FF00")

EXIT = -1
START_PAGE = 1
NAME_PAGE = 2
CHARACTER_PAGE = 3
MAIN_PAGE = 4
HOWTOPLAY_PAGE = 5

class Button:
  def __init__(self, name, position, method):
    self._name = name
    self._pos = position
    self._rect = pygame.Rect(position, images_dict[name].get_size())
    self._method = method

  def draw(self, screen):
    screen.blit(images_dict[self._name], self._rect)

  def eventHandler(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
      if event.button == 1:
        if self._rect.collidepoint(event.pos):
          self._method()

class InputBox:
  def __init__(self, x, y, w, h, font, text=''):
    self.rect = pygame.Rect(x, y, w, h)
    self.color = TEXT_BOX_COLOR
    self.text = text
    self.font = font
    self.txt_surface = self.font.render(text, True, TEXT_COLOR)
    self.active = False

  def eventHandler(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
      # If the user clicked on the input_box rect.
      if self.rect.collidepoint(event.pos):
          # Toggle the active variable.
        self.active = not self.active
      else:
        self.active = False


  def render(self):
    self.txt_surface = self.font.render(self.text, True, TEXT_COLOR)

  def unicode(self, event):
    self.text += event.unicode
    self.render()

  def clear(self):
    self.text = self.text[:-1]
    self.render()

  def clearAll(self):
    self.text = ''
    self.render()

  def draw(self, screen):
    screen.fill(self.color, self.rect)
    screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
    pygame.draw.rect(screen, self.color, self.rect, 2)

class GameClient(object):
  def __init__(self):
    pygame.init()
    self.ADDRESS = "localhost"
    self.PORT = 3000
    self.gameDisplay = pygame.display.set_mode((1280, 640))
    self.clock = pygame.time.Clock()
    self.players = []
    self.arrows = {}
    self.clientPlayer = 0
    self.gameMap = self.loadMap()
    self.solids = self.getSolids(self.gameMap)
    self.CLIENT = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    self.state = START_PAGE
    self.running = False
    self.font = pygame.font.Font('assets/upheavtt.ttf', 100)
    self.font1 = pygame.font.SysFont("monospace", 15)
    self.font2 = pygame.font.Font('assets/upheavtt.ttf', 30)
    self.chatClient = ChatClient()
    self.chatThread = Thread(target=self.chatClient.receiveMessages)
    self.chatThread.daemon = True
    self.name = "Ced"
    self.isChatting = False
    self.lobbyId = ""
    self.roundStart = False

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

  def updateArrows(self, data):
    self.arrows[data[2]] = (Sprites.Arrow(data[0][0], data[0][1], data[3], data[1] ))

  #Redrawing of Map
  def redrawMap(self, board):
    for i in range(0, 20):
      for j in range(0, 30):
        if(board[i][j] == '1'):
          self.gameDisplay.blit(block, ((32*j)-10, 32*i))

  #Load map - TODO, pass filename for multple different maps
  def loadMap(self):
    gameHandler = open("map2.txt", "r")
    tileMap = []
    for lines in gameHandler:
      line = lines.split(",")
      tileMap.append(line)

    return tileMap

  def getSolids(self, board):
    solid = []
    for i in range(0, 20):
      for j in range(0, 30):
        if(board[i][j] == '1'):
          solid.append(pygame.Rect( 32*j, 32*i, 32, 32))
    return solid
  
  # Redrawing of game, passed are the players and the arrows
  def redrawGameWindow(self):
    self.gameDisplay.blit(images_dict['bg'], [0,0]) #This will be removed once all tile designs have been made
    self.gameDisplay.blit(images_dict['chat_bg_active' if self.isChatting else 'chat_bg_inactive'], [980,0])

    self.redrawMap(self.gameMap)
    self.clientPlayer.redraw(self.gameDisplay)
    for player in self.players:
      player.redraw(self.gameDisplay)

    for arrow in self.arrows.values():
      arrow.redraw(self.gameDisplay)
      pygame.draw.rect(self.gameDisplay, (255,0,0), arrow.rect, 2)
  
  def receiveServerInfo(self):
    running = True
    while running:
      data, address = self.CLIENT.recvfrom(8192)
      data = pickle.loads(data)
      if data[0] == "ACTION":
        self.updatePlayers(data[1])
      elif data[0] == "NEW_ARROW":
        self.updateArrows(data[1])
      elif data[0] == "PICKUP":
        self.updatePickedUpArrows(data[1])

  def updatePickedUpArrows(self, data):
    for k,v in data.items():
      self.arrows.pop(k)

  def gameLoop(self):
    def send(message):
      if len(inMessages) > 24:
        inMessages.pop(0)
        inMessages.pop(0)
      inMessages.append(message)

    def sendAction(message):
      self.chatClient.writeMessage(message)
      self.isChatting = False
      inputMessage.clearAll()

    arrowId = 0

    self.chatClient.printToUI = send
    self.chatThread.start()

    listener = Thread(target = self.receiveServerInfo, args=())
    listener.daemon = True
    listener.start()

    inMessages = [
      "**********COMMANDS*********",
      " PLAYERS - See player list",
      "    HELP - See commands",
      "***************************"
    ]
    inputMessage = InputBox(1000, 590, 260, 30, self.font1)

    while self.state == MAIN_PAGE:
      self.clock.tick(60)

      for arrow in self.arrows.values():
        if(arrow.isAlive == Sprites.Arrow.ALIVE):
          arrow.move(self.players, self.clientPlayer, self.solids)
  
      # Loop for quitting and mouse event
      events = pygame.event.get()
      for event in events:
        if event.type == pygame.QUIT:
          self.chatClient.terminate()
          self.state = EXIT

        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_RETURN:
            if not self.isChatting:
              self.isChatting = True
            else:
              sendAction(inputMessage.text)
          elif self.isChatting:
            if event.key == pygame.K_BACKSPACE:
              inputMessage.clear()
            elif len(inputMessage.text) < 25:
              inputMessage.unicode(event)
        elif not self.isChatting and event.type == pygame.MOUSEBUTTONUP and self.clientPlayer.isAlive == Sprites.Player.ALIVE:
          if(self.clientPlayer.amountOfArrows != 0):
            self.clientPlayer.amountOfArrows -= 1
            self.arrows[str(self.clientPlayer.number) + str(arrowId)] = (Sprites.Arrow( round(self.clientPlayer.x + 12), round(self.clientPlayer.y + 4), self.clientPlayer.number, pygame.mouse.get_pos() ))
            self.sendToServer(["ARROW_SHOT", (round(self.clientPlayer.x + 12), round(self.clientPlayer.y + 4)), pygame.mouse.get_pos(), str(self.clientPlayer.number) + str(arrowId) ])
            arrowId += 1

      if self.clientPlayer.isAlive == Sprites.Player.ALIVE and not self.isChatting:
        self.clientPlayer.dashCooldown()

        keys = pygame.key.get_pressed()

        self.clientPlayer.getDirection(pygame.mouse.get_pos())
        self.clientPlayer.rotate(270)

        if keys[pygame.K_SPACE] and self.clientPlayer.dashReady:
          self.clientPlayer.step = 64
          self.clientPlayer.dashReady = False

        arrowPickedUp = "none"

        if keys[pygame.K_a]:
          arrowPickedUp = self.clientPlayer.move("l", self.solids, self.arrows)
        if keys[pygame.K_d]:
          arrowPickedUp = self.clientPlayer.move("r", self.solids, self.arrows)
        if keys[pygame.K_w]:
          arrowPickedUp = self.clientPlayer.move("u", self.solids, self.arrows)
        if keys[pygame.K_s]:
          arrowPickedUp = self.clientPlayer.move("d", self.solids, self.arrows)

        if arrowPickedUp != "none":
          self.sendToServer(["PICKUP", arrowPickedUp])

        self.sendToServer(["ACTION", (self.clientPlayer.x,self.clientPlayer.y), self.clientPlayer.direction])

      # Update window screen
      self.redrawGameWindow()
      self.gameDisplay.fill(WHITE, (1000, 200, 260, 375))
      pygame.draw.rect(self.gameDisplay, WHITE, (1000, 200, 260, 375), 2)
      self.gameDisplay.fill(WHITE, (975, 0, 5, 1280))
      pygame.draw.rect(self.gameDisplay, WHITE, (975, 0, 5, 1280), 2)

      inputMessage.draw(self.gameDisplay)

      # Draw arrows
      for i in range(900, 900-(self.clientPlayer.amountOfArrows*35), -35):
        self.gameDisplay.blit(images_dict['arrow'], (i, 570))

      self.gameDisplay.blit(self.font.render("9", True, WHITE), (890, 10))
      self.gameDisplay.blit(self.font2.render("POINTS", True, WHITE), (860, 0))
      self.gameDisplay.blit(self.font2.render("ARROWS", True, WHITE), (860, 540))

      # Draw messages
      for i in range(0,len(inMessages)):
        renderText = self.font1.render(inMessages[i], True, TEXT_COLOR)
        self.gameDisplay.blit(renderText, (1010, 205+(i*15)))

      pygame.display.flip()

    # Exit the game

  def characterPage(self):
    def fightClicked():
      print("fight clickkk")
      
    player1Button = Button('ancient_exile_inactive', (250, 60), None)
    player2Button = Button('assassin_prince_inactive', (450, 60), None)
    player3Button = Button('last_of_the_order_inactive', (650, 60), None)
    player4Button = Button('turncloak_soldier_inactive', (850, 60), None)
    fightButton = Button('fight_button', (340,400), fightClicked)

    playerButtons = [player1Button, player2Button, player3Button, player4Button]

    while self.state == CHARACTER_PAGE:
      # display background
      self.gameDisplay.blit(images_dict['bg3'], [0,0])
        

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.running = False
          self.state = EXIT
          #self.chatClient.terminate()
          break

        fightButton.eventHandler(event)

      for player in playerButtons:
        player.draw(self.gameDisplay)

      fightButton.draw(self.gameDisplay)

      pygame.display.flip()
      self.clock.tick(TICK_RATE)
      
      data, serverAddress = self.CLIENT.recvfrom(8192)
      data = pickle.loads(data)
      print(data)
      self.players = data[1]
      self.loadPlayers()
      self.PORT = self.PORT + self.clientPlayer.number + 1

      if(self.clientPlayer.number != 0 and len(self.lobbyId) != 5):
        self.lobbyId = data[2]
        self.chatClient.connectAndChat(self.name, self.lobbyId)
        if data[0] == "START_GAME":
          print("should exit")
          self.state = MAIN_PAGE

      if(self.clientPlayer.number == 0):
        if data[0] == "START_GAME":
          self.state = MAIN_PAGE

  def howtoplayPage(self):
    def homeClicked():
      self.state = START_PAGE

    homeButton = Button('home_button', (0,45), homeClicked)

    while self.state == HOWTOPLAY_PAGE:
      # display background
      self.gameDisplay.blit(images_dict['how_to_play'], [0,0])

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.running = False
          self.state = EXIT
          #self.chatClient.terminate()
          break

        homeButton.eventHandler(event)

      homeButton.draw(self.gameDisplay)

      pygame.display.flip()
      self.clock.tick(TICK_RATE)  

  def setName(self,name):
    self.name = name

  def namePage(self):
    def nextPage(name):
      self.setName(name)
      self.sendToServer("READY")
      data, serverAddress = self.CLIENT.recvfrom(8192)
      data = pickle.loads(data)
      self.loadPlayer(data[1])  
      
      if(self.clientPlayer.number == 0):
        self.lobbyId = self.chatClient.createLobby(5)
        self.sendToServer(self.lobbyId)
        self.chatClient.connectAndChat(self.name, self.lobbyId)
      self.state = CHARACTER_PAGE

    def homeClicked():
      self.state = START_PAGE  

    startButton = Button('start_button', (980,380), lambda: nextPage(nameBox.text))
    nameBox = InputBox(120, 490, 835, 95, self.font)
    homeButton = Button('home_button', (0,45), homeClicked)

    while self.state == NAME_PAGE:
      # display background
      self.gameDisplay.blit(images_dict['bg3'], [0,0])

      # check events
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.running = False
          self.state = EXIT
          # self.chatClient.terminate()
          break

        elif event.type == pygame.KEYDOWN:
          if nameBox.active:
            if event.key == pygame.K_RETURN:
              nextPage(nameBox.text)
            elif event.key == pygame.K_BACKSPACE:
              nameBox.clear()
            elif len(nameBox.text) < 10:
              nameBox.unicode(event)

        nameBox.eventHandler(event)
        startButton.eventHandler(event)
        homeButton.eventHandler(event)

      # Display logo
      self.gameDisplay.blit(images_dict['logo_test'], (0,0))

      self.gameDisplay.blit(images_dict['name_bound'], (110,400))
      nameBox.draw(self.gameDisplay)
      startButton.draw(self.gameDisplay)
      homeButton.draw(self.gameDisplay)

      pygame.display.flip()
      self.clock.tick(TICK_RATE)

  def startPage(self):
    def versusClicked():
      self.state = NAME_PAGE

    def exitClicked():
      self.running = False
      self.state = EXIT

    def guidesClicked():
      self.state = HOWTOPLAY_PAGE

    # Only instantiate ONCE
    versusButton = Button('versus_button', (500,360), versusClicked)
    exitButton = Button('exit_button', (900,390), exitClicked)
    guidesButton = Button('guides_button', (150,400), guidesClicked)

    while self.state == START_PAGE:
      # display background
      self.gameDisplay.blit(images_dict['bg3'], [0,0])

      # check events
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.running = False
          self.state = EXIT
          # self.chatClient.terminate()
          break

        # Check button events
        versusButton.eventHandler(event)
        exitButton.eventHandler(event)
        guidesButton.eventHandler(event)

      # Display logo
      self.gameDisplay.blit(images_dict['logo_test'], (0,0))
      
      # Draw the buttons
      versusButton.draw(self.gameDisplay)
      exitButton.draw(self.gameDisplay)
      guidesButton.draw(self.gameDisplay)
      
      pygame.display.flip()
      self.clock.tick(TICK_RATE)

  def main(self):
    self.running = True
    while self.running:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.running = False

      if self.state == START_PAGE:
        self.startPage()
      elif self.state == NAME_PAGE:
        self.namePage()
      elif self.state == CHARACTER_PAGE:
        self.characterPage()
      elif self.state == HOWTOPLAY_PAGE:
        self.howtoplayPage()  
      elif self.state == MAIN_PAGE:
        self.gameLoop()
      elif self.state == EXIT:
        break

    pygame.quit()

client = GameClient()
client.main()
