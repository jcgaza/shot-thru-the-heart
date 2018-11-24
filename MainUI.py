from tkinter import *
from ChatUI import *

root = Tk()
root.title("Shot Thru the Heart Chat")
root.geometry("400x250+0+0")

serverName = StringVar()
numPlayers = StringVar()
name = StringVar()

heading = Label(root, text="Welcome!", font=("arial", 40, "bold"), fg="steelblue").place(x=100,y=30)
label1 = Label(root, text="Enter your name: ", font=("arial", 14, "bold"), fg="black").place(x=30, y=100)

enterName = Entry(root, textvariable=name, width=20, bg="white").place(x=170, y=100)

def openChat(lobbyID, maxNum):
	chatWindow = Toplevel(root)
	chatWindow.geometry("400x300")
	chat = ChatInterface(name.get(), lobbyID, maxNum, chatWindow)

def max_players():
	maxPlayersWindow = Toplevel(root)
	maxPlayersWindow.geometry("300x200+0+0")
	text_input = Label(maxPlayersWindow, text="How many players? ", font=("arial", 14, "bold"), fg="black").place(x=70, y=60)
	enterPlayers = Entry(maxPlayersWindow, textvariable=numPlayers, width=20, bg="white").place(x=70, y=90)
	enterServer = Button(maxPlayersWindow, text="Join Server", width=10, height=3, bg="grey", command=lambda: openChat(None, int(numPlayers.get())) ).place(x=90, y=120)

def join_server():
	joinServerWindow = Toplevel(root)
	joinServerWindow.geometry("300x200+0+0")
	text_input = Label(joinServerWindow, text="Enter Server: ", font=("arial", 14, "bold"), fg="black").place(x=30, y=70)
	enter_server = Entry(joinServerWindow, textvariable=serverName, width=15, bg="white").place(x=130, y=70)
	enterServer = Button(joinServerWindow, text="Join Server", width=10, height=3, bg="grey", command=lambda: openChat(serverName.get(), None)).place(x=90, y=110)

createServer = Button(root, text="Create Server", width=10, height=5, bg="grey", command=max_players).place(x=70, y=130)
joinServer = Button(root, text="Join Server", width=10, height=5, bg="grey", command=join_server).place(x=200, y=130)



root.mainloop()