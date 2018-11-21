from tkinter import *
import time
import re
import os
import string
import webbrowser
#import ChatClient

#saved_lobby = ["CMSC137"]
saved_username = ["You"]

# checks if username file exists, if not, makes one.
if not os.path.isfile("usernames.txt"):
    # doesnt exist, creates usernames.txt file
    print('"username.txt" file doesn\'t exist. Creating new file.')
    with open ("usernames.txt", 'wb') as file:
        pass

else:
    # file exists, takes all existing usernames stored in file and adds them to saved_username list
    print('"username.txt" file found.')
    with open("usernames.txt", 'r') as file:
        for line in file:
            saved_username.append(line.replace("\n", ""))
    pass

# checks if default_win_size file exists, if not, makes one.
if not os.path.isfile("default_win_size.txt"):
    # doesnt exist, creates default_win_size.txt file
    print('"default_win_size.txt" file doesn\'t exist. Creating new file.')
    with open("default_win_size.txt", 'wb') as file:
        pass

    default_window_size = "400x300"

else:
    # file exists, takes existing window size and defines it
    print('"default_win_size.txt" file found.')
    with open("default_win_size.txt", 'r') as file:
        size = file.readlines()
        default_window_size= ''.join(size)


class ChatInterface(Frame):

    def __init__(self, master=None):
        #self.chat = ChatClient()
        Frame.__init__(self, master)
        self.master = master

        # sets default bg for top level windows
        self.tl_bg = "#EEEEEE"
        self.tl_bg2 = "#EEEEEE"
        self.tl_fg = "#000000"
        self.font = "Verdana 10"

        menu = Menu(self.master)
        self.master.config(menu=menu, bd=5)
# Menu bar
    # File
        file = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Save Chat Log", command=self.save_chat)
        file.add_command(label="Clear Chat", command=self.clear_chat)
        file.add_command(label="Lobby No. ")
        file.add_separator()
        file.add_command(label="Exit", command=self.client_exit)

    # Options
        options = Menu(menu, tearoff=0)
        menu.add_cascade(label="Options", menu=options)

        # username
        username = Menu(options, tearoff=0)
        options.add_cascade(label="Username", menu=username)
        username.add_command(label="Change Username", command=lambda: self.change_username(height=80))
        username.add_command(label="Default Username", command=self.default_username)
        username.add_command(label="View Username History", command=self.view_username_history)
        username.add_command(label="Clear Username History", command=self.clear_username_history)

        options.add_separator()

        # font
        font = Menu(options, tearoff=0)
        options.add_cascade(label="Font", menu=font)
        font.add_command(label="Default", command=self.font_change_default)
        font.add_command(label="Times", command=self.font_change_times)
        font.add_command(label="System", command=self.font_change_system)
        font.add_command(label="Helvetica", command=self.font_change_helvetica)
        font.add_command(label="Fixedsys", command=self.font_change_fixedsys)
     
        # all to default
        options.add_command(label="Default layout", command=self.default_format)

        options.add_separator()

        # change default window size
        # change default window size
        options.add_command(label="Change Default Window Size", command=self.change_default_window_size)

        # default window size
        options.add_command(label="Default Window Size", command=self.default_window_size)

    # Chat interface
        # frame containing text box with messages and scrollbar
        self.text_frame = Frame(self.master, bd=6)
        self.text_frame.pack(expand=True, fill=BOTH)

        # scrollbar for text box
        self.text_box_scrollbar = Scrollbar(self.text_frame, bd=0)
        self.text_box_scrollbar.pack(fill=Y, side=RIGHT)

        # contains messages
        self.text_box = Text(self.text_frame, yscrollcommand=self.text_box_scrollbar.set, state=DISABLED,
                             bd=1, padx=6, pady=6, spacing3=8, wrap=WORD, bg=None, font="Verdana 10", relief=GROOVE,
                             width=10, height=1)
        self.text_box.pack(expand=True, fill=BOTH)
        self.text_box_scrollbar.config(command=self.text_box.yview)

        # frame containing user entry field
        self.entry_frame = Frame(self.master, bd=1)
        self.entry_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # entry field
        self.entry_field = Entry(self.entry_frame, bd=1, justify=LEFT)
        self.entry_field.pack(fill=X, padx=6, pady=6, ipady=3)
        # self.users_message = self.entry_field.get()

        # frame containing send button and emoji button
        self.send_button_frame = Frame(self.master, bd=0)
        self.send_button_frame.pack(fill=BOTH)

        # send button
        self.send_button = Button(self.send_button_frame, text="Send", width=5, relief=GROOVE, bg='white',
                                  bd=1, command=lambda: self.send_message(None), activebackground="#FFFFFF",
                                  activeforeground="#000000")
        self.send_button.pack(side=LEFT, ipady=2)
        self.master.bind("<Return>", self.send_message_event)

    
    def last_sent_label(self, date):

        try:
            self.sent_label.destroy()
        except AttributeError:
            pass

        self.sent_label = Label(self.entry_frame, font="Verdana 7", text=date, bg=self.tl_bg2, fg=self.tl_fg)
        self.sent_label.pack(side=LEFT, fill=X, padx=3)



