import pygame as pg
import os
from pygame.locals import *
from os import listdir
from os.path import isfile, join

# Only read images ONCE
IMAGE_PATH = "./assets"
images_dict = dict()

images = [ f for f in listdir(IMAGE_PATH) if isfile(join(IMAGE_PATH,f)) and f.endswith('png') ]

for filename in images:
  images_dict[os.path.splitext(filename)[0]] = pg.image.load(join(IMAGE_PATH,filename))

# CONSTANTS
HEIGHT = 640
WIDTH = 1280
TICK_RATE = 15

COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')

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
          print("CLICKED!")

class InputBox:
  def __init__(self, x, y, w, h, font, text=''):
    self.rect = pg.Rect(x, y, w, h)
    self.color = COLOR_INACTIVE
    self.text = text
    self.font = font
    self.txt_surface = self.font.render(text, True, self.color)
    self.active = False

  def handle_event(self, event):
    if event.type == pg.MOUSEBUTTONDOWN:
      # If the user clicked on the input_box rect.
      if self.rect.collidepoint(event.pos):
          # Toggle the active variable.
        self.active = not self.active
      else:
        self.active = False
      # Change the current color of the input box.
      self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
    if event.type == pg.KEYDOWN:
      if self.active:
        if event.key == pg.K_RETURN:
          print(self.text)
          self.text = ''
        elif event.key == pg.K_BACKSPACE:
          self.text = self.text[:-1]
        else:
          self.text += event.unicode
        # Re-render the text.
        self.txt_surface = self.font.render(self.text, True, self.color)

  def update(self):
    # Resize the box if the text is too long.
    width = max(200, self.txt_surface.get_width()+10)
    self.rect.w = width

  def draw(self, screen):
    # Blit the text.
    screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
    # Blit the rect.
    # screen.fill(self.color, self.rect)
    pg.draw.rect(screen, self.color, self.rect, 2)

class App:
  def __init__(self):
    self._running = True
    self._display_surf = None
    self._clock = pg.time.Clock()
    self.size = (WIDTH, HEIGHT)
    self.font = None

  def on_init(self):
    pg.init()
    pg.display.set_caption("Shot Through the Heart")
    self._display_surf = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)
    self.font = pg.font.Font('assets/upheavtt.ttf', 32)

  def on_loop(self):
    pass

  def on_render(self):
    pass

  def on_cleanup(self):
    pg.quit()

  def on_execute(self):
    if self.on_init() == False:
      self._running = False

    # Only instantiate ONCE
    versusButton = Button('versus_button', (500,360), "Versus")
    exitButton = Button('exit_button', (900,390), "Versus")
    guidesButton = Button('guides_button', (150,400), "Versus")

    input_box1 = InputBox(500, 360, 300, 50, self.font)

    while self._running:
      # display background
      self._display_surf.blit(images_dict['bg3'], [0,0])

      # check events
      for event in pg.event.get():
        if event.type == pg.QUIT:
          self._running = False

        # Check button events
        versusButton.eventHandler(event)
        exitButton.eventHandler(event)
        guidesButton.eventHandler(event)

        input_box1.handle_event(event)

      self.on_loop()
      self.on_render()

      # Display logo
      self._display_surf.blit(images_dict['logo_test'], (0,0))
      
      # Draw the buttons
      # versusButton.draw(self._display_surf)
      # exitButton.draw(self._display_surf)
      # guidesButton.draw(self._display_surf)
      input_box1.draw(self._display_surf)
      pg.display.flip()
      self._clock.tick(TICK_RATE)
    
    self.on_cleanup()

if __name__ == "__main__" :
  theApp = App()
  theApp.on_execute()