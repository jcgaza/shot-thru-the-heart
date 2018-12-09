import pygame
import math

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
    self.lastDash = pygame.time.get_ticks()
    self.step = 6
    self.sprite = pygame.image.load(filename)
    self.mouseX, self.mouseY = pygame.mouse.get_pos()
    self.image = self.sprite
    self.amountOfArrows = 2
    self.arrows = []
    self.hitbox = (self.x+8, self.y+8, 24, 24)
    self.rect = pygame.Rect(self.hitbox)

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

  def wallCollision(self, direction):
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

  def move(self, direction):
    if(not self.wallCollision(direction)):
      if(direction == "l"):
        self.moveLeft()
      elif(direction == "r"):
        self.moveRight()
      elif(direction == "u"):
        self.moveUp()
      elif(direction == "d"):
        self.moveDown()

    self.arrowPickup()
    self.hitbox = (self.x+8, self.y+8, 24, 24)
    self.rect = pygame.Rect(self.hitbox)
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
    if now - self.lastDash >= Player.cooldown:
      self.dashReady = True
      self.lastDash = now


  def rotate(self):
    self.mouseX, self.mouseY = pygame.mouse.get_pos()
    relX, relY = self.mouseX - self.x, self.mouseY - self.y
    angleToMousePoint = (180 / math.pi) * -math.atan2(relY, relX) + 270
    self.image = pygame.transform.rotate(self.sprite, int(angleToMousePoint))

  def redrawPlayer(self):
    gameDisplay.blit(self.image, (self.x, self.y))

class Arrow(object):
  def __init__(self, x, y, number, mousePos):
    self.x = x
    self.y = y
    self.owner = number
    self.mouseX, self.mouseY = mousePos
    self.direction = self.getDirection()
    self.sprite = [pygame.image.load("arrowAlive.png"), pygame.image.load("arrowDead.png")]
    self.image = self.rotateImage()
    self.startPos = (x,y)
    self.travelled = (x,y)

    self.alive = 0 #meaning moving
    self.rect = self.image.get_rect()
    self.rect[0] = self.x
    self.rect[1] = self.y
  
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
  
  def redrawArrow(self):
    gameDisplay.blit(self.image, (self.x, self.y))

  def rotateImage(self):
    angleToMousePoint = (180 / math.pi) * -1 * self.direction + 270
    image = pygame.transform.rotate(self.sprite[0], int(angleToMousePoint))
    return image
 
  def getDirection(self):
    relX, relY = self.mouseX - self.x, self.mouseY - self.y
    direction = math.atan2(relY, relX)

    return direction

  def collisionDetection(self, x, y):
    for player in playerList:
      if (player.playerNumber == self.owner):
        continue
      xCollision = self.axisOverlap(player.hitbox[0], 24, self.rect[0]+x, self.rect[2])
      yCollision = self.axisOverlap(player.hitbox[1], 24, self.rect[1]+y, self.rect[3])
      xyCollision = xCollision & yCollision
      if(xyCollision and player.isAlive == Player.ALIVE):
        player.isAlive = Player.DEAD
        player.image = pygame.image.load("dead.png")
        self.alive = 1
        return

    for solid in solids:
      xCollision = self.axisOverlap(solid[0], solid[2], self.rect[0]+x, self.rect[2])
      yCollision = self.axisOverlap(solid[1], solid[3], self.rect[1]+y, self.rect[3])
      xyCollision = xCollision & yCollision
      if(xyCollision):
        self.alive = 1
        return


  def reachedMaxDist(self):
    distance = math.sqrt((self.x-self.startPos[0])**2 + (self.y-self.startPos[1])**2)
    if(distance >= 320):
      self.alive = 1

  def move(self):
    xVal = round(math.cos(self.direction) * 20)
    yVal = round(math.sin(self.direction) * 20)
    
    self.collisionDetection(xVal, yVal)

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

    if self.alive == 1:
      self.image = self.sprite[1]
      self.rect = self.image.get_rect()

    self.rect[0] = self.x
    self.rect[1] = self.y

# Game Window
pygame.init()
gameDisplay = pygame.display.set_mode((640, 640))
pygame.display.set_caption("Shot Thru the Heart")

block = pygame.image.load("blocks1.png")
clock = pygame.time.Clock()
background = pygame.image.load('bg1.png')

#Redrawing of Map
def redrawMap(board):
  for i in range(0, 20):
    for j in range(0, 20):
      if(board[i][j] == '1'):
        gameDisplay.blit(block, (30*j, 30*i))

def loadMap():
  gameHandler = open("map.txt", "r")
  tileMap = []
  for lines in gameHandler:
    line = lines.split(",")
    tileMap.append(line)

  return tileMap

def getSolids(board):
  solid = []
  for i in range(0, 20):
    for j in range(0, 20):
      if(board[i][j] == '1'):
        solid.append(pygame.Rect(30*j, 30*i, 30, 30))
  return solid
  
# Redrawing of window
def redrawGameWindow(players, arrows):
  gameDisplay.fill((255,255,255))
  gameDisplay.blit(background, (0,0))
  redrawMap(gameMap)
  for player in players:
    player.redrawPlayer()
    pygame.draw.rect(gameDisplay, (0,255,0), player.hitbox, 2)

  for arrow in arrows:
    arrow.redrawArrow()
    pygame.draw.rect(gameDisplay, (255,0,0), arrow.rect, 2)

  pygame.display.update()

# Client and List of players
player = Player(0,0, 1, "char3.png")
player2 = Player(64,64,2, "char4.png")

playerList = []
playerList.append(player)
playerList.append(player2)

# Arrows
arrows = []

# Map
gameMap = loadMap()
solids = getSolids(gameMap)
# Main Loop
run = True
while run:
  # Framerate
  clock.tick(60)

  # Update window screen
  redrawGameWindow(playerList, arrows)

  for arrow in arrows:
    if(arrow.alive == 0):
      arrow.move()
  
  # Loop for quitting
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

    if event.type == pygame.MOUSEBUTTONUP and player.isAlive == Player.ALIVE:
      if(player.amountOfArrows != 0):
        # improve algo and area of shooting
        player.amountOfArrows -= 1
        arrows.append(Arrow(round(player.x + 12), round(player.y + 4), player.playerNumber ,pygame.mouse.get_pos()))

  if(player.isAlive == Player.ALIVE):
    player.dashCooldown()
    # For getting keys being pressed/held and movement
    keys = pygame.key.get_pressed()
    player.rotate()
    if keys[pygame.K_SPACE] and player.dashReady:
      player.step = 64
      player.dashReady = False

    if keys[pygame.K_a]:
      player.move("l")
    if keys[pygame.K_d]:
      player.move("r")
    if keys[pygame.K_w]:
      player.move("u")
    if keys[pygame.K_s]:
      player.move("d")

pygame.quit()