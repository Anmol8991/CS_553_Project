import sys
import socket
import select
import errno
import random
from itertools import cycle

HOST = socket.gethostbyname(socket.gethostname())  # Get the IP address of the current machine
PORT = 8058
SERVER_PORT = 8057
MAX_EVENTS = 100
BUFFER = 1024
RESPONSE = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nHello, world!\r\n"

SERVER_POOL = set(['128.6.4.101', '128.6.4.102'])
SERVER_LIST = ['128.6.4.101', '128.6.4.102']

# Data structures for our policies
ITER = cycle(SERVER_POOL)
num_of_connections = {}

# Adding the server pool to the dictionary of connections mapping
for server in SERVER_LIST:
    num_of_connections[server] = 0

def round_robin(iter):
    # round_robin([A, B, C, D]) --> A B C D A B C D A B C D ...
    return next(iter)
    
# Definition of our Lowest Connection Policy
def fewest_connection():
    
    minimum = sys.maxsize
    server = ''
    
    # Iterating the connections dictionary to find the min
    for key, value in num_of_connections.items():
        
        # Selecting the server with the lowest number of connections
        if value < minimum:
            minimum = value
            server = key      
        
    # Incrementing the number of connections in the dictionary
    num_of_connections[server] = num_of_connections[server] + 1
    
    print(num_of_connections)
    
    return server 
    
# Definition of our IP Hashing Policy
def ip_hashing(client_address):
    
    length = len(SERVER_LIST)
    
    client_ip, client_port = client_address
    
    ip_parts = client_ip.split(".")
    ip_to_hash = int(ip_parts[3])
        
    server = SERVER_LIST[ip_to_hash % length] 
    
    return server


