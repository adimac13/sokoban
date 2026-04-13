import socket
import threading
from config import host, port

class Client:
    def __init__(self):
        self.host = host
        self.port = port
        self.nickname = ''
        self.nick_received = threading.Event() # For proper name visualization

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        thread_receive = threading.Thread(target=self.receive)
        thread_receive.start()

        thread_write = threading.Thread(target=self.write)
        thread_write.start()

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('ascii')
                if message == 'NICK':
                    self.nickname = self.client.recv(1024).decode('ascii')
                    print(f"Your name is: {self.nickname}")
                    self.nick_received.set()
                else:
                    return message
            except:
                print("Error!!!")
                self.client.close()
                break

    def write(self, message):
        self.nick_received.wait()
        self.client.send(message.encode('ascii'))


if __name__ == "__main__":
    try:
        client = Client()
    except:
        print("d")