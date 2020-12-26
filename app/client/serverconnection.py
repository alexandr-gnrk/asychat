import grpc
import threading

from ..proto import serverchat_pb2 as schat_pb2
from ..proto import serverchat_pb2_grpc as schat_pb2_grpc


class ServerConnection():

    def __init__(self, target):
        self.target = target
        self.channel = grpc.insecure_channel(self.target)
        self.stub = schat_pb2_grpc.ServerChatStub(self.channel)
        self.token = None

    def connect_user(self, username):
        conn_resp = self.stub.connect(
            schat_pb2.ConnectionRequest(
                username=username))
        self.token = conn_resp.user_token
        return conn_resp.status

    def disconnect_user(self):
        status = self.stub.disconnect(
            schat_pb2.DisconnectionRequest(
                user_token=self.token))
        self.token = None
        return status

    def send_message(self, text):
        status = self.stub.send_message(
            schat_pb2.Message(
                user_token=self.token,
                text=text))
        return status

    def actions_listener(self, callback):
        try:
            for action in self.stub.get_chat_stream(schat_pb2.Empty()):
                callback(action)
        except grpc._channel._MultiThreadedRendezvous:
            # connection is closed
            return

    def start_message_listener(self, callback):
        threading.Thread(
            target=self.actions_listener, 
            args=(callback,)).start()

    def cleanup(self):
        if self.channel is not None:
            if self.token is not None:
                self.disconnect_user()
            self.channel.close()

    def __del__(self):
        self.cleanup()
