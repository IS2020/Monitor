import serial
import time
import threading
import csv
import json
from datetime import datetime
class SerialMonitor(object):
    def __init__(self, port, threshold, path):
        self._port = port
        self._baudrate=9600
        self._conn = None
        self.path =path
        self.queue={'values':[],
                    'timestamp':[]}
        self.threshold=threshold
        self.buf = bytearray()

    def iniciaConexion(self):
        try:
            self._conn = serial.Serial(self._port, self._baudrate)
            return self._conn
        except:
            print("Fallo al leer el puerto %s " % str(self._port))

    def cerrarConexion(self):
        self._conn.close()

    def monitorListen(self):
        while True:
            muestra_to_csv=0
            val =self.readline()
            #print(val.decode())
            val =val.decode()[:-2]
            if int(val) > self.threshold:
                while muestra_to_csv <200:
                    val_to_save =self.readline().decode()[:-2]
                    self.queue['values'].append(val_to_save)
                    self.queue['timestamp'].append(time.time())
                    print(val_to_save)
                    muestra_to_csv+=1
                print(self.queue)
                try:
                    write_csv_thread=threading.Thread(target=self.saveToJson())
                    write_csv_thread.start()
                    write_csv_thread.join()
                except ValueError as error:
                    print(error)

    def saveToCsv(self):
        try:
            for element in self.queue:
                with open(self.path+"test_data.csv","a") as f:
                    writer = csv.writer(f,delimiter=",")
                    writer.writerow([element['timestamp'],element['values']])
            self.queue.clear()
        except ValueError as error:
            print(error)

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self._conn.in_waiting))
            data = self._conn.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)

    def saveToJson(self):

        with open(self.path+'medicion_test.json', 'w') as fp:
            json.dump(self.queue,fp)
        self.queue['values'].clear()
        self.queue['timestamp'].clear()


    def send_json_to_server():
        with open('data.json', 'rb') as f: 
         r = requests.post('http://127.0.0.1:8000/uploadData/', files={'file': f},params={"api_key":"$2y$10$rn.GcB6A9RY2ZnCrOVD0UOQAhPs5Ce5pTqR5rwN6SwBOmKzrw9Vg2","ts":timestamp}) 
         print(r)

def main():
    s = SerialMonitor(port='/dev/cu.usbmodem14201', threshold=200, path='/Users/macbook/Documents/data_sismic/')
    s.iniciaConexion()
    s.monitorListen()

if __name__ == '__main__':
    main()
