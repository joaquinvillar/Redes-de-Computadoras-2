import socket
import sys
import cv2
import pickle
import numpy as np
import struct
from threading import Thread 
from SocketServer import ThreadingMixIn 
import copy
import time

#python Server.py localhost 1234 0 

# new thread that accept the connections tcp and saves it in tcoListadd
class TCPAccept(Thread):
	def __init__(self): 
		Thread.__init__(self) 

	def run(self):

		try:
			s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.settimeout(5)
			s.bind((HOST, PORT))

			s.listen(1)
			print "\nEsperando por conexiones entrantes..."

			while run == True:
				try:
					conn, addr = s.accept()
					print 'Mensaje[' + addr[0] + ':' + str(addr[1]) + '] - ' + 'Nuevo Cliente TCP'
					tcpListadd[addr] = conn
				except socket.timeout:
					pass
			s.close()
		except KeyboardInterrupt, SystemExit:
			s.close()


class UDPClients(Thread):
	def __init__(self): 
		Thread.__init__(self) 

	def run(self):

		try:
			while run == True:
				try:
					# receive subsciption msg from client (data, addr)
					d = sUDP.recvfrom(1024)
					dataUDP = d[0]
					addrUDP = d[1]		
					subscriptiontime = time.time()
					UDPListadd[addrUDP] = subscriptiontime
					print 'Mensaje[' + addrUDP[0] + ':' + str(addrUDP[1]) + '] - ' + 'UDP ' + dataUDP.strip()
				except socket.timeout:
					pass
			sUDP.close()
		except KeyboardInterrupt, SystemExit:
			sUDP.close()

#capture the video
if sys.argv[3] == "0":
	cap = cv2.VideoCapture(0)
else:
	cap = cv2.VideoCapture(sys.argv[3])

HOST = sys.argv[1]
PORT = int(sys.argv[2])

run = True

sUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sUDP.settimeout(5)
# Bind socket
sUDP.bind((HOST, PORT))

tcpListadd = {}
tcpList = {}
threads = [] 
deleteList = {}

UDPListadd = {}
UDPList = {}
UDPthreads = [] 
UDPdeleteList = {}

print "\nLevantando Servidor..."

#thread for udp accept
tcoUDPThread = UDPClients()
tcoUDPThread.start() 
UDPthreads.append(tcoUDPThread) 

#thread for tcp accept
tcoThread = TCPAccept()
tcoThread.start() 
threads.append(tcoThread) 

while True:
	try:
		#read the frame
		ret,frame = cap.read()
		#get it in string
		data = pickle.dumps(frame)

		#add the new tcp connections
		for a, c in tcpListadd.iteritems():
			tcpList[a] = c
			deleteList[a] = c

		#delete the connections from the list
		for uno,dos in deleteList.iteritems():
			del tcpListadd[uno]

		deleteList = {}
		copyList = {}

		#add the new udp connections
		for a, c in UDPListadd.iteritems():
			if a in UDPList:
				UDPList[a] = c
			else:
				UDPList[a] = c
			UDPdeleteList[a] = c

		#delete the connections from the list
		for uno,dos in UDPdeleteList.iteritems():
			del UDPListadd[uno]

		UDPdeleteList = {}
		UDPcopyList = {}

		limit = 65500 #65,535 bytes - 20 bytes(Size of IP header) = 65, 515 bytes (including 8 bytes UDP header)
		img = frame
		width, height, cosocolor = img.shape
		ratio = float(width) / float(height)

		while img.size > limit:
			width -= 100
			height = int(width / ratio)
			newimg = cv2.resize(img,(int(width), int(height)))
			img = newimg
		sendUDP = img.tostring ()		

		data = pickle.dumps(img)

		#iterate the tcp connections and sends the frame
		for address, connection in tcpList.iteritems():
			try:
				connection.sendall(struct.pack("L", len(data)) + data)
				copyList[address] = connection
			except Exception as e:
				pass
				
		tcpList = {}

			#iterate the udp connections and sends the frame
		for address, subscriptiontime in UDPList.iteritems():
			try:
				if time.time() < subscriptiontime + 90: 
					sUDP.sendto(sendUDP,(address[0], address[1]))
					UDPcopyList[address] = subscriptiontime
				else:
					print 'Tiempo de subscripcion agotado, cliente: IP ' + address[0] + ' Puerto ' + str(address[1])
			except Exception as e:
				pass
		UDPList = {}
		
		#add the connections that did not send errors
		for aaa,bbb in UDPcopyList.iteritems():
			UDPList[aaa] = bbb

		#add the connections that did not send errors
		for aaa,bbb in copyList.iteritems():
			tcpList[aaa] = bbb

	except KeyboardInterrupt:
		for address, connection in tcpList.iteritems():
			try:
				connection.shutdown(SHUT_RDWR)
				connection.close()
			except Exception as e:
				pass
		run = False
		break
cap.release()
cv2.destroyAllWindows()
run = False
for t in threads: 
	t.join() 
for th in UDPthreads:
	th.join()