class LoadBalancer(object):
    """ Load balancer.
    
    Flow Diagram:-
    Client Socket <-> map(Client Socket, Server Socket) <-> Server Socket
    
    Notes:-
    flow_table is a dictionary that stores the mapping from the client socket to the server side socket
    sockets is a list that stores the currently connected and open server side sockets
    """

    flow_table = dict()
    ss_sockets = list()
    map_fd = {}
    resonse_to_a_fd = {}

    def __init__(self, algorithm='random'):
        self.algorithm = algorithm

        try: 
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        except socket.error as e: 
            print ("Error CREATING socket: {}".format(e)) 
            sys.exit(1)

        # Bind the socket to a specific address and port
        try: 
            self.server_socket.bind((HOST, PORT))
        except socket.error as e: 
            print ("Error BINDING socket: {}".format(e)) 
            sys.exit(1)

        self.server_socket.setblocking(0)
        # Listen for incoming connections
        try: 
            self.server_socket.listen(100)
        except socket.error as e: 
            print ("Error LISTENING socket: {}".format(e)) 
            sys.exit(1)

        print("Server is listening at IP: {} Port: {}....".format(HOST,PORT))
        print("\n")
        try:
            # Create an epoll instance
            self.epoll = select.epoll()
            self.epoll.register(self.server_socket.fileno(), select.EPOLLIN)
        except OSError as e:
            print("Error in epoll instance: {}".format(e))
            sys.exit(1)

    def new_connection(self):
        try:
            # new conncention can be from any side = client or backened server
            client_socket, client_address = self.server_socket.accept()  
        except socket.error as e:
            print("Can't establish connection with client: {}".format(e))

        # select a backend server => ip of backend server
        server_ip = self.select_server(SERVER_POOL, client_address, self.algorithm)
        
        # init a server-side socket
        ss_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #instantiate socket on load balancer in order to connect to the backend server

        try:
            ss_socket.connect((server_ip, SERVER_PORT)) # connect to the backend server
            print("Load balancer: {} <=> Server connected: {}".format(ss_socket.getsockname(),(socket.gethostbyname(server_ip), SERVER_PORT)))
        except:
            print("Can't establish connection with the Backend Server {} ".format(server_ip))
            print("Closing Connection with client {} on socket {}".format(client_address,client_socket.fileno()))
            client_socket.close()
            return
        
        client_socket.setblocking(0)
        ss_socket.setblocking(0)

        self.ss_sockets.append(ss_socket.fileno())

        self.map_fd[client_socket.fileno()] = client_socket
        self.map_fd[ss_socket.fileno()] = ss_socket
        self.flow_table[client_socket.fileno()] = ss_socket.fileno()
        self.flow_table[ss_socket.fileno()] = client_socket.fileno()

        # Monitor Server-side socket to RECEIVE data
        self.epoll.register(ss_socket.fileno(), select.EPOLLIN | select.EPOLLONESHOT)
        # Monitor Client-side socket to RECEIVE data
        self.epoll.register(client_socket.fileno(), select.EPOLLIN | select.EPOLLONESHOT)

        
        print("New CLIENT connection from {} on socket: {}".format(client_address,client_socket.fileno()))
        print("New connection with BACKEND SERVER {} on socket: {}".format((server_ip,SERVER_PORT),ss_socket.fileno()))


    def select_server(self, server_list, client_address, algorithm):
            if algorithm == 'random':
                return random.choice(server_list)
            elif algorithm == 'round robin':
                return round_robin(ITER)
            elif algorithm == 'fewest_connections':
                return fewest_connection()
            elif algorithm == 'ip_hashing':
                return ip_hashing(client_address)
            else:
                raise Exception('unknown algorithm: {}'.format(algorithm) )
        
    def on_recv(self,fd):
        print("Recieved incoming data on socket: {}".format(fd))
        # Handle incoming data
        data = b""

        while True:
            try:
                chunk = self.map_fd[fd].recv(BUFFER)
                # The first exit condition is when the recv function returns an empty byte string, 
                # which indicates that the socket has been closed by the remote peer.(i.e the backend server)
                #  In this case, the loop breaks and control is returned to the calling function.
                if not chunk: 
                    # to confirm this case occurs when we receive response from server..check fd if fd in 
                    # in ss_sockets => true assumption otherwise wrong
                    print(True if fd in self.ss_sockets else False)
                    break

                data += chunk
                
            except socket.error as e:
                if e.errno == errno.EWOULDBLOCK or errno.EAGAIN:
                    break
                else:
                    raise
        
        # on receive data code 
        print("Read Data: {}".format(data))
        self.resonse_to_a_fd[self.flow_table[fd]] = data
        res_socket = self.map_fd[self.flow_table[fd]]
        self.epoll.modify(res_socket, select.EPOLLOUT| select.EPOLLONESHOT)
        


        

    def on_send(self,fd):
        
        # => incoming message = REQUEST from CLIENT => Action: forward it to the selected server 
        #  => incoming message = RESPONSE from BACKEND SERVER => Action: forward it to the CLIENT
        response = self.resonse_to_a_fd[fd] 
        
        try:
            print("Forwarding packets to socket: {}".format(fd))
            self.map_fd[fd].send(response)
        except socket.error:
                raise
                
        self.epoll.modify(self.map_fd[fd], select.EPOLLIN| select.EPOLLONESHOT)
        
        """        
        
        if fd in self.ss_sockets:
            
        else:
            print("Closing Connection with client and backend server on socket {} and {}".format(fd,self.flow_table[fd]))
            print("\n")
            self.epoll.unregister(fd)
            self.epoll.unregister(self.flow_table[fd])

            self.map_fd[fd].close()
            self.map_fd[self.flow_table[fd]].close()

            del self.flow_table[self.flow_table[fd]]
            del self.flow_table[fd]
            return
            
		"""
           

    def start(self):
        try:
            while True:
                try:
                    events = self.epoll.poll(MAX_EVENTS) #self.epoll.poll(30,MAX_EVENTS)
                    # print("events fd: {}".format(events))
                    # if len(events)==0:
                    #     print ("Error NO ready events") 
                    #     sys.exit(1)
                except OSError as e:
                    print ("Error NO ready events: {}".format(e)) 
                    sys.exit(1)

                for fileno, event in events:
                    
                    # Handle new connections
                    if fileno == self.server_socket.fileno():
                        # onaccept(function) and choosing server and create connection to the selected server
                        self.new_connection()
                        
                    elif event & select.EPOLLIN:
                        self.on_recv(fileno)
                        
                    
                    elif event & select.EPOLLOUT:
                        self.on_send(fileno)

                    elif event & select.EPOLLHUP:
                        self.epoll.unregister(fileno)
                        self.map_fd[fileno].close()
                        del self.map_fd[fileno]
        
        finally:
            print("Close ALL")
            self.epoll.unregister(self.server_socket.fileno())
            self.epoll.close()
            self.server_socket.close()

    

if __name__ == '__main__':
    
    try:
        LoadBalancer('round robin').start()
    except KeyboardInterrupt:
        print ("Ctrl C - Stopping load_balancer")
        sys.exit(1)
