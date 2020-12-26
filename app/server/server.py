from concurrent import futures
import threading
import uuid

import grpc
from loguru import logger

from ..proto import serverchat_pb2 as schat_pb2
from ..proto import serverchat_pb2_grpc as schat_pb2_grpc


class ChatServicer(schat_pb2_grpc.ServerChatServicer):

    def __init__(self):
        self.tokens = dict()
        self.tokens_lock = threading.Lock()
        self.actions = list()
        self.actions_lock = threading.Lock()

    def add_new_action(self, username, action_type, playload=''):
        with self.actions_lock:
            self.actions.append(
                schat_pb2.Action(
                    username=username,
                    action_type=action_type,
                    playload=playload))

    def connect(self, request, context):
        with self.tokens_lock:
            if request.username not in self.tokens.values():
                # add connect action to list of acctions 
                self.add_new_action(
                    request.username,
                    schat_pb2.Action.ActionType.CONNECT)

                # create and save related token
                token = uuid.uuid4().hex
                self.tokens[token] = request.username

                user_token = token
                is_ok, error_message = True, ''

                logger.debug(f'User <{request.username}> connected')
            else:
                user_token = ''
                is_ok, error_message = False, 'User with such name already exists.'
                logger.debug(f'User <{request.username}> tried unsuccessfully to connect')

        
        return schat_pb2.ConnectionResponse(
            user_token=user_token,
            status=schat_pb2.Status(
                is_ok=is_ok,
                error_message=error_message))
         
    def disconnect(self, request, context):
        with self.tokens_lock:
            if request.user_token in self.tokens:
                username = self.tokens[request.user_token]
                # add disconnect action
                self.add_new_action(
                    username,
                    schat_pb2.Action.ActionType.DISCONNECT)

                del self.tokens[request.user_token]

                is_ok, error_message = True, ''

                logger.debug(f'User <{username}> disconnected')
            else:
                is_ok, error_message = False, 'There aren\'t such user.'
                logger.debug(f'User <{request.username}> tried unsuccessfully to disconnected')


        return schat_pb2.Status(
            is_ok=is_ok,
            error_message=error_message)

    def send_message(self, request, context):
        with self.tokens_lock:
            username = self.tokens.get(request.user_token, None)
            
            if username is not None:
                # add send message action
                self.add_new_action(
                    username,
                    schat_pb2.Action.ActionType.SEND_MESSAGE,
                    request.text)

                print('{}> {}'.format(username, request.text))
                is_ok, error_message = True, ''
                logger.debug(f'User <{username}> sent message "{request.text}"')
            else:
                is_ok, error_message = False, 'Token is not valid.'
                logger.debug(f'User with token <{request.token}> tried unsuccessfully to sent message {request.text}')


        return schat_pb2.Status(
            is_ok=is_ok,
            error_message=error_message)

    def get_chat_stream(self, request, context):
        next_action_ind = 0
        # yield all actions
        while True:
            # get actions to send
            with self.actions_lock:
                actions_to_send = self.actions[next_action_ind:]
                next_action_ind = len(self.actions)
            # send actions
            for action in actions_to_send:
                yield action
    

def serve():
    logger.debug('Chat server started at localhost:50051')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schat_pb2_grpc.add_ServerChatServicer_to_server(
        ChatServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()