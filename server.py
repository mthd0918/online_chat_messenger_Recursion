import socket
import time
import threading

SERVER_ADDRESS = '0.0.0.0'
SERVER_PORT = 9001

server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket_udp.bind((SERVER_ADDRESS, SERVER_PORT))

# clients {[client_address: user_name, last_sending]}

print("server is starting...")

clients = {}

def relay_messages(message, sender_address, sender_name):
    if isinstance(message, str):
        message = message.encode('utf-8')

    message_and_sender_name = f"{sender_name}: {message.decode()}".encode('utf-8')

    for addr in clients:
        # print(f"client: {addr}, sender: {sender_address}")
        if addr != sender_address:
            try:
                server_socket_udp.sendto(message_and_sender_name, addr)
            except Exception as e:
                print(f"Error sending message to {addr}: {e}")

def parse_address(address_string):
    ip, port = address_string.split(':')
    return (ip, int(port))

def remove_inactive_clients():
    while True:
        current_time = time.time()
        inactive_clients = []

        for client_addr, clients_info in clients.items():
            if current_time - clients_info['last_sending'] > 5:
                inactive_clients.append(client_addr)
        
        for client_addr in inactive_clients:
            del clients[client_addr]
            print(f"removed: {client_addr}")
        
        time.sleep(10)

remove_thread = threading.Thread(target=remove_inactive_clients)
remove_thread.daemon = True
remove_thread.start()

while True:
    data, client_address = server_socket_udp.recvfrom(4096)
    print(client_address)
    receive_time = time.time()

    try:
        data_count = data[0]
        # 各データサイズを取得
        sizes = [data[i] for i in range(1, data_count + 1)]
        header_length = 1 + data_count

        # 各データをデコード
        curr_position = header_length
        extracted_data = []
        for size in sizes:
            extracted_data.append(data[curr_position:curr_position+size].decode())
            curr_position += size

        if len(extracted_data) != 3:
            raise ValueError(f"Expected 3 data items, but got {len(extracted_data)}")
        
        client_address_str, user_name_str, message_str = extracted_data
        parsed_client_address = parse_address(client_address_str)

        # print("**********")
        # print(f"Client Address: {client_address_str}")
        # print(f"User Name: {user_name_str}")
        # print(f"Message: {message_str}")
        # print(f'Recieved: {time.strftime("%Y/%m/%d %H:%M", time.localtime(receive_time))}')
        # print("**********")

        # クライアント情報を更新
        clients[parsed_client_address] = {
            'user_name': user_name_str,
            'last_sending': receive_time
        }

        # print('~~~~All~~~~')
        # for client_addr, client_info in clients.items():
        #     print(f"Client Address: {client_addr}")
        #     print(f"user name: {client_info['user_name']}")
        #     print(f"recieved: {client_info['last_sending']}")
        # print('~~~~~~~~~~~')

        relay_messages(message_str, parsed_client_address, user_name_str)

    except ValueError as ve:
        print(f"Error processing data: {ve}")
    except Exception as e:
        print(f"Unexpected error: {e}")