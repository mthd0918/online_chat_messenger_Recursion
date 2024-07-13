import socket
import time
import threading
import secrets

class ChatServer:
    def __init__(self, server_address='0.0.0.0', tcp_port=9001, udp_port=9002):
        self.clients = {}
        self.rooms = {}

        self.server_address = server_address
        self.tcp_port = tcp_port
        self.udp_port = udp_port

        # tcp socket
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((self.server_address, self.tcp_port))
        
        # udp socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.server_address, self.udp_port))

    def start(self):
        print("Server is starting...")
        tcp_thread = threading.Thread(target=self.tcp_handler)
        udp_thread = threading.Thread(target=self.udp_handler)
        remove_thread = threading.Thread(target=self.remove_inactive_clients)

        tcp_thread.start()
        udp_thread.start()
        remove_thread.start()

        tcp_thread.join()
        udp_thread.join()
        remove_thread.join()

    def tcp_handler(self):
        self.tcp_socket.listen(5)
        print(f"TCP Server listening on {self.server_address}:{self.tcp_port}")
        while True:
            client_socket, address = self.tcp_socket.accept()
            threading.Thread(target=self.handle_tcp_client, args=(client_socket, address)).start()

    def handle_tcp_client(self, client_socket, address):
        try:
            data = client_socket.recv(4096)
            header = data[:32]
            room_name_size = int.from_bytes(header[:1], "big")
            operation = int.from_bytes(header[1:2], "big")
            payload_size = int.from_bytes(header[3:32], "big")

            body = data[32:]
            room_name = body[:room_name_size].decode("utf-8")
            username = body[room_name_size:room_name_size + payload_size].decode("utf-8")

            token = secrets.token_bytes(32)

            if operation == 1:
                self.rooms[room_name] = [token]
                print(f"new room created: {room_name}")
            elif operation == 2:
                if room_name in self.rooms:
                    self.rooms[room_name].append(token)
                    print(f"User joined room: {room_name}")
                else:
                    client_socket.send("Room does not exist".encode())
                    return

            self.clients[token] = {
                'address': address,
                'username': username,
                'room': room_name,
                'last_activity': time.time()
            }

            # Send token back to client
            client_socket.send(token)
            print(f"Token sent to client: {token.hex()}")

        except Exception as e:
            print(f"Error handling TCP client: {e}")
            client_socket.send("An error occurred".encode())

        finally:
            client_socket.close()

    def udp_handler(self):
        print(f"UDP Server listening on {self.server_address}:{self.udp_port}")
        while True:
            data, client_address = self.udp_socket.recvfrom(4096)
            threading.Thread(target=self.handle_udp_message, args=(data, client_address)).start()

    def handle_udp_message(self, data, client_address):
        try:
            header = data[:2]
            room_name_size = int.from_bytes(header[:1], "big")
            token_size = int.from_bytes(header[1:2], "big")

            body = data[2:]
            room_name = body[:room_name_size].decode("utf-8")
            token = body[room_name_size:room_name_size + token_size]
            message = body[room_name_size + token_size:].decode("utf-8")

            if token in self.clients:
                self.clients[token]['last_activity'] = time.time()
                self.clients[token]['address'] = client_address  # Update client address
                username = self.clients[token]['username']
                
                print(f"Message from {username} in room {room_name}: {message}")
                
                self.relay_message(room_name, token, message)
            else:
                print(f"Received message from unknown client: {client_address}")

        except Exception as e:
            print(f"Error handling UDP message: {e}")

    def relay_message(self, room_name, sender_token, message):
        if room_name in self.rooms:
            sender_name = self.clients[sender_token]['username']
            formatted_message = f"{sender_name}: {message}"
            for token in self.rooms[room_name]:
                if token != sender_token:
                    try:
                        client_address = self.clients[token]['address']
                        self.udp_socket.sendto(formatted_message.encode(), client_address)
                    except Exception as e:
                        print(f"Error sending message to client: {e}")

    def remove_inactive_clients(self):
        while True:
            time.sleep(60)
            current_time = time.time()
            inactive_tokens = [token for token, client in self.clients.items() 
                               if current_time - client['last_activity'] > 300]
            
            for token in inactive_tokens:
                room_name = self.clients[token]['room']
                username = self.clients[token]['username']
                if room_name in self.rooms:
                    self.rooms[room_name].remove(token)
                    if not self.rooms[room_name]:
                        del self.rooms[room_name]
                del self.clients[token]
                print(f"Removed inactive client: {username} from room {room_name}")

if __name__ == "__main__":
    server = ChatServer()
    server.start()