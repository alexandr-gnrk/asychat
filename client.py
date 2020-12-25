import grpc

import chat_pb2
import chat_pb2_grpc


# channel = grpc.insecure_channel()
with grpc.insecure_channel('localhost:50051') as channel:
    stub = chat_pb2_grpc.ChatStub(channel)            
    conn_resp = stub.connect(
        chat_pb2.ConnectionRequest(
            username='Alex'))
    token = conn_resp.user_token
    status = stub.send_message(
        chat_pb2.Message(
            user_token=token,
            text='Hello world'))
    print('Message status', status.is_ok)
    status = stub.disconnect(
        chat_pb2.DisconnectionRequest(
            user_token=token))
    print('Disconnect status', status.is_ok)