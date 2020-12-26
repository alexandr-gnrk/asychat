import threading

import grpc

import serverchat_pb2 as schat_pb2
import serverchat_pb2_grpc as schat_pb2_grpc


def message_listener(stub):
    for action in stub.get_chat_stream(schat_pb2.Empty()):
        if action.action_type == schat_pb2.Action.ActionType.CONNECT:
            print('User {} is connected to the server'.format(action.username))
        elif action.action_type == schat_pb2.Action.ActionType.DISCONNECT:
            print('User {} is disconnected from the server'.format(action.username))
        elif action.action_type == schat_pb2.Action.ActionType.SEND_MESSAGE:
            print('{} > {}'.format(action.username, action.playload))


username = input('Enter username:')

# channel = grpc.insecure_channel()
with grpc.insecure_channel('localhost:50051') as channel:
    stub = schat_pb2_grpc.ServerChatStub(channel)            
    
    threading.Thread(target=message_listener, args=(stub,)).start()
    
    conn_resp = stub.connect(
        schat_pb2.ConnectionRequest(
            username=username))
    token = conn_resp.user_token

    try:
        while True:
            text = input('< ')
            status = stub.send_message(
            schat_pb2.Message(
                user_token=token,
                text=text))
            print('Message status', status.is_ok)
    except KeyboardInterrupt:
        status = stub.disconnect(
            schat_pb2.DisconnectionRequest(
                user_token=token))
    # print('Disconnect status', status.is_ok)