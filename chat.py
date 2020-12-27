import argparse

parser = argparse.ArgumentParser(
    description="Anonymus chat that uses gRPC.")
parser.add_argument(
    '-s', '--server',
    action='store_true',
    dest='server',
    help='start chat server')
parser.add_argument(
    '-l', '--listener',
    action='store_true',
    dest='listener',
    help='start message listener (from RabbitMQ)')

args = parser.parse_args()

if args.server:
    import app.server
    app.server.serve()
elif args.listener:
    from app.msg_listener import MSGListener
    MSGListener().start()
else:
    from app.client import Client
    target = 'localhost:50051'
    Client(target).start()