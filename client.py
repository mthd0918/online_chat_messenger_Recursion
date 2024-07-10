import socket
import threading
import time

SERVER_ADDRESS = "0.0.0.0"
SERVER_PORT = 9001

client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket_udp.bind(('', 0))
actual_address = client_socket_udp.getsockname()

def received_messages():
    while True:
        try:
            data, _ = client_socket_udp.recvfrom(4096)
            message = data.decode()
            print(f"{message}")
        except Exception as e:
            print(f"Error receiving message: {e}")

receive_thread = threading.Thread(target=received_messages)
receive_thread.daemon = True
receive_thread.start()

try:
    DATA_COUNT = 3

    user_name = input("Enter your name: ")
    
    while True:
        message = input("Enter your message(or 'quit' to exit): ")
        if message.lower() == 'quit':
            break
        
        address_str = f"{actual_address[0]}:{actual_address[1]}"

        sizes = [len(address_str).to_bytes(1, "big"),
             len(user_name).to_bytes(1, "big"),
             len(message).to_bytes(1, "big")
            ]

        header = DATA_COUNT.to_bytes(1, "big") + b''.join(sizes)
        body = address_str.encode() + user_name.encode() + message.encode()

        data = header + body

        client_socket_udp.sendto(data, (SERVER_ADDRESS, SERVER_PORT))

except Exception as e:
    print(f"Error: {e}")

finally:
    client_socket_udp.close()