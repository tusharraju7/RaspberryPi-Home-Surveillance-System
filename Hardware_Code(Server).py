#!/usr/bin/env python
import numpy
import pickle
import os
import time
from mraa import getGpioLookup
from grove.button import Button
from grove.grove_ryb_led_button import GroveLedButton
from seeed_dht import DHT
from grove.display.jhd1802 import JHD1802
from grove.grove_relay import GroveRelay
import io
import picamera
import cv2
import datetime
import socket
import face_recognition

print('Setting up System...')
print("Welcome to Raspberry Pi Home Sureveillance System")


IP = '0.0.0.0'
PORT = 8000
print('[INFO]Server IP : {}'.format(IP))
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

server_socket.bind((IP,PORT))
server_socket.listen(1)


print("Server Activated")

date_string = datetime.datetime.now().strftime("%b %d %Y")

current_dir = '/home/pi/Desktop/Application/DoorDatabase/'
path1 = os.path.join(current_dir,date_string)
stream = io.BytesIO()

if(os.path.isdir(path1)):
    print("[INFO] Accessing Storage Database...")
else:
    print("[INFO] Creating New Storage Database...")
    os.mkdir(path1)
print("[INFO] System is ready...\n")

def main():
    relay = GroveRelay(18)
    button = GroveLedButton(5)
    lcd = JHD1802()
    temp_humd_sensor = DHT('11',16)
    classifier = '/home/pi/Desktop/Application/haarcascade_frontalface_default.xml'
    lcd.setCursor(0,0)
    lcd.write("System Activated")
    def doorbell_ring(index,event,tm):
        if event & Button.EV_SINGLE_CLICK:
            time_string = datetime.datetime.now().strftime("%H:%M:%S")
            lcd.setCursor(0,0)
            lcd.write("Doorbell Pressed")
            print("[INFO]Doorbell Rung...")
            button.led.light(True)
            lcd.setCursor(1,0)
            lcd.write("Look at Camera  ")
            time.sleep(2)
            with picamera.PiCamera() as camera:
                camera.resolution = (320, 240)
                lcd.setCursor(1,0)
                lcd.write("3 2 1...        ")
                time.sleep(3)
                camera.capture(stream,format='jpeg')
                lcd.setCursor(1,0)
                lcd.write("Image Captured ")
                print("[INFO]Image Captured...")
            data = pickle.loads(open('/home/pi/Desktop/Application/encodings.pickle', "rb").read())
            buff = numpy.frombuffer(stream.getvalue(), dtype=numpy.uint8)
            image = cv2.imdecode(buff, 1)
            face_cascade = cv2.CascadeClassifier(classifier)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1,minNeighbors=5, minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in faces]
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []
            face_detected = False
            for encoding in encodings:
                matches = face_recognition.compare_faces(data["encodings"],encoding)
                name = "Unknown"
                if True in matches:
                     matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                     counts = {}
                     for i in matchedIdxs:
                         name = data["names"][i]
                         counts[name] = counts.get(name, 0) + 1
                     name = max(counts, key=counts.get)
                names.append(name)
            for ((top, right, bottom, left), name) in zip(boxes, names):
                cv2.rectangle(image, (left, top), (right, bottom),(0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
                face_detected = True
                if name != 'Unknown':
                     print("[INFO]Face Detected...")
                     print('[INFO] Entry Granted')
                     lcd.setCursor(0,0)
                     lcd.write("Welcome Home    ")
                     lcd.setCursor(1,0)
                     lcd.write("{}!          ".format(name))
                     relay.on()
                     print("[INFO] Door Locked")
                     time.sleep(5)
                     relay.off()
                else:
                     print('[INFO] Entry Denied ')
                     lcd.setCursor(0,0)
                     lcd.write("Face Unknown    ")
                     lcd.setCursor(1,0)
                     lcd.write("Contact Owner   ")
                     print('[INFO] Door Locked')
                     relay.off()
            if not face_detected:
               lcd.setCursor(0,0)
               lcd.write("No Face Detected ")
               lcd.setCursor(1,0)
               lcd.write("Try Again...     ")
            button.led.light(False)
            cv2.imwrite(path1+'/'+time_string+'.jpg',image)
            print("[INFO]Image Stored...\n")
            time.sleep(5)
            humidity,temperature = temp_humd_sensor.read()
            lcd.setCursor(0,0)
            lcd.write("Temperature: {0:2}C".format(temperature))
            lcd.setCursor(1,0)
            lcd.write("Humidity: {0:5}%".format(humidity))
    button.on_event = doorbell_ring
    while True:
            client_socket, address = server_socket.accept()
            print("[INFO] Connection Established")
            full_message = client_socket.recv(8)
            decoded_message = full_message.decode('utf-8')
            print('[INCOMING SIGNAL] {}'.format(decoded_message))
            if(decoded_message == '1'):
               relay.on()
               lcd.setCursor(0,0)
               lcd.write("Welcome Home!   ")
               lcd.setCursor(1,0)
               lcd.write("Door Unlocked...")
               print("[INFO] Door Open")
               time.sleep(3)
            elif (decoded_message == '2'):
               relay.off()
               lcd.setCursor(0,0)
               lcd.write("Entry Denied    ")
               lcd.setCursor(1,0)
               lcd.write("Door Locked...  ")
               print("[INFO] Door Closed")
               time.sleep(3)
            elif(decoded_message == '4'):
               try:
                  with picamera.PiCamera() as camera:
                         print("[INFO] Live Video Stream Started...")
                         while True:
                            client, address = server_socket.accept()
                            message = client.recv(8)
                            try:
                               check = message.decode('utf-8')
                               if(check == '1'):
                                  camera.capture('video.jpg')
                                  photo = 'video.jpg'
                                  file = open(photo,'rb')
                                  byte = file.read(1024)
                                  while(byte):
                                     client.send(byte)
                                     byte = file.read(1024)
                                  file.close()
                                  client.close()
                               elif(check == '0'):
                                  client.close()
                                  break
                            finally:
                               try:
                                  client.close()
                               finally:
                                  pass
               finally:
                   print("[INFO] Live Video Stream Ended...")
            elif(decoded_message == '5'):
                     humidity,temperature = temp_humd_sensor.read()
                     data  = str(humidity) + ' ' +  str(temperature)
                     client,address = server_socket.accept()
                     try:
                        client.send(data.encode('utf-8'))
                        client.close()
                     except:
                        try:
                          client.close()
                        except:
                          pass
            humidity,temperature = temp_humd_sensor.read()
            lcd.setCursor(0,0)
            lcd.write("Temperature: {0:2}C".format(temperature))
            lcd.setCursor(1,0)
            lcd.write("Humidity: {0:5}%".format(humidity))

if __name__ == '__main__':
    main()

