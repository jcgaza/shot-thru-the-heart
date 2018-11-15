import socket
import player_pb2
import tcp_packet_pb2

from threading import Thread

HOST = "202.92.144.45"
PORT = 80
BUFFER = 1024
ADDRESS = (HOST, PORT)

tcp = tcp_packet_pb2.TcpPacket()
connect = tcp.ConnectPacket()
connect.type = tcp.CONNECT

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect(ADDRESS)

  # Create Lobby Packet
  if input("Create lobby? [Y/N] ").lower() == "y":
    lobby = tcp.CreateLobbyPacket()
    lobby.type = tcp.CREATE_LOBBY

    print("Enter max players: ", end="")
    lobby.max_players = int(input())

    s.send(lobby.SerializeToString())
    data = s.recv(1024)
    lobby.ParseFromString(data)
    lobbyID = lobby.lobby_id
  else:
    lobbyID = input("Enter lobby ID: ")
    # TODO: add error LDNE here

  print("You're in Lobby {}.".format(lobbyID))
  # Connect Packet
  tcp.type = tcp.CONNECT
  connect.player.name = input("Enter name: ")
  connect.lobby_id = lobbyID

  s.send(connect.SerializeToString())
  
  chat = tcp.ChatPacket()
  chat.type = tcp.CHAT
  chat.player.name = connect.player.name

  def parser(data):
    tcp.ParseFromString(data)

    if (tcp.type == tcp.CONNECT):
      connect.ParseFromString(data)
      print("{} joined.".format(connect.player.name))
    elif (tcp.type == tcp.CHAT):
      chat.ParseFromString(data)
      print("{}: {}".format(chat.player.name, chat.message))

  def receivePacket(parser):
    while True:
      try:
        data = s.recv(BUFFER)
        parser(data)
      except OSError:
        break

  receiver = Thread(target=receivePacket, args=[parser])
  receiver.start()

  while True:
    message = input("Message: ")
    chat.message = message
    s.send(chat.SerializeToString())