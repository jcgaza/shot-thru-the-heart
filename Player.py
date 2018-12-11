import pygame as pg

class Player(object):
  cooldown = 3000
  ALIVE = 1
  DEAD = 0
  def __init__(self, x, y, number, filename):
    self.isAlive = Player.ALIVE
    self.playerNumber = number
    self.x = x
    self.y = y
    self.width = 32
    self.height = 32
    self.dashReady = True
    self.lastDash = pg.time.get_ticks()
    self.step = 6
    self.sprite = pg.image.load(filename)
    self.mouseX, self.mouseY = pg.mouse.get_pos()
    self.image = self.sprite
    self.amountOfArrows = 2
    self.arrows = []
    self.hitbox = (self.x+8, self.y+8, 24, 24)
    self.rect = pg.Rect(self.hitbox)
    self.solids = None

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

  def arrowPickup(self):
    for arrow in arrows:
      if(arrow.alive == 1):
        xCollision = self.axisOverlap(self.hitbox[0], 24, arrow.rect[0], arrow.rect[2])
        yCollision = self.axisOverlap(self.hitbox[1], 24, arrow.rect[1], arrow.rect[3])
        xyCollision = xCollision & yCollision
        if(xyCollision):
          player.amountOfArrows += 1
          arrows.pop(arrows.index(arrow))

  # def wallCollision(self, direction):
  #   xCollision = False
  #   yCollision = False
  #   xyCollision = False

  #   if(direction == "l"):
  #     yStep = 0
  #     xStep = -1 * self.step
  #   elif(direction == "r"):
  #     yStep = 0
  #     xStep = self.step
  #   elif(direction == "u"):
  #     yStep = -1 *self.step
  #     xStep = 0
  #   else:
  #     xStep = 0
  #     yStep = self.step

  #   #fix dash solids mechanics, since player can dash through walls
  #   for solid in self.solids:
  #     xCollision = self.axisOverlap(self.hitbox[0] + xStep, 24, solid[0], solid[2])
  #     yCollision = self.axisOverlap(self.hitbox[1] + yStep, 24, solid[1], solid[3])
  #     xyCollision = xCollision & yCollision
  #     if(xyCollision):
  #       if (direction == "l"):
  #         self.x = solid[0] + solid[2] - 8 
  #       elif (direction == "r"):
  #         self.x = solid[0] - self.width
  #       elif (direction == "u"):
  #         self.y = solid[1] + solid[3] - 8
  #       elif (direction == "d"):
  #         self.y = solid[1] - self.height
  #       return True
  #   return False

  def move(self, direction):
    # if(not self.wallCollision(direction)):
    if(direction == "l"):
      self.moveLeft()
    elif(direction == "r"):
      self.moveRight()
    elif(direction == "u"):
      self.moveUp()
    elif(direction == "d"):
      self.moveDown()

    # self.arrowPickup()
    self.hitbox = (self.x+8, self.y+8, 24, 24)
    self.rect = pg.Rect(self.hitbox)
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
    now = pg.time.get_ticks()
    if now - self.lastDash >= Player.cooldown:
      self.dashReady = True
      self.lastDash = now

  def rotate(self):
    # self.mouseX, self.mouseY = pg.mouse.get_pos()
    # relX, relY = self.mouseX - self.x, self.mouseY - self.y
    angleToMousePoint = (180 / math.pi) * -math.atan2(relY, relX) + 270
    self.image = pg.transform.rotate(self.sprite, int(angleToMousePoint))

  def redrawPlayer(self, screen):
    screen.blit(self.image, (self.x, self.y))