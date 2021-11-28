import socket
from workerthread import WorkerThread


class WebServer:

    def serve(self):
        print("starting server...")

        try:
            server_socket = self.create_server_socket()

            while True:

                print("waiting for connection from client")
                (client_socket, address) = server_socket.accept()
                print(
                    f"connection with client ended.. remote_address: {address}")

                thread = WorkerThread(client_socket, address)
                thread.start()

        finally:
            print("Stopping server...")

    def create_server_socket(self) -> socket:
        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_socket.bind(("127.0.0.1", 8080))
        server_socket.listen(10)

        return server_socket


if __name__ == '__main__':
    server = WebServer()
    server.serve()
