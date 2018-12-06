import pygame
import math
class GameSprite(object):
  ALIVE = 1
  DEAD = 0
  cooldown = 3000
  def __init__(self, x, y, number, sprite):
    self.x = x
    self.y = y
    self.number = number
    self.isAlive = GameSprite.ALIVE
    self.sprite = sprite
    self.currSprite = self.sprite[GameSprite.ALIVE]
    self.image = self.sprite[GameSprite.ALIVE]
    self.direction = 0

  # Uses  Separating Axis Theorem for collisions
  # Taken from https://www.pandadeath.com/tile-based-collision-detection.html
  def axisOverlap(self, pointOne, lengthOne, pointTwo, lengthTwo):
    collided = False
    if pointOne < pointTwo:
        if pointTwo+lengthTwo-pointOne < lengthOne+lengthTwo:
            collided = True
    elif pointOne > pointTwo:
        if pointOne+lengthOne-pointTwo < lengthOne+lengthTwo:
            collided = True
    elif pointOne == pointTwo:
        collided = True
    return collided

  def redraw(self, display):
    display.blit(self.image, (self.x, self.y))

  def rotate(self, degree):
    angleToMousePoint = (180 / math.pi) * -1 * self.direction + degree
    self.image = pygame.transform.rotate(self.currSprite, int(angleToMousePoint))

  def getDirection(self, mousePos):
    relX, relY = mousePos[0] - self.x, mousePos[1] - self.y
    self.direction = math.atan2(relY, relX)
#######################PLAYER CLASS#######################################

class Player(GameSprite):
  COOLDOWN = 3000

  def __init__(self, x, y, number, sprite):
    GameSprite.__init__(self, x, y, number, sprite)
    self.width = 32
    self.height = 32
    self.dashReady = True
    self.lastDash = 0 # change this value once game actually starts pygame.time.get_ticks()
    self.step = 6
    self.amountOfArrows = 2
    self.hitbox = (self.x+8, self.y+8, 24, 24)
    self.points = 0

  def arrowPickup(self, arrows):
    for arrow in arrows:
      if(arrow.alive == 1):
        xCollision = self.axisOverlap(self.hitbox[0], 24, arrow.rect[0], arrow.rect[2])
        yCollision = self.axisOverlap(self.hitbox[1], 24, arrow.rect[1], arrow.rect[3])
        xyCollision = xCollision & yCollision
        if(xyCollision):
          player.amountOfArrows += 1
          arrows.pop(arrows.index(arrow))

  def wallCollision(self, direction, solids):
    xCollision = False
    yCollision = False
    xyCollision = False

    if(direction == "l"):
      yStep = 0
      xStep = -1 * self.step
    elif(direction == "r"):
      yStep = 0
      xStep = self.step
    elif(direction == "u"):
      yStep = -1 *self.step
      xStep = 0
    else:
      xStep = 0
      yStep = self.step
    #fix dash solids mechanics, since player can dash through walls
    for solid in solids:
      xCollision = self.axisOverlap(self.hitbox[0] + xStep, 24, solid[0], solid[2])
      yCollision = self.axisOverlap(self.hitbox[1] + yStep, 24, solid[1], solid[3])
      xyCollision = xCollision & yCollision
      if(xyCollision):
        if (direction == "l"):
          self.x = solid[0] + solid[2] - 8 
        elif (direction == "r"):
          self.x = solid[0] - self.width
        elif (direction == "u"):
          self.y = solid[1] + solid[3] - 8
        elif (direction == "d"):
          self.y = solid[1] - self.height
        return True
    return False

  def move(self, direction, solids, arrows):
    if(not self.wallCollision(direction, solids)):
      if(direction == "l"):
        self.moveLeft()
      elif(direction == "r"):
        self.moveRight()
      elif(direction == "u"):
        self.moveUp()
      elif(direction == "d"):
        self.moveDown()

    self.arrowPickup(arrows)
    self.hitbox = (self.x+8, self.y+8, 24, 24)
    self.step = 6

  def moveRight(self):
    self.x += self.step

  def moveLeft(self):
    self.x -= self.step
  
  def moveUp(self):
    self.y -= self.step

  def moveDown(self):
    self.y += self.step
  
  def dashCooldown(self):
    now = pygame.time.get_ticks()
    if now - self.lastDash >= Player.COOLDOWN:
      self.dashReady = True
      self.lastDash = now
