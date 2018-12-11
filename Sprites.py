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
    for arrowId, arrow in arrows.items():
      if(arrow.isAlive == Arrow.DEAD):
        xCollision = self.axisOverlap(self.hitbox[0], 24, arrow.rect[0], arrow.rect[2])
        yCollision = self.axisOverlap(self.hitbox[1], 24, arrow.rect[1], arrow.rect[3])
        xyCollision = xCollision & yCollision
        if(xyCollision):
          self.amountOfArrows += 1
          arrows.pop(arrowId)
          return arrowId
    return "none"

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

    pickup = self.arrowPickup(arrows)
    self.hitbox = (self.x+8, self.y+8, 24, 24)
    self.step = 6
    return pickup

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

#######################ARROW CLASS#######################################
class Arrow(GameSprite):
  def __init__(self, x, y, number, mousePos):
    GameSprite.__init__(self,x,y,number, ["arrowDead.png", "arrowAlive.png"])

    self.direction = 0
    self.getDirection(mousePos)
    self.startPos = (x,y)
    self.travelled = (x,y)
    self.currSprite = pygame.image.load("arrowAlive.png")
    self.rotate(270)
    self.rect = self.image.get_rect()
    self.rect[0] = self.x
    self.rect[1] = self.y
  
  def collisionDetection(self, x, y, playerList, clientPlayer, solids):
    for player in playerList:
      if (player.number == self.number):
        continue
      xCollision = self.axisOverlap(player.hitbox[0], 24, self.rect[0]+x, self.rect[2])
      yCollision = self.axisOverlap(player.hitbox[1], 24, self.rect[1]+y, self.rect[3])
      xyCollision = xCollision & yCollision
      if(xyCollision and player.isAlive == Player.ALIVE):
        player.isAlive = Player.DEAD
        player.image = pygame.image.load("dead.png")
        self.isAlive = Arrow.DEAD
        return

    if clientPlayer.number != self.number:
      xCollision = self.axisOverlap(clientPlayer.hitbox[0], 24, self.rect[0]+x, self.rect[2])
      yCollision = self.axisOverlap(clientPlayer.hitbox[1], 24, self.rect[1]+y, self.rect[3])
      xyCollision = xCollision & yCollision
      if(xyCollision and clientPlayer.isAlive == Player.ALIVE):
        clientPlayer.isAlive = Player.DEAD
        clientPlayer.image = pygame.image.load("dead.png")
        self.isAlive = Arrow.DEAD

    for solid in solids:
      xCollision = self.axisOverlap(solid[0], solid[2], self.rect[0]+x, self.rect[2])
      yCollision = self.axisOverlap(solid[1], solid[3], self.rect[1]+y, self.rect[3])
      xyCollision = xCollision & yCollision
      if(xyCollision):
        self.isAlive = Arrow.DEAD
        return

  def reachedMaxDist(self):
    distance = math.sqrt((self.x-self.startPos[0])**2 + (self.y-self.startPos[1])**2)
    if(distance >= 320):
      self.isAlive = Arrow.DEAD

  def move(self, players, player, solids):
    xVal = round(math.cos(self.direction) * 20)
    yVal = round(math.sin(self.direction) * 20)
    
    self.collisionDetection(xVal, yVal, players, player, solids)

    self.x += xVal
    self.y += yVal
    if(self.x > 640):
      self.x = 0
    elif(self.x < 0):
      self.x = 602
    if(self.y > 640):
      self.y = 0
    elif(self.y < 0):
      self.y = 602
    
    self.travelled = (self.travelled[0]+xVal, self.travelled[1]+yVal)
    self.rect = self.image.get_rect()
    self.reachedMaxDist()

    if self.isAlive == Arrow.DEAD:
      self.currSprite = pygame.image.load("arrowDead.png")
      self.image = self.currSprite
      self.rect = self.image.get_rect()

    self.rect[0] = self.x
    self.rect[1] = self.y
