import socket
import threading
import time

class ChatClient:
    def __init__(self, server_address="0.0.0.0", tcp_port=9001, udp_port=9002):
        self.server_address = server_address
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', 0))

    """
    todo
    - main()
        - input_username
        - operation(host or not)
        - roomname
    - send_info()
        - send_header & body & message
            - roomname, operation, state, token, payload(username), message
    - recieve_message()
        - print username: message
    """

    def main(self):
        print("hello")

if __name__ == "__main__":
    client = ChatClient()
    client.main()