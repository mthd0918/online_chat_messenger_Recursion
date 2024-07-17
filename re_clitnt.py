import socket
import threading

class ChatClient:
    def __init__(self, server_address="0.0.0.0", tcp_port=9001, udp_port=9002):
        self.server_address = server_address
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.tcp_socket = None
        self.udp_socket = None

    def tcp_main(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((self.server_address, self.tcp_port))
        
        while True:
            message = input("TCPメッセージを入力 (終了するには 'quit' と入力): ")
            if message.lower() == 'quit':
                break
            self.tcp_socket.send(message.encode('utf-8'))
            data = self.tcp_socket.recv(4096).decode('utf-8')
            print(f"TCP -> サーバーからの応答: {data}")
        
        self.tcp_socket.close()

    def udp_main(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        while True:
            message = input("UDPメッセージを入力 (終了するには 'quit' と入力): ")
            if message.lower() == 'quit':
                break
            self.udp_socket.sendto(message.encode('utf-8'), (self.server_address, self.udp_port))
            data, _ = self.udp_socket.recvfrom(4096)
            print(f"UDP -> サーバーからの応答: {data.decode('utf-8')}")
        
        self.udp_socket.close()

    def run(self):
        tcp_thread = threading.Thread(target=self.tcp_main)
        udp_thread = threading.Thread(target=self.udp_main)

        tcp_thread.start()
        udp_thread.start()

        tcp_thread.join()
        udp_thread.join()

if __name__ == "__main__":
    client = ChatClient()
    client.run()