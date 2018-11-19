import socket
import select
import player_pb2
import tcp_packet_pb2

from threading import Thread
from sys import exit, stdout

class ChatClient():
  HOST = "202.92.144.45"
  PORT = 80
  BUFFER = 1024
  ADDRESS = (HOST, PORT)

  def __init__(self):
    self.tcp = tcp_packet_pb2.TcpPacket()
    self.connect = self.tcp.ConnectPacket()
    self.connect.type = self.tcp.CONNECT
    
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.connect(ChatClient.ADDRESS)

    except socket.error, (value, message):
      if self.s:
        self.s.close()
        print("Could not make connection.")
        exit()

    # Connect Packet
    self.tcp.type = tcp.CONNECT
    self.connect.player.name = input("Enter name: ")
    
    lobbyID = self.createLobbyPacket()
    self.connect.lobby_id = lobbyID

    self.s.send(self.connect.SerializeToString())
    data = self.s.recv(BUFFER)
    self.tcp.ParseFromString(data)

    # ERR_LDNE Packet
    if self.tcp.type == self.tcp.ERR_LDNE:
      print("Lobby does not exist.")
      exit()

    # ERR_LFULL Packet
    elif self.tcp.type == self.tcp.ERR_LFULL:
      print("Lobby is full!")
      exit()

    print("You're in Lobby {}.".format(lobbyID))
    self.isConnected = True

    # Chat Packet
    self.chat = tcp.ChatPacket()
    self.chat.type = tcp.CHAT
    self.chat.player.name = connect.player.name

    self.helpMenu()

    # For receiving messages
    # receiver = Thread(target=receivePacket, args=[parser])
    # receiver.start()

    while self.isConnected:
      try:
        read_sockets, write_sockets, error_sockets = select.select([0,self.s], [], [])

        for sock in read_sockets:
          if sock == self.s:
            data = self.s.recv(BUFFER)
            
            if not data:
              print("You have disconnected.")
              self.terminate()
            else:
              self.parser(data)
          else:
            self.writeMessage()
      except ValueError:
        break
      except OSError:
        break

  # Checking data received
  def parser(data):
    self.tcp.ParseFromString(data)

    if self.tcp.type == self.tcp.CONNECT:
      self.connect.ParseFromString(data)
      if self.connect.update == self.connect.NEW:
        print("{} joined.".format(self.connect.player.name))

    elif self.tcp.type == self.tcp.CHAT:
      self.chat.ParseFromString(data)
      print("{}: {}".format(self.chat.player.name, self.chat.message))

    elif self.tcp.type == self.tcp.DISCONNECT:
      self.disconnect.ParseFromString(data)
      if self.disconnect.update == self.disconnect.NORMAL:
        print("{} has disconnected.".format(self.disconnect.player.name))
      elif self.disconnect.update == self.disconnect.LOST:
        print("{} lost connection.".format(self.disconnect.player.name))

    else:
      pass

  # Creates lobby
  def createLobbyPacket():
    if input("Create lobby? [Y/N] ").lower() == "y":
      lobby = self.tcp.CreateLobbyPacket()
      lobby.type = self.tcp.CREATE_LOBBY

      print("Enter max players: ", end="")
      lobby.max_players = int(input())

      self.s.send(lobby.SerializeToString())
      data = self.s.recv(BUFFER)
      lobby.ParseFromString(data)
      lobbyID = lobby.lobby_id
    else:
      lobbyID = input("Enter lobby ID: ")

    return lobbyID

  def playerListPacket():
    playerList = self.tcp.PlayerListPacket()
    playerList.type = self.tcp.PLAYER_LIST

    self.s.send(playerList.SerializeToString())
    data = self.s.recv(BUFFER)
    playerList.ParseFromString(data)

    for player in playerList.player_list:
      print("{} is here.".format(player.name))

  def terminate():
    self.isConnected = False
    self.s.shutdown(1)
    self.s.close()

  def helpMenu():
    print("help - Print commands")
    print("players - Print list of connected players")
    print("exit - Disconnect from lobby")

  def writeMessage():
    message = input("Message: ")
    stdout.flush()

    if message.lower() == "help":
      self.helpMenu()
    elif message.lower() == "players":
      self.playerListPacket()
    else:
      self.chat.message = message
      self.s.send(chat.SerializeToString())
