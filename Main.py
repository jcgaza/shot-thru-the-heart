import pygame as pg
import os
from pygame.locals import *
from os import listdir
from os.path import isfile, join
from threading import Thread
from ChatClient import ChatClient

# Only read images ONCE
IMAGE_PATH = "./assets"
CHARACTERS_PATH = "./assets/characters"
images_dict = dict()

images = [ f for f in listdir(IMAGE_PATH) if isfile(join(IMAGE_PATH,f)) and f.endswith('png') ]
char_images = [ f for f in listdir(CHARACTERS_PATH) if isfile(join(CHARACTERS_PATH,f)) and f.endswith('png') ]

for filename in images:
  images_dict[os.path.splitext(filename)[0]] = pg.image.load(join(IMAGE_PATH,filename))

for filename in char_images:
  images_dict[os.path.splitext(filename)[0]] = pg.image.load(join(CHARACTERS_PATH,filename))

# CONSTANTS
HEIGHT = 640
WIDTH = 1280
TICK_RATE = 15

COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')

TEXT_BOX_COLOR = pg.Color('#EBEBEB')
TEXT_COLOR = pg.Color('#000000')
WHITE = pg.Color("#FFFFFF")

EXIT = -1
START_PAGE = 1
NAME_PAGE = 2
CHARACTER_PAGE = 3
MAIN_PAGE = 4

class Button:
  def __init__(self, name, position, method):
    self._name = name
    self._pos = position
    self._rect = pg.Rect(position, images_dict[name].get_size())
    self._method = method

  def draw(self, screen):
    screen.blit(images_dict[self._name], self._rect)

  def eventHandler(self, event):
    if event.type == pg.MOUSEBUTTONDOWN:
      if event.button == 1:
        if self._rect.collidepoint(event.pos):
          self._method()

class InputBox:
  def __init__(self, x, y, w, h, font, text=''):
    self.rect = pg.Rect(x, y, w, h)
    self.color = TEXT_BOX_COLOR
    self.text = text
    self.font = font
    self.txt_surface = self.font.render(text, True, TEXT_COLOR)
    self.active = False

  def eventHandler(self, event):
    if event.type == pg.MOUSEBUTTONDOWN:
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
    pg.draw.rect(screen, self.color, self.rect, 2)


