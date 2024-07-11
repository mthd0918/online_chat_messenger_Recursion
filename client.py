import socket
import threading

class ChatClient:
    def __init__(self, server_address="0.0.0.0", server_port=9001):
        self.server_address = server_address
        self.server_port = server_port
        self.client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket_udp.bind(('', 0))
        self.actual_address = self.client_socket_udp.getsockname()
        self.username = ""
        self.running = True

    def start(self):
        self.username = input("Enter your name: ")
        
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.daemon = True
        receive_thread.start()

        self.send_data()

    def send_data(self):
        try:
            while self.running:
                message = input("Enter your message (or 'quit' to exit): ")
                if message.lower() == 'quit':
                    self.running = False
                    break
                        
                username_size = len(self.username).to_bytes(1, "big")
                message_size = len(message).to_bytes(1, "big")

                header = username_size + message_size
                body = self.username.encode() + message.encode()

                data = header + body

                self.client_socket_udp.sendto(data, (self.server_address, self.server_port))

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self.client_socket_udp.close()

    def receive_data(self):
        while self.running:
            try:
                data, _ = self.client_socket_udp.recvfrom(4096)
                message = data.decode()
                print(f"{message}")
            except Exception as e:
                print(f"Error receiving message: {e}")


if __name__ == "__main__":
    client = ChatClient()
    client.start()