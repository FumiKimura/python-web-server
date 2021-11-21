import socket


class TCPClient:

    def request(self):

        print("starting client")

        try:
            client_socket = socket.socket()
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            print("connecting to server")
            client_socket.connect(("localhost", 80))
            print("connection established")

            with open("client_send.txt", "rb") as f:
                request = f.read()

            client_socket.send(request)

            response = client_socket.recv(4096)

            with open("client_recv.txt", "wb") as f:
                f.write(response)

            client_socket.close()

        finally:
            print("Stopping the client")


if __name__ == "__main__":
    client = TCPClient()
    client.request()
