import pika


class MSGListener():

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.queue_name = 'chat_events'

        self.channel.queue_declare(queue=self.queue_name)

        self.channel.basic_consume(
            queue=self.queue_name, 
            on_message_callback=self.callback, 
            auto_ack=True)

    def callback(self, ch, method, properties, body):
        print(" [x] Received %r" % body)

    def start(self):
        self.channel.start_consuming()


if __name__ == '__main__':
    MSGListener().start()