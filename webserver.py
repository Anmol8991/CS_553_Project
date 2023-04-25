import socket
import select
import errno
import sys

MAX_EVENTS = 1000
BUFFER = 1024
EXIT = 1
HOST = socket.gethostbyname(socket.gethostname())  # Get the IP address of the current machine
PORT = 8072
RESPONSE = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nHello, world!\r\n"


try: 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
except socket.error as e: 
    print ("Error CREATING socket: {}".format(e)) 
    sys.exit(1)

# Bind the socket to a specific address and port
try: 
    server_socket.bind((HOST, PORT))
except socket.error as e: 
    print ("Error BINDING socket: {}".format(e)) 
    sys.exit(1)


# Listen for incoming connections
try: 
    server_socket.listen(100)
except socket.error as e: 
    print ("Error LISTENING socket: {}".format(e)) 
    sys.exit(1)

print("Backend Server is listening at IP: {} Port: {}....".format(HOST,PORT))
print("\n")



try:
    while True:
        try:
            client_connection, client_address = server_socket.accept()  
        except socket.error as e:
            raise
        client_fd = client_connection.fileno()
        print("New Client connection from {} on socket: {}".format(client_address,client_fd))

        data = b""

        try:
            chunk = client_connection.recv(BUFFER)
            data += chunk
        # exit from loop when all data is received => that is why the error statement
        except socket.error as e:
            raise

        
        # on receive data code = receive data and 
        print("Read Data: {}".format(data)) #Completed the basic step
        print(len(data))
        print("Sending Response....")
        try:  
            client_connection.send(RESPONSE)
            # epoll.modify(fileno, select.EPOLLIN)
        except socket.error as e:
                break
        
        print("Closing Connection with client on socket {}".format(client_fd))
        client_connection.close()
        print("\n")
        

finally:
    server_socket.close()