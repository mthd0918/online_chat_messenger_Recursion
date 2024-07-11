import socket
import time
import threading

class ChatServer:
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
                if current_time - clients_last_sending['last_sending'] > 5:
                    inactive_clients.append(client_address)

            for client_address in inactive_clients:
                del  self.clients[client_address]
                print(f"removed: {client_address}")

            time.sleep(10)
    
    def main_loop(self):
        while True:
            data, client_address = self.server_socket_udp.recvfrom(4096)
            receive_time = time.time()

            try:
                extracted_data = self.parse_data(data)
                if len(extracted_data) != 3:
                    raise ValueError(f"Expected 3 data items, but got {len(extracted_data)}")

                client_address_str, user_name_str, message_str = extracted_data
                parsed_client_address = self.parse_address(client_address_str)

                print("**********")
                print(f"Client Address: {client_address_str}")
                print(f"User Name: {user_name_str}")
                print(f"Message: {message_str}")
                print(f'Recieved: {time.strftime("%Y/%m/%d %H:%M", time.localtime(receive_time))}')
                print("**********")

                self.update_client_info(parsed_client_address, user_name_str, receive_time)
                self.relay_messages(message_str, parsed_client_address, user_name_str)
            except ValueError as ve:
                print(f"Error processing data: {ve}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    def parse_data(self, data):
        data_count = data[0]
        sizes = [data[i] for i in range(1, data_count + 1)]
        header_length = 1 + data_count

        curr_position = header_length
        extracted_data = []
        for size in sizes:
            extracted_data.append(data[curr_position:curr_position+size].decode())
            curr_position += size

        return extracted_data
    
    def parse_address(self, address_string):
        ip, port = address_string.split(':')
        return (ip, int(port))

    def update_client_info(self, client_address, user_name, receive_time):
        self.clients[client_address] = {
            'user_name': user_name,
            'last_sending': receive_time
        }

    def relay_messages(self, message, sender_address, sender_name):
        if isinstance(message, str):
            message = message.encode('utf-8')

        message_and_sender_name = f"{sender_name}: {message.decode()}".encode('utf-8')

        for addr in self.clients:
            if addr != sender_address:
                try:
                    self.server_socket_udp.sendto(message_and_sender_name, addr)
                except Exception as e:
                    print(f"Error sending message to {addr}: {e}")

if __name__ == "__main__":
    server = ChatServer()
    server.start()