import socket
import threading
import sys
import signal
import atexit
import os


class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "localhost"
        self.port = 8000
        self.addr = (self.host, self.port)
        self.sock.bind(self.addr)
        self.sock.listen(10)
        self.client_list = {}

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if data.decode() == "q":
                    del self.client_list[client_socket]
                    client_socket.close()
                    return
                self.broadcast(data, self.client_list[client_socket])

            except Exception as e:
                del self.client_list[client_socket]
                client_socket.close()
                return

    @atexit.register
    def shut_down_server(
        self=None, sig=None, frame=None
    ):  # self is none because I don't know the proper way to handle this with atexit
        for connection in list(self.client_list):
            connection.sendall("Server shutting down!".encode())
            connection.close()

        os._exit(1)

    def broadcast(self, message, client_name):
        for connection, _ in self.client_list.items():
            connection.sendall(f"{client_name}: {message.decode()}".encode())

    def start(self):
        signal.signal(signal.SIGINT, self.shut_down_server)
        while True:
            client_socket, addr = self.sock.accept()
            name = client_socket.recv(128).decode()
            self.client_list[client_socket] = name
            print(f"{name}({addr[0]}) has joined the Server.")
            client = threading.Thread(target=self.handle_client, args=(client_socket,))
            client.start()


if __name__ == "__main__":
    server = Server()
    server.start()
