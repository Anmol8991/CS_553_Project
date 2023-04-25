import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('128.6.4.102', 8057))
# sock.setblocking(0)

data = 'curl http://128.6.4.102:8057' 
for i in range(10):
    len_sent = sock.send(data)
print(len_sent)
print(len_sent == len(data))
