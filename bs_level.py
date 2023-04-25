import socket
import select
import errno
import sys

MAX_EVENTS = 100
BUFFER = 1024
EXIT = 1
HOST = socket.gethostbyname(socket.gethostname())  # Get the IP address of the current machine
PORT = 9009


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
    # Create an epoll instance
    epoll = select.epoll()
    epoll.register(server_socket.fileno(), select.EPOLLIN)
except OSError as e:
    print("Error in epoll instance: {}".format(e))
    sys.exit(1)

try:
    connections = {}
    while True:

        try:
            events = epoll.poll(MAX_EVENTS)
        except OSError as e:
            print ("Error NO ready events: {}".format(e))
            sys.exit(1)

        for fileno, event in events:
            # Handle new connections
            if fileno == server_socket.fileno():
                #   onaccept(function) and choosing server and create connection to the selected server

                #   If no pending connections are present on the queue, and the
                #   socket is not marked as nonblocking, accept() blocks the caller
                #   until a connection is present.  If the socket is marked
                #   nonblocking and no pending connections are present on the queue,
                #   accept() fails with the error EAGAIN or EWOULDBLOCK.
                try:
                    client_connection, client_address = server_socket.accept()  
                except socket.error as e:
                        raise

                client_fd = client_connection.fileno()
                epoll.register(client_fd, select.EPOLLIN )
                connections[client_fd] = client_connection
                print("New Client connection from {} on socket: {}".format(client_address,client_fd))

            elif event & select.EPOLLIN:
                # Handle incoming data
                print("inc data from socket; {}".format(fileno))
                data = b""
                try:
                    data += connections[fileno].recv(BUFFER)
                except socket.error as e:
                        raise
                if data:
                    # on receive data code = receive data and 
                    print("Read Data: {}".format(data)) #Completed the basic step
                    print("Sending Response....")
                    try:  
                        connections[fileno].send(RESPONSE)
                    except socket.error:
                            raise
                    print("Closing Connection with client on socket {}".format(fileno))
                    epoll.unregister(fileno)
                    connections[fileno].close()
                    del connections[fileno]
                    # print("\n")
                
                     
                

                    
except socket.error as e:
    raise