import socket
import threading

class ChatClient:
    def __init__(self, server_address="0.0.0.0", server_port=9001):
        self.SERVER_ADDRESS = server_address
        self.SERVER_PORT = server_port
        self.client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket_udp.bind(('', 0))
        self.actual_address = self.client_socket_udp.getsockname()
        self.user_name = ""
        self.running = True

    def start(self):
        self.user_name = input("Enter your name: ")
        
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        self.send_messages()

    def receive_messages(self):
        while self.running:
            try:
                data, _ = self.client_socket_udp.recvfrom(4096)
                message = data.decode()
                print(f"\n{message}")
            except Exception as e:
                print(f"Error receiving message: {e}")

    def send_messages(self):
        try:
            while self.running:
                message = input("Enter your message (or 'quit' to exit): ")
                if message.lower() == 'quit':
                    self.running = False
                    break
                
                self.send_data(message)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self.client_socket_udp.close()

    def send_data(self, message):
        DATA_COUNT = 3
        address_str = f"{self.actual_address[0]}:{self.actual_address[1]}"

        sizes = [len(address_str).to_bytes(1, "big"),
                 len(self.user_name).to_bytes(1, "big"),
                 len(message).to_bytes(1, "big")]

        header = DATA_COUNT.to_bytes(1, "big") + b''.join(sizes)
        body = address_str.encode() + self.user_name.encode() + message.encode()

        data = header + body

        self.client_socket_udp.sendto(data, (self.SERVER_ADDRESS, self.SERVER_PORT))

if __name__ == "__main__":
    client = ChatClient()
    client.start()