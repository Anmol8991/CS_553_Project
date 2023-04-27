import psutil
import time
import sys

f = open("cpu_usage.txt", "w")

try:
    while True:
        time.sleep(1)
        f.write(str(psutil.cpu_percent()))
        f.write("\n")
        
except KeyboardInterrupt:
    print ("Ctrl C - Closing the measurements")
    f.close()
    sys.exit(1)