class App:
  def __init__(self):
    self._running = True
    self._display_surf = None
    self._clock = pg.time.Clock()
    self._state = START_PAGE

    self.size = (WIDTH, HEIGHT)
    self.font = None

    self.chatClient = ChatClient()
    self.chatThread = Thread(target=self.chatClient.receiveMessages)
    self.chatThread.daemon = True

    self.name = ""

  def on_init(self):
    pg.init()
    pg.display.set_caption("Shot Through the Heart")
    self._display_surf = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)
    self.font = pg.font.Font('assets/upheavtt.ttf', 100)
    self.font1 = pg.font.SysFont("monospace", 15)

  def on_cleanup(self):
    pg.quit()

  def on_execute(self):
    if self.on_init() == False:
      self._running = False

    while self._running:
      for event in pg.event.get():
        if event.type == pg.QUIT:
          self.chatClient.terminate()
          self._running = False

      if self._state == START_PAGE:
        self.startPage()
      elif self._state == NAME_PAGE:
        self.namePage()
      elif self._state == CHARACTER_PAGE:
        self.characterPage()
      elif self._state == MAIN_PAGE:
        self.mainPage()
      elif self._state == EXIT:
        break

    self.on_cleanup()

  def characterPage(self):
    player1Button = Button('ancient_exile_inactive', (250, 100), None)
    player2Button = Button('assassin_prince_inactive', (450, 100), None)
    player3Button = Button('last_of_the_order_inactive', (650, 100), None)
    player4Button = Button('turncloak_soldier_inactive', (850, 100), None)

    playerButtons = [player1Button, player2Button, player3Button, player4Button]

    while self._state == CHARACTER_PAGE:
      # display background
      self._display_surf.blit(images_dict['bg3'], [0,0])

      for event in pg.event.get():
        if event.type == pg.QUIT:
          self._running = False
          self._state = EXIT
          self.chatClient.terminate()
          break

      for player in playerButtons:
        player.draw(self._display_surf)

      pg.display.flip()
      self._clock.tick(TICK_RATE)

  def setName(self,name):
    self.name = name

  def namePage(self):
    def nextPage(name):
      self.setName(name)
      self._state = MAIN_PAGE

    startButton = Button('start_button', (980,380), lambda: nextPage(nameBox.text))
    nameBox = InputBox(120, 490, 835, 95, self.font)

    while self._state == NAME_PAGE:
      # display background
      self._display_surf.blit(images_dict['bg3'], [0,0])

      # check events
      for event in pg.event.get():
        if event.type == pg.QUIT:
          self._running = False
          self._state = EXIT
          self.chatClient.terminate()
          break

        elif event.type == pg.KEYDOWN:
          if nameBox.active:
            if event.key == pg.K_RETURN:
              nextPage(nameBox.text)
            elif event.key == pg.K_BACKSPACE:
              nameBox.clear()
            else:
              nameBox.unicode(event)

        nameBox.eventHandler(event)
        startButton.eventHandler(event)

      # Display logo
      self._display_surf.blit(images_dict['logo_test'], (0,0))

      self._display_surf.blit(images_dict['name_bound'], (110,400))
      nameBox.draw(self._display_surf)
      startButton.draw(self._display_surf)

      pg.display.flip()
      self._clock.tick(TICK_RATE)

  def startPage(self):
    def versusClicked():
      self._state = NAME_PAGE

    def exitClicked():
      self._running = False
      self._state = EXIT

    def guidesClicked():
      print("Coming soon!")

    # Only instantiate ONCE
    versusButton = Button('versus_button', (500,360), versusClicked)
    exitButton = Button('exit_button', (900,390), exitClicked)
    guidesButton = Button('guides_button', (150,400), guidesClicked)

    while self._state == START_PAGE:
      # display background
      self._display_surf.blit(images_dict['bg3'], [0,0])

      # check events
      for event in pg.event.get():
        if event.type == pg.QUIT:
          self._running = False
          self._state = EXIT
          self.chatClient.terminate()
          break

        # Check button events
        versusButton.eventHandler(event)
        exitButton.eventHandler(event)
        guidesButton.eventHandler(event)

      # Display logo
      self._display_surf.blit(images_dict['logo_test'], (0,0))
      
      # Draw the buttons
      versusButton.draw(self._display_surf)
      exitButton.draw(self._display_surf)
      guidesButton.draw(self._display_surf)
      
      pg.display.flip()
      self._clock.tick(TICK_RATE)

  def mainPage(self):
    def send(message):
      if len(inMessages) > 36:
        inMessages.pop(0)
      inMessages.append(message)

    def sendAction(message):
      self.chatClient.writeMessage(message)
      inputMessage.clearAll()

    self.chatClient.printToUI = send
    self.chatClient.connectAndChat(self.name, self.chatClient.createLobby(5))
    self.chatThread.start()

    inMessages = []
    inputMessage = InputBox(1000, 590, 220, 30, self.font1)
    sendButton = Button('send_button', (1230,593), lambda: sendAction(inputMessage.text))

    rect = pg.Rect(1000, 20, 260, 560)
    txt_surface = self.font1.render("", True, TEXT_COLOR)

    while self._state == MAIN_PAGE:
      self._display_surf.blit(images_dict['bg'], [0,0])

      for event in pg.event.get():
        if event.type == pg.QUIT:
          self._running = False
          self._state = EXIT
          self.chatClient.terminate()
          break

        elif event.type == pg.KEYDOWN:
          if inputMessage.active:
            if event.key == pg.K_RETURN:
              sendAction(inputMessage.text)
            elif event.key == pg.K_BACKSPACE:
              inputMessage.clear()
            else:
              inputMessage.unicode(event)
              
        inputMessage.eventHandler(event)
        sendButton.eventHandler(event)
      
      inputMessage.draw(self._display_surf)
      sendButton.draw(self._display_surf)

      self._display_surf.fill(WHITE, rect)
      pg.draw.rect(self._display_surf, WHITE, rect, 2)

      for i in range(0,len(inMessages)):
        renderText = self.font1.render(inMessages[i], True, TEXT_COLOR)
        self._display_surf.blit(renderText, (1010, 25+(i*15)))
      
      pg.display.flip()
      self._clock.tick(TICK_RATE)

if __name__ == "__main__" :
  theApp = App()
  theApp.on_execute()