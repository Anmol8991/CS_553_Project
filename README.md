# CS_553_Project
Epoll Based Reverse Proxy with load balancing

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

The total time of running these experiments is less than 10 minutes, but unfortunaltely we were not able to find scripts for it to automate the process as we are running multiple tests that requires more than one terminal.
