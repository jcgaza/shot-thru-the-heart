from tkinter import *

root = Tk()
root.title("Shot Thru the Heart Chat")
root.geometry("400x250+0+0")

server_name = StringVar()
name = StringVar()

heading = Label(root, text="Welcome!", font=("arial", 40, "bold"), fg="steelblue").place(x=100,y=30)
label1 = Label(root, text="Enter your name: ", font=("arial", 14, "bold"), fg="black").place(x=30, y=100)

enterName = Entry(root, textvariable=name, width=20, bg="white").place(x=170, y=100)

def server():
	import ChatUI

def max_players():
	maxPlayersWindow = Toplevel(root)
	maxPlayersWindow.geometry("300x200+0+0")
	text_input = Label(maxPlayersWindow, text="How many players? ", font=("arial", 14, "bold"), fg="black").place(x=70, y=70)
	player1 = Button(maxPlayersWindow, text="1", width=3, height=3, bg="grey", command=server).place(x=20, y=110)
	player2 = Button(maxPlayersWindow, text="2", width=3, height=3, bg="grey", command=server).place(x=80, y=110)
	player3 = Button(maxPlayersWindow, text="3", width=3, height=3, bg="grey", command=server).place(x=140, y=110)
	player4 = Button(maxPlayersWindow, text="4", width=3, height=3, bg="grey", command=server).place(x=200, y=110)

def create_server():
	import ChatUI

def join_server():
	joinServerWindow = Toplevel(root)
	joinServerWindow.geometry("300x200+0+0")
	text_input = Label(joinServerWindow, text="Enter Server: ", font=("arial", 14, "bold"), fg="black").place(x=30, y=70)
	enter_server = Entry(joinServerWindow, textvariable=server_name, width=15, bg="white").place(x=130, y=70)
	enterServer = Button(joinServerWindow, text="Join Server", width=10, height=3, bg="grey", command=server).place(x=90, y=110)

createServer = Button(root, text="Create Server", width=10, height=5, bg="grey", command=max_players).place(x=70, y=130)
joinServer = Button(root, text="Join Server", width=10, height=5, bg="grey", command=join_server).place(x=200, y=130)



root.mainloop()