import socket
import select
import errno
import sys

MAX_EVENTS = 100
BUFFER = 1024
EXIT = 1
HOST = socket.gethostbyname(socket.gethostname())  # Get the IP address of the current machine
PORT = 8057
num_of_reqs = 0
num_of_cons = 0


RESPONSE = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nHello, world!\n"


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

server_socket.setblocking(0)

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
    epoll.register(server_socket.fileno(), select.EPOLLIN | select.EPOLLET)
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
                
                client_connection.setblocking(0)

                client_fd = client_connection.fileno()
                epoll.register(client_fd, select.EPOLLIN | select.EPOLLONESHOT)
                connections[client_fd] = client_connection
                
                num_of_cons = num_of_cons + 1
      
                print("New Client connection from {} on socket: {}".format(client_address,client_fd))

            elif event & select.EPOLLIN:
                # Handle incoming data
                data = b""

                while True:
                    try:
                        chunk = connections[fileno].recv(BUFFER)
                        # The first exit condition is when the recv function returns an empty byte string, 
                        # which indicates that the socket has been closed by the remote peer.(i.e the backend server)
                        #  In this case, the loop breaks and control is returned to the calling function.
                        if not chunk: 
                            # to confirm this case occurs when we receive response from server..check fd if fd in 
                            # in ss_sockets => true assumption otherwise wrong
                            break
                        data += chunk
                    except socket.error as e:
                        if e.errno == errno.EWOULDBLOCK or errno.EAGAIN:
                            break
                        else:
                            raise
                
                
                epoll.modify(connections[fileno], select.EPOLLOUT | select.EPOLLONESHOT)

            elif event & select.EPOLLOUT:

                print("Sending Response....")
                try:  
                    connections[fileno].send(RESPONSE)
                    
                    num_of_reqs = num_of_reqs + 1
                    
                    print("The number of requests served at this server is {}".format(num_of_reqs))
                    print("The number of connections served at this server is {}".format(num_of_cons))
                except socket.error:
                        raise
                
                epoll.modify(connections[fileno], select.EPOLLIN | select.EPOLLONESHOT)
                # print("Closing Connection with client on socket {}".format(fileno))
                # epoll.unregister(fileno)
                # connections[fileno].close()
                # del connections[fileno]
                # print("\n")

            elif event & select.EPOLLHUP:
                epoll.unregister(fileno)
                connections[fileno].close()
                connections[fileno]
                               
except socket.error as e:
    raise
