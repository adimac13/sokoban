import socket
import threading
from .config import host, port

class Client:
    def __init__(self):
        self.host = host
        self.port = port
        self.nickname = ''
        self.new_message = False
        self.end_of_client = False
        self.nick_received = threading.Event() # For proper name visualization
        self.message_received = threading.Event() # For proper message receiving
        self.msg = ''

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        thread_receive = threading.Thread(target=self.receive)
        thread_receive.start()

    def receive(self):
        buffer = ''
        while not self.end_of_client:
            try:
                buffer += self.client.recv(1024).decode('ascii')
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message == 'NICK':
                        self.client.send(f'Success'.encode('ascii'))
                        self.nickname = self.client.recv(1024).decode('ascii')
                        # print(f"Your name is: {self.nickname}")
                        self.nick_received.set()
                    else:
                        self.msg = message
                        self.message_received.set()
            except:
                self.client.close()
                break

    def write(self, message):
        self.client.send(message.encode('ascii'))


if __name__ == "__main__":
    pass