# File functions
    def client_exit(self):
        exit()

    def save_chat(self):
        # creates unique name for chat log file
        time_file = str(time.strftime('%X %x'))
        remove = ":/ "
        for var in remove:
            time_file = time_file.replace(var, "_")

        # gets current directory of program. creates "logs" folder to store chat logs.
        path = os.getcwd() + "\\logs\\"
        new_name = path + "log_" + time_file
        saved = "Chat log saved to {}\n".format(new_name)

        # saves chat log file
        try:
            with open(new_name, 'w')as file:
                self.text_box.configure(state=NORMAL)
                log = self.text_box.get(1.0, END)
                file.write(log)
                self.text_box.insert(END, saved)
                self.text_box.see(END)
                self.text_box.configure(state=DISABLED)

        except UnicodeEncodeError:
            # displays error when trying to save chat with unicode. (fix in future)
            self.error_window("Unfortunately this chat can't be saved as of this \nversion "
                              "because it contains unicode characters.", type="simple_error", height='100')

    # clears chat
    def clear_chat(self):
        self.text_box.config(state=NORMAL)
        self.last_sent_label(date="No messages sent.")
        self.text_box.delete(1.0, END)
        self.text_box.delete(1.0, END)
        self.text_box.config(state=DISABLED)


# Help functions
    def features_msg(self):
        msg_box = Toplevel()
        msg_box.configure(bg=self.tl_bg)

# creates top level window with error message
    def error_window(self, error_msg, type="simple_error", height='100', button_msg="Okay"):
        # try's to destroy change username window if its an error with username content
        try:
            self.change_username_window.destroy()
        except AttributeError:
            pass

        # makes top level with placement relative to root and specified error msg
        self.error_window_tl = Toplevel(bg=self.tl_bg)
        self.error_window_tl.focus_set()
        self.error_window_tl.grab_set()

        # gets main window width and height to position change username window
        half_root_width = root.winfo_x()
        half_root_height = root.winfo_y() + 60
        placement = '400x' + str(height) + '+' + str(int(half_root_width)) + '+' + str(int(half_root_height))
        self.error_window_tl.geometry(placement)

        too_long_frame = Frame(self.error_window_tl, bd=5, bg=self.tl_bg)
        too_long_frame.pack()

        self.error_scrollbar = Scrollbar(too_long_frame, bd=0)
        self.error_scrollbar.pack(fill=Y, side=RIGHT)

        error_text = Text(too_long_frame, font=self.font, bg=self.tl_bg, fg=self.tl_fg, wrap=WORD, relief=FLAT,
                          height=round(int(height)/30), yscrollcommand=self.error_scrollbar.set)
        error_text.pack(pady=6, padx=6)
        error_text.insert(INSERT, error_msg)
        error_text.configure(state=DISABLED)
        self.error_scrollbar.config(command=self.text_box.yview)

        button_frame = Frame(too_long_frame, width=12)
        button_frame.pack()

        okay_button = Button(button_frame, relief=GROOVE, bd=1, text=button_msg, font=self.font, bg=self.tl_bg,
                             fg=self.tl_fg, activebackground=self.tl_bg, width=5, height=1,
                             activeforeground=self.tl_fg, command=lambda: self.close_error_window(type))
        okay_button.pack(side=LEFT, padx=5)

        if type == "username_history_error":
            cancel_button = Button(button_frame, relief=GROOVE, bd=1, text="Cancel", font=self.font, bg=self.tl_bg,
                             fg=self.tl_fg, activebackground=self.tl_bg, width=5, height=1,
                             activeforeground=self.tl_fg, command=lambda: self.close_error_window("simple_error"))
            cancel_button.pack(side=RIGHT, padx=5)

