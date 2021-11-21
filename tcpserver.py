import socket


class TCPServer:

    def serve(self):
        print("starting server...")

        try:
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            server_socket.bind(("127.0.0.1", 8080))
            server_socket.listen(10)

            print("waiting for connection from client")
            (client_socket, address) = server_socket.accept()
            print(f"connection with client ended.. remote_address: {address}")

            request = client_socket.recv(4096)

            with open("server_recv.txt", "wb") as f:
                f.write(request)

            with open("server_send.txt", "rb") as f:
                response = f.read()

            client_socket.send(response)

            client_socket.close()

        finally:
            print("stopping server...")


if __name__ == '__main__':
    server = TCPServer()
    server.serve()
