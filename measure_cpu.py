import psutil
import time
import sys
import socket

machine_name = socket.gethostname()

f = open(" ".join(["cpu_usage.txt", machine_name]), "w")

try:
    while True:
        time.sleep(1)
        f.write(str(psutil.cpu_percent()))
        f.write("\n")
        
except KeyboardInterrupt:
    print ("Ctrl C - Closing the measurements")
    f.close()
    sys.exit(1)
