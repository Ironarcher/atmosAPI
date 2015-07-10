import socket
import thread
import sys
from urllib2 import urlopen

#Insert secret api key here
apikey = ""
#Time in seconds between record syncs with server (default: 10 minutes)
record_update_timer = 600
#Do not tamper with these:
logrecord = {}
started = False
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def activate():
	started = True
	recordlog()
	ping()
	print("Logging activated")

#Input the name of the table and the text to log
def log(tablename, text):
	if not started:
		activate()
	thread.start_new_thread(sendMessage, (tablename, text))

@setInterval(record_update_timer)
def recordlog():
	typ = "3"
	msg = typ + apikey + "%s"

	for key, value in logrecord.iteritems():
		msg.join(key)
		msg.join("%s")
		msg.join(value)
		msg.join("%s") 
	s.sendto(msg, getHostIP())

def addrecord(tablename):
	if tablename in logrecord:
		logrecord[tablename] = logrecord[tablename] + 1
	else:
		logrecord[tablename] = 1

#Max packet size is 4096 bytes
def sendMessage(tablename, text):
	if apikey != "":
		#Type of message being sent: second kind (1)
		typ = "1"
		#Replace %s with another string to prevent packet problems
		if tablename.contains("%s"):
			tablename.replace("%s", "#><$")
		if text.contains("%s"):
			text.replace("%s", "#><$")
			
		msg = typ + apikey + "%s" + tablename + "%s" + text
		if sys.getsizeof(msg) < 4096:
			sent = s.sendto(message, getHostIP())
		else:
			print("Packet too large")
			#Send packet too large exception instead to the server
		addrecord(tablename)
	else:
		print('Api-key must be inputed by using atmoslog.apikey = "input_key_here" before logging')

def getHostIP():
	server_address = ('localhost', 8191)
	return server_address

def setInterval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop(): # executed in another thread
                while not stopped.wait(interval) and started: # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True # stop if the program exits
            function(*args, **kwargs)
            t.start()
            return stopped
        return wrapper
    return decorator

def ping():
	thread.start_new_thread(ping_child, ())

def ping_child():
	start = time.time()
	msg = "1"
	s.sendto(msg, getHostIP())
	data, server = s.recvfrom(4096)
	end = time.time()
	timed = end - start
	print("Pinged server: %s millisecond response time" % timed)
	print("Logging connection is go")

def deactivate():
	started = False
	recordlog()
	s.close()
	print("Logging deactivated")