# Send Message

    # allows user to hit enter instead of button to change username
    def change_username_main_event(self, event):
        saved_username.append(self.username_entry.get())
        self.change_username_main(username=saved_username[-1])

        # gets passed username from input

    def change_username_main(self, username, default=False):

        # takes saved_username list and writes all usernames into text file
        def write_usernames():
            with open('usernames.txt', 'w') as filer:
                for item in saved_username:
                    filer.write(item + "\n")

        # ensures username contains only letters and numbers
        found = False
        for char in username:
            if char in string.punctuation:
                found = True

        if found is True:
            saved_username.remove(username)
            self.error_window("Your username must contain only letters and numbers.", type="username_error",
                              height='100')
        # username length limiter (limits to 20 characters or less and greater than 1 character)
        elif len(username) > 20:
            saved_username.remove(username)
            self.error_window("Your username must be 20 characters or less.", type="username_error", height='100')

        elif len(username) < 2:
            saved_username.remove(username)
            self.error_window("Your username must be 2 characters or more.", type="username_error", height='100')

        # detects if user entered already current username
        elif len(saved_username) >= 2 and username == saved_username[-2]:
            self.error_window("That is already your current username!", type="username_error", height='100')

        # used to detect when user wants default username.
        else:
            # closes change username window, adds username to list, and displays notification
            self.close_username_window()
            write_usernames()
            self.send_message_insert("Username changed to " + '"' + username + '".')

    # allows "enter" key for sending msg
    def send_message_event(self, event):
        user_name = saved_username[-1]
        self.send_message(user_name)

    # joins username with message into publishable format
    def send_message(self, username):

        user_input = self.entry_field.get()

        username = saved_username[-1] + ": "
        message = (username, user_input)
        readable_msg = ''.join(message)
        readable_msg.strip('{')
        readable_msg.strip('}')

        # clears entry field, passes formatted msg to send_message_insert
        if user_input != '':
            self.entry_field.delete(0, END)
            self.send_message_insert(readable_msg)

    # inserts user input into text box
    def send_message_insert(self, message):
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, message + '\n')
        self.last_sent_label(str(time.strftime( "Last message sent: " + '%B %d, %Y' + ' at ' + '%I:%M %p')))
        self.text_box.see(END)
        self.text_box.configure(state=DISABLED)

    # closes change username window
    def close_username_window(self):
        self.change_username_window.destroy()

    # decides type of error when i create an error window ( re-open change username window or not)
    def close_error_window(self, type):
        if type == "username_error":
            self.error_window_tl.destroy()
            self.change_username(height=80)
        elif type == "dimension_error":
            self.error_window_tl.destroy()
            self.change_username(type="window_size", label='Enter "width x height" \n'
                                                           "ex: 500x500", height=125)
        elif type == "simple_error":
            self.error_window_tl.destroy()
        elif type == "username_history_error":
            self.error_window_tl.destroy()
            self.clear_username_history_confirmed()
        else:
            print("You gave an unknown error type.")

# Font options
    def font_change_default(self):
        self.text_box.config(font="Verdana 10")
        self.entry_field.config(font="Verdana 10")
        self.font = "Verdana 10"

    def font_change_times(self):
        self.text_box.config(font="Times")
        self.entry_field.config(font="Times")
        self.font = "Times"

    def font_change_system(self):
        self.text_box.config(font="System")
        self.entry_field.config(font="System")
        self.font = "System"

    def font_change_helvetica(self):
        self.text_box.config(font="helvetica 10")
        self.entry_field.config(font="helvetica 10")
        self.font = "helvetica 10"

    def font_change_fixedsys(self):
        self.text_box.config(font="fixedsys")
        self.entry_field.config(font="fixedsys")
        self.font = "fixedsys"


    # Default font and color theme
    def default_format(self):
        self.font_change_default()
        self.color_theme_default()

