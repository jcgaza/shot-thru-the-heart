import socket
import select
import player_pb2
import tcp_packet_pb2

from threading import Thread
from sys import exit, stdout

HOST = "202.92.144.45"
PORT = 80
BUFFER = 1024
ADDRESS = (HOST, PORT)

tcp = tcp_packet_pb2.TcpPacket()
connect = tcp.ConnectPacket()
connect.type = tcp.CONNECT

# Checking data received
def parser(data):
  tcp.ParseFromString(data)

  if tcp.type == tcp.CONNECT:
    connect.ParseFromString(data)
    if connect.update == connect.NEW:
      print("{} joined.".format(connect.player.name))

  elif tcp.type == tcp.CHAT:
    chat.ParseFromString(data)
    print("{}: {}".format(chat.player.name, chat.message))

  elif tcp.type == tcp.DISCONNECT:
    disconnect.ParseFromString(data)
    if disconnect.update == disconnect.NORMAL:
      print("{} has disconnected.".format(disconnect.player.name))
    elif disconnect.update == disconnect.LOST:
      print("{} lost connection.".format(disconnect.player.name))

  else:
    pass

# For receiving messages
# def receivePacket(parser):
#   while isConnected:
#     try:
#       read_sockets, write_sockets, error_sockets = select.select([s], [], [])

#       for sock in read_sockets:
#         if sock == s:
#           data = s.recv(BUFFER)
          
#           if not data:
#             print("You have disconnected.")
#             terminate()
#           else:
#             parser(data)
#         else:
#           writeMessage()
#     except OSError:
#       break
#     except ValueError:
#       break

# Creates lobby
def createLobbyPacket():
  if input("Create lobby? [Y/N] ").lower() == "y":
    lobby = tcp.CreateLobbyPacket()
    lobby.type = tcp.CREATE_LOBBY

    print("Enter max players: ", end="")
    lobby.max_players = int(input())

    s.send(lobby.SerializeToString())
    data = s.recv(BUFFER)
    lobby.ParseFromString(data)
    lobbyID = lobby.lobby_id
  else:
    lobbyID = input("Enter lobby ID: ")

  return lobbyID

# Returns players connected
def playerListPacket():
  playerList = tcp.PlayerListPacket()
  playerList.type = tcp.PLAYER_LIST

  s.send(playerList.SerializeToString())
  data = s.recv(BUFFER)
  playerList.ParseFromString(data)

  for player in playerList.player_list:
    print("{} is here.".format(player.name))

def disconnectPacket():
  s.send(disconnect.SerializeToString())

# Print commands
def helpMenu():
  print("help - Print commands")
  print("players - Print list of connected players")
  print("exit - Disconnect from lobby")

def writeMessage():
  message = input("Message: ")
  stdout.flush()

  if message.lower() == "help":
    helpMenu()
  elif message.lower() == "players":
    playerListPacket()
  elif message.lower() == "exit":
    disconnectPacket()
  else:
    chat.message = message
    s.send(chat.SerializeToString())

def terminate():
  isConnected = False
  s.shutdown(1)
  s.close()

### MAIN

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect(ADDRESS)

  # Disconnect Packet
  disconnect = tcp.DisconnectPacket()
  disconnect.type = tcp.DISCONNECT

  # Connect Packet
  tcp.type = tcp.CONNECT
  connect.player.name = input("Enter name: ")
  
  lobbyID = createLobbyPacket()
  connect.lobby_id = lobbyID

  s.send(connect.SerializeToString())
  data = s.recv(BUFFER)
  tcp.ParseFromString(data)

  # ERR_LDNE Packet
  if tcp.type == tcp.ERR_LDNE:
    print("Lobby does not exist.")
    exit()

  # ERR_LFULL Packet
  elif tcp.type == tcp.ERR_LFULL:
    print("Lobby is full!")
    exit()

  print("You're in Lobby {}.".format(lobbyID))
  isConnected = True

  # Chat Packet
  chat = tcp.ChatPacket()
  chat.type = tcp.CHAT
  chat.player.name = connect.player.name

  helpMenu()

  # For receiving messages
  # receiver = Thread(target=receivePacket, args=[parser])
  # receiver.start()

  while isConnected:
    try:
      read_sockets, write_sockets, error_sockets = select.select([0,s], [], [])

      for sock in read_sockets:
        if sock == s:
          data = s.recv(BUFFER)
          
          if not data:
            print("You have disconnected.")
            terminate()
          else:
            parser(data)
        else:
          writeMessage()
    except ValueError:
      break
    except OSError:
      break
