import cv2
from ultralytics import YOLO
import socketserver
import threading

model = YOLO("yolov8n-seg.pt")

import threading
mutex = threading.Lock()

def recognizeThread():
    while True:
        mutex.acquire()
        frame = cv2.imread("tmpfs/input.jpg")
        mutex.release()
        result = model(frame,classes=[0],imgsz=320)[0]
        result.save(filename="tmpfs/result.jpg")
        print("proccessed frame")
        cv2.imshow("image",cv2.imread('tmpfs/result.jpg'))
        cv2.waitKey(1)

threading.Thread(target=recognizeThread).start()

class MyTCPHandler(socketserver.BaseRequestHandler):
    def myreceive(self, msglen):
        chunks = []
        bytes_recd = 0
        while bytes_recd < msglen:
            chunk = self.request.recv(min(msglen - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)
    
    def handle(self):
        while True:
            length_bytes = self.myreceive(4)
            length = int.from_bytes(length_bytes, byteorder='little')
            frame = self.myreceive(length)
            mutex.acquire()
            file = open("tmpfs/input.jpg", "wb")
            file.write(frame)
            file.close()
            print("received frame. frame length =",length)
            mutex.release()


server = socketserver.TCPServer(("0.0.0.0", 4321), MyTCPHandler)
server.serve_forever()