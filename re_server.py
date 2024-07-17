import socket
import json
import os
import threading
import time
import secrets

class ChatServer:
    def __init__(self, server_address='0.0.0.0', tcp_port=9001, udp_port=9002):
        self.clients = {}
        self.rooms = {}

        self.dpath = 'temp'
        if not os.path.exists(self.dpath):
            os.makedirs(self.dpath)

        self.server_address = server_address

        # tcp_socket
        self.tcp_port = tcp_port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((self.server_address, self.tcp_port))
        self.tcp_socket.listen(3)

        print("***")
        print(f"TCPサーバーが{self.server_address}:{self.tcp_port}で起動しました")
        print("***")

        # udp_socket
        self.udp_port = udp_port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.server_address, self.udp_port))

        print("***")
        print(f"UDPサーバーが{self.server_address}:{self.udp_port}で起動しました")
        print("***")


    """
    todo
    - jsonファイル
    {
        "clients": {
        "clientToken1": {
            "clientAddress": "192.168.1.1",
            "username": "user1",
            "last_response": 2024-7-17-14:37:42,
            "hostTokens": ["token1", "token2"],
            "guestTokens": ["token3", "token4"]
        }
    },
        "rooms": {
            "hostToken1": {
            "hostAddress": "192.168.1.2",
            "roomName": "Room1",
            "guestTokens": ["guestToken1", "guestToken2"]
            }
        }
    }

    - TCP接続
        - chatroomの管理
            - チャットルームの作成、参加
                - 作成: operation == 1
                    - state: host
                        - host用のtokenを作成、送信
                - 参加: operation == 2
                    - state: guest(not host)
                        - not host用のトークンを作成 -> roomsへ参加用のtokenを追加
    - UDP接続
        - メッセージの送信
            - メッセージのリレー
        - メッセージの受信
        - 非アクティブなユーザーの削除
            - state: host
                - ルームの削除
            - state: guest
                - 当該ユーザーの削除
    """

    def tcp_main(self):
        while True:
            try:
                # 接続の待機
                client_socket, address = self.tcp_socket.accept()
                print(f"TCP -> クライアント{address}が接続しました")

                # データの受信
                data = client_socket.recv(4096).decode('utf-8')
                print(f"TCP -> 受信したデータ: {data}")

                # データの送信
                response = "Hello from TCP server"
                client_socket.send(response.encode('utf-8'))
            finally:
                client_socket.close()

    def udp_main(self):
        while True:
            data, address = self.udp_socket.recvfrom(4096)
            print(f"UDP -> クライアント{address}からデータを受信: {data.decode('utf-8')}")

            response = "Hello from UDP server!"
            self.udp_socket.sendto(response.encode('utf-8'), address)

    
    def run(self):
        tcp_thread = threading.Thread(target=self.tcp_main)
        udp_thread = threading.Thread(target=self.udp_main)

        tcp_thread.start()
        udp_thread.start()

        tcp_thread.join()
        udp_thread.join()


if __name__ == "__main__":
    server = ChatServer()
    server.run()
