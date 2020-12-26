import threading

import grpc

from ..proto import serverchat_pb2 as schat_pb2
from ..proto import serverchat_pb2_grpc as schat_pb2_grpc
from .serverconnection import ServerConnection


def print_info(action):
    if action.action_type == schat_pb2.Action.ActionType.CONNECT:
        print('User {} is connected to the server'.format(action.username))
    elif action.action_type == schat_pb2.Action.ActionType.DISCONNECT:
        print('User {} is disconnected from the server'.format(action.username))
    elif action.action_type == schat_pb2.Action.ActionType.SEND_MESSAGE:
        print('{} > {}'.format(action.username, action.playload))


def start():
    username = input('Enter username:')
    chat_server = ServerConnection('localhost:50051')
    chat_server.start_message_listener(print_info)
    chat_server.connect_user(username)

    try:
        while True:
            text = input('< ')
            chat_server.send_message(text)
    except KeyboardInterrupt:
        chat_server.disconnect_user()
        chat_server.cleanup()