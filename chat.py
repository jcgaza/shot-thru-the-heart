import socket
import player_pb2
import tcp_packet_pb2
import struct

HOST = "202.92.144.45"
PORT = 80
ADDRESS = (HOST, PORT)
tcp = tcp_packet_pb2.TcpPacket()

def mainMenu(option):
  if (option == 1):
    print("[1] Create Lobby")
    print("[2] Join Lobby")
    print("[3] Exit")
  elif (option == 2):
    print("[1] Chat")
    print("[2] Disconnect")

def createLobbyPocket():
  lobby = tcp.CreateLobbyPacket()
  lobby.type = tcp.CREATE_LOBBY

  print("Enter max players: ", end="")
  lobby.max_players = int(input())

  s.send(lobby.SerializeToString())
  data = s.recv(1024)
  lobby.ParseFromString(data)

  print(lobby.lobby_id)

def connectPacket():
  connect = tcp.ConnectPacket()
  connect.type = tcp.CONNECT

  print("Enter lobby ID: ", end="")
  connect.lobby_id = str(input())
  
  newPlayer = player_pb2.Player()
  
  print("Enter player name: ", end="")
  connect.player.name = input()

  s.send(connect.SerializeToString())
  data = s.recv(1024)
  connect.ParseFromString(data)
  print(connect.player)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect(ADDRESS)
  option = 1

  while True:
    mainMenu(option)
    
    print("Choose: ", end="")
    choice = int(input())
    if (option == 1 and choice == 1):
      createLobbyPocket()
      option += 1
    elif (option == 1 and choice == 2):
      connectPacket()
    elif (option == 1 and choice == 3):
      break
    elif (option == 2 and choice == 1):
      connectPacket()
    elif (option == 2 and choice == 2):
      option -= 1