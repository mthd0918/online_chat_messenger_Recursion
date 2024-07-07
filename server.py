import socket

# AF_INETを使用し、UDPソケットを作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 9001
print('starting up on port {}'.format(server_port))

# ソケットを特殊なアドレス0.0.0.0とポート9001に紐付け
sock.bind((server_address, server_port))

users = {}

while True:
    print('\n-----waiting to receive message-----')
    try:
        data, address = sock.recvfrom(4096)

        # byte data
        print(f'Recived: {len(data)} byte from {address}')

        # decode
        decoded_data = data.decode('utf-8')
        print(f'decoded data: {decoded_data}')
        
        # ユーザー名を保存
        users[address] = decoded_data
        print(f"Current users: {users}")
        
        print("All users:")
        for address, user_name in users.items():
            print(f"address: {address}, user_name: {user_name}")

        if data:
            response = f'{decoded_data}'.encode('utf-8')
            sent = sock.sendto(response, address)
            print('sent {} bytes back to {}'.format(sent, address))
            print('-----connecting done-----')
    except Exception as e:
        print(f'Error: {e}')
        break