import socket
BUFFER = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('128.6.4.101', 8058))
# sock.setblocking(0)

file_contents = ""

with open('file_to_send.txt', 'r') as file:
    file_contents = bytes(file.read().rstrip(), 'utf-8')

data = b'file_to_send.txt' 

num_of_correct_trans = 0

for i in range(1000):

    len_sent = sock.send(data)
    recieved_mes = sock.recv(BUFFER)
    
    if recieved_mes == file_contents:
        num_of_correct_trans = num_of_correct_trans + 1
    
    print("The data recieved for request {} is {}".format(i, recieved_mes))

print("The number of correct transmissions are {}".format(num_of_correct_trans))
