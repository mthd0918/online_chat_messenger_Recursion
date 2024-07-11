import socket
import time
import threading

class UDPChatServer:
    def __init__(self, server_address='0.0.0.0', server_port=9001):
        self.server_address = server_address
        self.server_port = server_port
        self.clients = {}
        self.server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket_udp.bind((self.server_address, self.server_port))

    def start(self):
        print("Server is starting...")
        remove_thread = threading.Thread(target=self.remove_inactive_clients)
        remove_thread.daemon = True
        remove_thread.start()
        self.main_loop()

    def remove_inactive_clients(self):
        while True:
            current_time = time.time()
            inactive_clients = []

            for client_address, clients_last_sending in self.clients.items():
                if current_time - clients_last_sending['last_sending'] > 30:
                    inactive_clients.append(client_address)

            for client_address in inactive_clients:
                del  self.clients[client_address]
                print(f"removed: {client_address}")

            time.sleep(60)
    
    def main_loop(self):
        while True:
            data, client_address = self.server_socket_udp.recvfrom(4096)
            receive_time = time.time()

            try:
                header = data[:2]
                username_size = int.from_bytes(header[:1], "big")
                message_size = int.from_bytes(header[1:2], "big")
                
                body = data[2:]
                username = body[2:username_size].decode()
                message = body[username_size:username_size + message_size].decode()

                print("**********")
                print(f"Client Address: {client_address}")
                print(f"User Name: {username}")
                print(f"Message: {message}")
                print(f'Recieved: {time.strftime("%Y/%m/%d %H:%M", time.localtime(receive_time))}')
                print("**********")

                self.update_client_map(username, client_address, receive_time)
                self.relay_messages(client_address, message)

            except ValueError as ve:
                print(f"Error processing data: {ve}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    def update_client_map(self, username, client_address, receive_time):
        self.clients[client_address] = {
            'username': username,
            'last_sending': receive_time
        }

    def relay_messages(self, sender_address, message):
        sender_name = self.clients[sender_address]['username']
        formatted_message = f"{sender_name}: {message}"
        for client_address, client_info in self.clients.items():
            if client_address != sender_address:
                try:
                    self.server_socket_udp.sendto(formatted_message.encode(), client_address)
                except Exception as e:
                    print(f"Error sending message to {client_info['username']} at {client_address}: {e}")

if __name__ == "__main__":
    server = ChatServer()
    server.start()