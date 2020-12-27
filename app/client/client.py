from datetime import datetime
import tkinter as tk
import tkinter.simpledialog

from ..proto import serverchat_pb2 as schat_pb2
from ..proto import serverchat_pb2_grpc as schat_pb2_grpc
from .serverconnection import ServerConnection


class Client():

    def __init__(self, target):
        self.server = ServerConnection(target)
        # create root window
        self.root = tk.Tk()
        self.root.geometry('300x400')
        # hide window
        self.root.withdraw()
        # add handling for window close
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.exit)

        # create widgets
        self.chat_text = tk.Text()
        self.chat_text.tag_config(
            'connect', 
            foreground='green4')
        self.chat_text.tag_config(
            'disconnect', 
            foreground='red4')

        self.username_label = tk.Label( 
            width=10, 
            anchor=tk.E)
        
        self.message_entry = tk.Entry()
        self.message_entry.bind('<Return>', self.send_message_action)
        self.message_entry.focus()
        
        self.send_button = tk.Button(text='Send')
        self.send_button.config(command=self.send_message_action)

        # place widgets on window
        self.chat_text.pack(expand=True, fill=tk.BOTH)
        self.username_label.pack(side=tk.LEFT)
        self.message_entry.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.send_button.pack(side=tk.LEFT)

    def start(self):
        username = self.get_username()
        self.username_label.config(text=f'{username}: ')
        self.server.connect_user(username)
        self.server.start_message_listener(self.handle_action)
        # show window
        self.root.deiconify()
        self.root.mainloop()

    def get_username(self):
        username = None
        while username is None:
            username = tk.simpledialog.askstring(
                "Username", 
                "Enter username:", 
                parent=self.root)
        return username

    def send_message_action(self, event=None):
        message = self.message_entry.get()
        # clear the field
        self.message_entry.delete(0, tk.END)
        self.server.send_message(message)

    def handle_action(self, action):
        if action.action_type == schat_pb2.Action.ActionType.CONNECT:
            self.add_connect_message(action.username)
        elif action.action_type == schat_pb2.Action.ActionType.DISCONNECT:
            self.add_disconnect_message(action.username)
        elif action.action_type == schat_pb2.Action.ActionType.SEND_MESSAGE:
            self.add_new_message(action.username, action.payload)

    def get_time_string(self):
        return datetime.now().strftime('[%H:%M]')

    def add_connect_message(self, username):
        time = self.get_time_string()
        msg = f'<{username}> connected to the server\n'
        text = ''.join([time, ' ', msg])
        self.chat_text.insert(tk.END, text, 'connect')

    def add_disconnect_message(self, username):
        time = self.get_time_string()
        msg = f'<{username}> disconnected from the server\n'
        text = ''.join([time, ' ', msg])
        self.chat_text.insert(tk.END, text, 'disconnect')

    def add_new_message(self, username, message):
        time = self.get_time_string()
        msg = f'<{username}> {message}\n'
        text = ''.join([time, ' ', msg])
        self.chat_text.insert(tk.END, text)


    def exit(self):
        self.server.cleanup()
        self.root.destroy()
        exit(0)