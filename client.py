import socket
BUFFER = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('128.6.4.101', 8091))
# sock.setblocking(0)

data = b'Hi from client' 

for i in range(1000):
    len_sent = sock.send(data)
    len_read = sock.recv(BUFFER)

print(len_read)
print(len_sent == len(data))
