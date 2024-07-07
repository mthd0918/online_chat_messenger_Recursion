import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 9001

address = '127.0.0.2'
port = 9050
sock.bind((address,port))

user_name = input("Enter your name: ")
byte_user_name = user_name.encode('utf-8')

try:
    print('-----starting socket-----')
    # サーバへのデータ送信
    sent = sock.sendto(byte_user_name, (server_address, server_port))
    print('Send {} bytes'.format(sent))

    # 応答を受信
    data, server = sock.recvfrom(4096)
    decoded_data = data.decode('utf-8')
    print('Recieved: {}'.format(decoded_data))

finally:
    print('-----closing socket------')
    sock.close()