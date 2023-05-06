import socket
BUFFER = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('128.6.4.101', 8058))
# sock.setblocking(0)

data = b'Hi from client'
RESPONSE = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nHello, world!\n"
accurate_count = 0

for i in range(1000):
    len_sent = sock.send(data)
    received_mes = sock.recv(BUFFER)
    print(received_mes)
    
    if RESPONSE == received_mes:
        accurate_count = accurate_count + 1
        
    print("The number of accurate transmissions are: {}".format(accurate_count))
