import socket
import threading

class ChatClient:
    def __init__(self, server_address="localhost", tcp_port=9001, udp_port=9002):
        self.server_address = server_address
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', 0))
        self.token = None
        self.username = ""
        self.room_name = ""
        self.running = True

    def start(self):
        self.username = input("Enter your name: ")

        while True:
            try:
                operation = int(input("Enter 1 to create a room, 2 to join an existing room: "))
                if operation in [1, 2]:
                    break
                else:
                    print("Invalid operation. Please enter 1 or 2.")
            except ValueError:
                print("Invalid input. Please enter a number (1 or 2).")

        if operation == 1:
            self.room_name = input("Enter name for the new room: ")
        else:
            self.room_name = input("Enter name of the room to join: ")

        if self.tcp_handshake(operation):
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

            self.send_messages()
        else:
            print("Failed to connect to the server or join/create room.")

    def tcp_handshake(self, operation):
        try:
            self.tcp_socket.connect((self.server_address, self.tcp_port))
            
            room_name_size = len(self.room_name).to_bytes(1, "big")
            operation_bytes = operation.to_bytes(1, "big")
            state = (1 if operation == 1 else 0).to_bytes(1, "big") 
            payload_size = len(self.username).to_bytes(29, "big")

            header = room_name_size + operation_bytes + state + payload_size
            body = self.room_name.encode() + self.username.encode()

            print(f"{room_name_size}, body: {body.decode()}")

            self.tcp_socket.send(header + body)

            response = self.tcp_socket.recv(1024)
            if len(response) == 32:
                self.token = response
                print("Successfully connected to the server and joined/created room.")
                return True
            else:
                print(f"Server response: {response.decode()}")
                return False

        except Exception as e:
            print(f"Error during TCP handshake: {e}")
            return False
        finally:
            self.tcp_socket.close()

    def send_messages(self):
        try:
            while self.running:
                message = input()
                if message.lower() == 'quit':
                    self.running = False
                    break
                
                room_name_size = len(self.room_name).to_bytes(1, "big")
                token_size = len(self.token).to_bytes(1, "big")

                header = room_name_size + token_size
                body = self.room_name.encode() + self.token + message.encode()

                data = header + body

                self.udp_socket.sendto(data, (self.server_address, self.udp_port))

        except Exception as e:
            print(f"Error sending message: {e}")
        finally:
            self.udp_socket.close()

    def receive_messages(self):
        while self.running:
            try:
                data, _ = self.udp_socket.recvfrom(4096)
                message = data.decode()
                print(f"\r{message}")
            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}")


if __name__ == "__main__":
    client = ChatClient()
    client.start()