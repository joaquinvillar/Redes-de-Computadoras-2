import cv2
import numpy as np
import socket
import sys
import pickle
import struct
import time
from threading import Thread 
from SocketServer import ThreadingMixIn 

#python Client.py localhost 1234 UDP
#python Client.py localhost 1234 TCP

# 1 HOST SERVIDOR
# 2 PUERTO SERVIDOR
# UDP o TCP

class Subs(Thread):
    def __init__(self): 
        Thread.__init__(self) 

    def run(self):
        try:
            sock.sendto('Mensaje de subscripcion inicial', (HOST, PORT))
            timeout = 30
            timeout_start = time.time()
            while(run == True) :
                if time.time() == timeout + timeout_start:  
                    sock.sendto('Mensaje de subscripcion', (HOST, PORT))
                    timeout_start = time.time()
        except KeyboardInterrupt, SystemExit:
            pass

HOST = sys.argv[1]
PORT = int(sys.argv[2])

run = True
ejecutar = True

if sys.argv[3] == "TCP":

    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((HOST, PORT))
    clientsocket.settimeout(5)
    data = ""
    payload_size = struct.calcsize("L") #unsigned long  integer     4 bytes

    while (ejecutar == True):
        try:        
			#receive the size of the frame
			try:
				while len(data) < payload_size:
					data += clientsocket.recv(4096)
					if not data:
						ejecutar = False
						break
			except socket.error:
				ejecutar = False
				break

			if ejecutar == True:
				packed_msg_size = data[:payload_size]

				#unpack the size of the frame
				data = data[payload_size:]
				msg_size = struct.unpack("L", packed_msg_size)[0]
				# receive the frame
				while len(data) < msg_size:
					try:
						data += clientsocket.recv(4096)
					except socket.timeout:
						ejecutar = False
						break
				if ejecutar == True:
					frame_data = data[:msg_size]
					data = data[msg_size:]

					frame=pickle.loads(frame_data)

					frame = frame.reshape(106,80,3)

					width = 106
					height = 80
					img = frame
					ratio = float(106) / float(80)
					limit = 500000
					while img.size < limit:
					        width += 100
					        height = int(width / ratio)
					        #img.resize((width, height), Image.ANTIALIAS)
					        newimg = cv2.resize(img,(int(width), int(height)))
					        img = newimg
					frame = img

					cv2.imshow('TCPClient',frame)
					if cv2.waitKey(1) & 0xFF == ord('q'):
						ejecutar = False
						break
        except KeyboardInterrupt:
			print 'Conexion finalizada'
			run = False
			break
	if ejecutar == False:
		clientsocket.shutdown(socket.SHUT_RDWR) 
		clientsocket.close()
else:

    UDPthreads = [] 

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    tcoUDPThread = Subs()
    tcoUDPThread.start() 
    UDPthreads.append(tcoUDPThread) 

    while True:
        try:
            data, addr = sock.recvfrom(46080)
            s = str(data)
            frame = np.fromstring(s,dtype=np.uint8)
            frame = frame.reshape(106,80,3)

            width = 106
            height = 80
            img = frame
            ratio = float(106) / float(80)
            limit = 500000
            while img.size < limit:
                    width += 100
                    height = int(width / ratio)
                    #img.resize((width, height), Image.ANTIALIAS)
                    newimg = cv2.resize(img,(int(width), int(height)))
                    img = newimg
            frame = img
            cv2.imshow('UDPClient',frame)

            if cv2.waitKey(1) & 0xFF == ord ('q'):
                break
        except KeyboardInterrupt:
            print 'Conexion finalizada'
            run = False
            break        
    for t in UDPthreads: 
        t.join()