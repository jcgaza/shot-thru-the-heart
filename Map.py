import pygame as pg 

WALL_SIZE = 32

bg = pg.image.load('./assets/bg_game1.png')

class Wall:
  def __init__(self, pos, filename):
    self._image = pg.image.load("./assets/"+filename+".png")
    self.pos = pos
    self.rect = pg.Rect(pos, self._image.get_size())

  def draw(self, screen):
    screen.blit(self._image, self.rect)

  def eventHandler(self):
    pass

class Map(object):
  def __init__(self):
    self.players = []
    self.arrows = {}

    self.gameMap = self.loadMap("map.txt")
    self.walls = self.getWalls(self.gameMap)
    self.gameSurface = pg.Surface((980, 640))

  def loadMap(self, filename):
    gameHandler = open(filename, "r")
    tileMap = []
    for lines in gameHandler:
      line = lines.split(",")
      tileMap.append(line)

    return tileMap

  def getWalls(self, board):
    walls = []
    for i in range(0, 20):
      for j in range(0, 30):
        if(board[i][j] == '1'):
          walls.append(Wall((WALL_SIZE*j, WALL_SIZE*i), "block"))
    return walls

  def redrawWalls(self):
    for wall in self.walls:
      wall.draw(self.gameSurface)

  def redrawPlayers(self):
    for player in self.players:
      player.redrawPlayer(self.gameSurface)

  def redrawGame(self):
    self.gameSurface.blit(bg, [0,0])
    self.redrawWalls()
    self.redrawPlayers()
