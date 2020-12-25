from concurrent import futures
import uuid

import grpc

import chat_pb2
import chat_pb2_grpc

tokens = dict()

class ChatServicer(chat_pb2_grpc.ChatServicer):

    def connect(self, request, context):
        global tokens
        if request.username not in tokens.values():
            token = uuid.uuid4().hex
            tokens[token] = request.username
            user_token = token
            is_ok = True
            error_message = ''
        else:
            user_token = ''
            is_ok = False
            error_message = 'User with such name already exists.'
        
        return chat_pb2.ConnectionResponse(
            user_token=user_token,
            status=chat_pb2.Status(
                is_ok=is_ok,
                error_message=error_message))
         
    def disconnect(self, request, context):
        global tokens
        if request.user_token in tokens:
            del tokens[request.user_token]

            is_ok, error_message = True, ''
        else:
            is_ok, error_message = False, 'There aren\'t such user.'

        return chat_pb2.Status(
            is_ok=is_ok,
            error_message=error_message)

    def send_message(self, request, context):
        global tokens
        username = tokens.get(request.user_token, None)
        
        if username is not None:
            print('{}> {}'.format(username, request.text))
            is_ok, error_message = True, ''
        else:
            is_ok, error_message = False, 'Token is not valid.'

        return chat_pb2.Status(
            is_ok=is_ok,
            error_message=error_message)
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(
        ChatServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    print('Chat gRPC server started.')
    serve()
    # rpc connect(ConnectionRequest) returns (ConnectionResponse) {}
    # rpc disconnect(DisconnectionRequest) returns (Status) {}
    # rpc send_message(Message) returns (Status) {}