import pygame as pg 

WALL_SIZE = 32

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
      for j in range(0, 20):
        if(board[i][j] == '1'):
          walls.append(pg.Rect(WALL_SIZE*j, WALL_SIZE*i, WALL_SIZE, WALL_SIZE))
    return walls

  def redrawGame(self):
    self.gameSurface.fill((255,255,255))
