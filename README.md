# CS_553_Project
Epoll Based Reverse Proxy with load balancing

SUMMARY 
Event based used to have fine-grained control over scheduling of tasks.
We monitor sockets for various events.

We achieve our goal of getting control over the scheduling of tasks mainly using HOW events are generated(i.e event triggering type) and WHAT type of events are generated(i.e event state).
We manage the scheduling of multiple connections(i.e execution of multiple threads if we implement it through a multi-threaded program) by deciding which event to handle next (i.e equivalent to scheduling)  and deciding which event to handle next is basically how events are generated since they are added automatically to the total event list(ready list of epoll). Generation of events is basically setting the triggering type(i.e level, edge, oneshot)[note1]. We set the right event triggering type for the sockets we are <b monitoring\b>(i.e edge_oneshot for new connection sockets and level for listening_socket) and then we handle these events by identifying their event state(i.e this basically tells us what type of event we are dealing with....incoming data or outgoing data) and if need be also modify the event state of a monitored file decsiptor[note2] and then take actions accordingly....and thus achieving the goal that Event-based servers enable fine-grained control over the scheduling of tasks.

note: 
1. Be cautious in setting the triggering type of events...if it is set wrong it will lead to wrong event generation which will lead to handling of that event but since that event should NOT be generated in the first place the handling of event will lead to disastorous outputs.
(Ex. Suppose an event of type EPOLLIN is generated => handling this event will lead to reading all the data from the buffer.
Ideally, next event generated should be of EPOLLOUT to send all the response data in the buffer but due to wrong triggering an EPOLLIN event is generated => handling this event will lead to reading an empty buffer)

IDEALLY
Recieved incoming data on socket: 8
Read Data: GET / HTTP/1.1
Host: 128.6.4.101:8085
Forwarding packets to socket: 9
Recieved incoming data on socket: 9
Read Data: HTTP/1.1 200 OK
Content-Type: text/html
Hello, world!
Forwarding packets to socket: 8
Closing Connection with client and backend server on socket 8 and 9

ERROR
Recieved incoming data on socket: 8
Read Data: GET / HTTP/1.1
Host: 128.6.4.101:8085
Forwarding packets to socket: 9
Recieved incoming data on socket: 9
Read Data: HTTP/1.1 200 OK
Content-Type: text/html
Hello, world!
<b Recieved incoming data on socket: 9
Read Data: \b>
Forwarding packets to socket: 8
Closing Connection with client and backend server on socket 8 and 9

2. In level-triggered mode, the EPOLLOUT event will be generated whenever a socket is ready for writing. This means that if you call epoll_wait with EPOLLOUT set, and a socket is available for writing, the event will be returned immediately. If you don't write to the socket, the EPOLLOUT event will continue to be returned by epoll_wait.

In edge-triggered mode, the EPOLLOUT event will only be generated ONCE, when the socket transitions from not-ready-for-writing to ready-for-writing. Even though the socket may already be available for writing, the application may not be aware of it(because we monitor it for only incoming data), so the EPOLLOUT event is necessary to ensure that the application is notified when the socket is ready. You will only receive an EPOLLOUT event when the socket becomes available for writing again after having previously been unavailable.
Ex. if we modify to EPOLLOUT from earlier EPOLLIN => this will lead to an event generation because socket state changes from non-writable(i.e since buffer has data that needs to be read or buffer might be free as we have read all the data but the program is not aware about it since we were only mintoring for incoming data) to writable(i.e buffer is free to send data)


Instructions for running the tests:-

1) Latency Test using wrk2 (Stateless)

Start the first backend server at iLab 1 using python backend_server_stateless.py
Start the second backend server at iLab 2 using python backend_server_stateless.py
Start the load balancer at iLab 1 at a different port using using python load_balancer_stateless.py
Run the wrk2 client at iLab 1 using wrk -t2 -c100 -d30s -R2000 http://128.6.4.101:[PORT]/
Run the wrk2 client at iLab 2 using wrk -t2 -c100 -d30s -R2000 http://128.6.4.101:[PORT]/

NOTE:- Here PORT is the port that the load balancer is running on. 

2) Sending and receiving data using a client application (Stateful)

Start the first backend server at iLab 1 using python backend_server_stateful.py
Start the second backend server at iLab 2 using python backend_server_stateful.py
Start the load balancer at iLab 1 at a different port using using python load_balancer_stateful.py
Run the client program using client.py at iLab 1 
Run the client program using client.py at iLab 2

NOTE:- We need to set the port number in the client.py as the one of the load balancer. The clients must be run simultaneously.

3) File Tests using a client application (Stateful)

Start the first backend server at iLab 1 using python backend_server_stateful.py
Start the second backend server at iLab 2 using python backend_server_stateful.py
Start the load balancer at iLab 1 at a different port using using python load_balancer_stateful.py
Run the client program using file_client.py at iLab 1 
Run the client program using file_client.py at iLab 2

NOTE:- We need to set the port number in the client.py as the one of the load balancer. The clients must be run simultaneously.

4) Changing the policies

To change the policies we need to change the Load Balancer argument in the main function for the load balancer to either ‘round robin’, ‘fewest_connections’ or ‘ip_hashing’. We were planning on using command line arguments for selecting the port number and policy, but we couldn’t complete that due to the lack of time.

5) Additional Metrics

Due to fluctuations we observed in the results each time measured during different time of the day, we implemented another program to capture the CPU usage during the entire duration of the above mentioned tests We used the measure_cpu.py file to measure the cpu load on the machines running backend servers and load balancer (iLab 1 and iLab 2 in our case). This program just measures the CPU usage at a given time interval and reports that to the cpu_usage.txt file.


NOTE:- The port numnbers are set in the load balancer file and the backend server files. We were planning on using command line arguments, but we couldn't implement that as we ran out of time.

In the load balancer file :-
The SERVER_PORT is the port of the backend server
The PORT is the port of the load balancer

In the backend server file :- 
The PORT is the port of the backend server
