import socket

if __name__ == '__main__':
    ip_address = socket.gethostbyname(socket.gethostname())
    print(ip_address)

