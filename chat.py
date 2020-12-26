import argparse

parser = argparse.ArgumentParser(
    description="Anonymus chat that uses gRPC.")
parser.add_argument(
    '-s', '--server',
    action='store_true',
    dest='server',
    help='start chat server')

args = parser.parse_args()

if args.server:
    import app.server
    app.server.serve()
else:
    from app.client import Client
    target = 'localhost:50051'
    Client(target).start()