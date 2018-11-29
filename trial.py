from tkinter import *
from ChatClient import ChatClient
from threading import Thread
from sys import exit

largeFont = ('Verdana', 30)
mediumFont = ('Verdana', 20)
BLACK = '#303030'

class MainUI(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Shot Through the Heart")
        self.geometry("350x600+300+300")
        self.frame = None
        self.switchFrame(NamePage)

        self.values = {}
        self.chatClient = ChatClient()
        self.chatThread = None

    def switchFrame(self, frameClass):
        newFrame = frameClass(self)
        if self.frame is not None:
            self.frame.destroy()
        self.frame = newFrame

    def connectToServer(self):
        self.chatClient.connectAndChat(self.values['name'], self.values['lobbyId'])
        self.chatThread = Thread(target=self.chatClient.receiveMessages)
        self.chatThread.start()
        self.switchFrame(ChatInterface)
        
    def exitSystem(self):
        self.chatClient.disconnectChat()
        self.frame.destroy()
        self.destroy()

class NamePage(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.config(bg=BLACK)
        self.pack(fill=BOTH, expand=True)
        self.rowconfigure(1, weight=1, pad=3)
        self.rowconfigure(5, weight=1)
        
        nameLabel = Label(self)
        nameImg = PhotoImage(file="assets/name_label.png")
        nameLabel.config(image=nameImg, highlightthickness=0, bd=0, borderwidth=0, background=BLACK)
        nameLabel.image = nameImg
        nameLabel.grid(row=2, column=0)

        self.name = Entry(self, font=largeFont, relief=FLAT, background="#ffffff", width=13)
        self.name.grid(row=3, column=0, padx=10, pady=10)

        enterBtn = Button(self, text="Enter", activebackground=BLACK, highlightthickness=0, bd=0, borderwidth=0, background=BLACK,
                    command=lambda: self.check())
        enterImg = PhotoImage(file="assets/enter_chat.png")
        enterBtn.config(image=enterImg)
        enterBtn.image = enterImg
        enterBtn.grid(row=4, column=0)

    def check(self):
        name = self.name.get()
        if len(name) != 0:
            self.master.values['name'] = name
            self.master.switchFrame(LobbyPage)

class LobbyPage(Frame):
    def __init__(self, master):
        Frame.__init__(self, master) 
        self.master = master
        self.config(bg=BLACK)
        self.pack(fill=BOTH, expand=True)
        self.rowconfigure(1, weight=1, pad=3)
        self.rowconfigure(5, weight=1, pad=2)
        self.rowconfigure(7, weight=1)

        # TODO: Custom class for label        
        lobbyLabel = Label(self)
        lobbyImg = PhotoImage(file="assets/lobby_id.png")
        lobbyLabel.config(image=lobbyImg, highlightthickness=0, bd=0, borderwidth=0, background=BLACK)
        lobbyLabel.image = lobbyImg
        lobbyLabel.grid(row=2, column=0)

        self.lobbyId = StringVar()
        lobby = Entry(self, font=largeFont, textvariable=self.lobbyId, relief=FLAT, background="#ffffff", width=13)
        lobby.grid(row=3, column=0, padx=10, pady=10)

        # TODO: Custom class for Button
        joinBtn = Button(self, text="Enter", activebackground=BLACK, highlightthickness=0, bd=0, borderwidth=0, background=BLACK,
                        command=lambda: self.checkId())
        joinImg = PhotoImage(file="assets/join_lobby.png")
        joinBtn.config(image=joinImg)
        joinBtn.image = joinImg
        joinBtn.grid(row=4, column=0)

        orLabel = Label(self)
        orImg = PhotoImage(file="assets/or.png")
        orLabel.config(image=orImg, highlightthickness=0, bd=0, borderwidth=0, background=BLACK)
        orLabel.image = orImg
        orLabel.grid(row=6, column=0, pady=2)

        createBtn = Button(self, text="Enter", activebackground=BLACK, highlightthickness=0, bd=0, borderwidth=0, background=BLACK,
                            command=lambda: self.createLobbyWindow())
        createImg = PhotoImage(file="assets/create_lobby.png")
        createBtn.config(image=createImg)
        createBtn.image = createImg
        createBtn.grid(row=7, column=0, pady=2)
    
    def checkId(self):
        if len(self.lobbyId.get()) != 0:
            self.master.values['lobbyId'] = self.lobbyId.get()
            self.master.connectToServer()

    def createLobbyWindow(self):
        win = Toplevel()
        win.wm_title("Create Lobby")
        win.geometry("350x350")
        win.config(bg=BLACK)
        win.columnconfigure(0, weight=1, pad=1)
        win.rowconfigure(1, weight=1, pad=3)
        win.rowconfigure(5, weight=1)

        label = Label(win, font=mediumFont, text="Max. Number of Players", fg="white", bg=BLACK)
        label.grid(row=2, column=0)

        # TODO: Validate!
        txtInput = Entry(win, font=mediumFont, relief=FLAT, background="#ffffff", width=13)
        txtInput.grid(row=3, column=0, pady=10)

        btn = Button(win, text="Enter", activebackground=BLACK, highlightthickness=0, bd=0, borderwidth=0, background=BLACK,
                    command=lambda: checkNum())
        btnimg = PhotoImage(file="assets/create_lobby.png")
        btn.config(image=btnimg)
        btn.image = btnimg
        btn.grid(row=4, column=0)
    
        def isInt(str):
            try:
                int(str)
                return True
            except:
                return False
        
        def checkNum():
            if isInt(txtInput.get()):
                self.lobbyId.set(self.master.chatClient.createLobby(int(txtInput.get())))
                win.destroy()

class ChatInterface(Frame):
    def __init__(self, master):
        Frame.__init__(self, master) 
        self.config(bg=BLACK)
        self.pack(fill=BOTH, expand=True)
        self.master = master
        self.master.chatClient.printToUI = self.send_message_insert

        upper = Frame(self, bg=BLACK)
        upper.pack(fill=BOTH)
        lobbyID = Label(upper, text="Lobby ID: " + self.master.values['lobbyId'], bg=BLACK, fg="white")
        lobbyID.pack(side=LEFT, padx=10, pady=(10,0))
        
        exitButton = Button(upper, text="Exit", width=5, relief=FLAT, bg='white', command=lambda: self.exitAction())
        exitButton.pack(side=RIGHT, padx=10, pady=(10,0))
        
        self.text_frame = Frame(self, bd=6, bg=BLACK)
        self.text_frame.pack(expand=True, fill=BOTH)

        # scrollbar for text box
        self.text_box_scrollbar = Scrollbar(self.text_frame, bd=0)
        self.text_box_scrollbar.pack(fill=Y, side=RIGHT, pady=10, padx=(0,10))

        # contains messages
        self.text_box = Text(self.text_frame, yscrollcommand=self.text_box_scrollbar.set, state=DISABLED,
                             bd=1, padx=6, pady=6, spacing3=8, wrap=WORD, bg="#ffffff", font="Verdana 10", relief=FLAT,
                             width=10, height=1)
        self.text_box.pack(expand=True, fill=BOTH, pady=10, padx=(10,0))
        self.text_box_scrollbar.config(command=self.text_box.yview)

        # frame containing user entry field
        self.entry_frame = Frame(self, bd=1, bg=BLACK)
        self.entry_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # entry field
        self.entry_field = Entry(self.entry_frame, bd=1, justify=LEFT, relief=FLAT, background="#ffffff")
        self.entry_field.pack(fill=X, padx=10, pady=6, ipady=3)

        # frame containing send button and emoji button
        self.send_button_frame = Frame(self, bd=0, bg=BLACK)
        self.send_button_frame.pack(fill=BOTH)

        # send button
        self.send_button = Button(self.send_button_frame, text="Send", width=5, relief=FLAT, bg='white', command=lambda: self.send_message(self.master.values['name']))
        self.send_button.pack(side=LEFT, ipady=2, padx=10)

    def send_message(self, username):
        user_input = self.entry_field.get()
        self.master.chatClient.writeMessage(user_input)
        self.entry_field.delete(0, END)
    
    def send_message_insert(self, user, message):
        self.text_box.configure(state=NORMAL)
        if user is None:
            self.text_box.insert(END, message + '\n')
        else:
            self.text_box.insert(END, user + ': ' + message + '\n')

        self.text_box.see(END)
        self.text_box.configure(state=DISABLED)

    def exitAction(self):
        self.master.exitSystem()

if __name__ == '__main__':
    app = MainUI()
    app.mainloop()