# Change Username or window size window
    def change_username(self, type="username", label=None, height=None):
        self.change_username_window = Toplevel()

        if type == "username":
            self.change_username_window.bind("<Return>", self.change_username_main_event)
        elif type == "window_size":
            self.change_username_window.bind("<Return>", self.change_window_size_event)

        self.change_username_window.configure(bg=self.tl_bg)
        self.change_username_window.focus_set()
        self.change_username_window.grab_set()

        # gets main window width and height to position change username window
        half_root_width = root.winfo_x()+100
        half_root_height = root.winfo_y()+60
        placement = '180x' + str(height) + '+' + str(int(half_root_width)) + '+' + str(int(half_root_height))
        self.change_username_window.geometry(placement)

        # frame for entry field
        enter_username_frame = Frame(self.change_username_window, bg=self.tl_bg)
        enter_username_frame.pack(pady=5)

        if label:
            self.window_label = Label(enter_username_frame, text=label, fg=self.tl_fg)
            self.window_label.pack(pady=4, padx=4)

        self.username_entry = Entry(enter_username_frame, width=22, bg=self.tl_bg, fg=self.tl_fg, bd=1,
                      insertbackground=self.tl_fg)
        self.username_entry.pack(pady=3, padx=10)

        # Frame for Change button and cancel button
        buttons_frame = Frame(self.change_username_window, bg=self.tl_bg)
        buttons_frame.pack()

    # implement username/ size
        if type == "username":
            username_command = lambda: self.change_username_main(self.username_entry.get())
        elif type == "window_size":
            username_command = lambda: self.change_window_size_main(self.username_entry.get())

        change_button = Button(buttons_frame, relief=GROOVE, text="Change", width=8, bg=self.tl_bg, bd=1,
                               fg=self.tl_fg, activebackground=self.tl_bg, activeforeground=self.tl_fg,
                               command=username_command)
        change_button.pack(side=LEFT, padx=4, pady=3)


    # cancel
        cancel_button = Button(buttons_frame, relief=GROOVE, text="Cancel", width=8, bg=self.tl_bg, bd=1,
                               fg=self.tl_fg, command=self.close_username_window,
                               activebackground=self.tl_bg, activeforeground=self.tl_fg)
        cancel_button.pack(side=RIGHT, padx=4, pady=3)

# Use default username ("You")
    def default_username(self):
        saved_username.append("You")
        self.send_message_insert("Username changed to default.")

# promps user to Clear username history (deletes usernames.txt file and clears saved_username list)
    def clear_username_history(self):
        self.error_window(error_msg="Are you sure you want to clear your username history?\n", button_msg="Clear",
                          type="username_history_error", height="120")

    def clear_username_history_confirmed(self):
         os.remove("usernames.txt")
         saved_username.clear()
         saved_username.append("You")

         self.send_message_insert("Username history cleared.")

# opens window showing username history (possible temp feature)
    def view_username_history(self):
        with open("usernames.txt", 'r') as usernames:
            view_usernames = str(usernames.readlines())

        view_usernames = re.sub("[\[\]']", "", view_usernames)
        view_usernames = view_usernames.replace("\\n", "")

        self.error_window(error_msg="Username History: \n\n" + view_usernames, type="simple_error",
                          button_msg="Close", height='150')

# Change Default Window Size
    # called from options, creates window to input dimensions
    def change_default_window_size(self):
        self.change_username(type="window_size", label='Enter "width x height" \n'
                                                       "ex: 500x500", height=125)

    # event window, also gets input and checks if it's valid to use as dimensions
    def change_window_size_event(self, event):
        dimensions_get = self.username_entry.get()

        listed = list(dimensions_get)
        try:
            x_index = listed.index("x")

            # formats height and width into seperate int's
            num_1 = int(''.join(listed[0:x_index]))
            num_2 = int(''.join(listed[x_index + 1:]))

        except ValueError or UnboundLocalError:
            self.error_window(
                error_msg="Invalid dimensions specified. \nPlease Use the format shown in the example.",
                type="dimension_error", height='125')
            self.close_username_window()

        # checks that its not too big or too small
        try:
            if num_1 > 3840 or num_2 > 2160 or num_1 < 360 or num_2 < 200:
                self.error_window(error_msg="Dimensions you specified are invalid.\n"
                                            "Maximum dimensions are 3840 x 2160. \n"
                                            "Minimum dimensions are 360 x 200.",
                                  type="dimension_error", height="140")
            else:
                self.change_window_size_main(dimensions_get)
        except:
            pass

    # change size and saves new default into txt file to remember across sessions
    def change_window_size_main(self, window_size):
        window_size = window_size.lower().replace(" ", "")

        root.geometry(window_size)

        with open("default_win_size.txt", 'w') as file:
            print("New default window size set: " + window_size)
            file.write(window_size)

        self.close_username_window()

        self.send_message_insert("Default window size changed to " + window_size + ".")

# return to default window size
    def default_window_size(self):

        # gets custom default win size from file
        with open("default_win_size.txt", 'r') as file:
            size = file.readlines()
            default_window_size = ''.join(size)

        root.geometry(default_window_size)
        print(default_window_size)

        # scrolls to very bottom of textbox
        def see_end():
            self.text_box.configure(state=NORMAL)
            self.text_box.see(END)
            self.text_box.configure(state=DISABLED)
        root.after(10, see_end)

root = Tk()
root.title("Shot-Thru-The-Heart")
root.geometry(default_window_size)
print(default_window_size)
root.minsize(360,200)

a = ChatInterface(root)

root.mainloop()
