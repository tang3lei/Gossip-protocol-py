import socket
import threading
import time

port_num = 31234


class UnitServer(threading.Thread):
    def __init__(self, threadID, name, counter, port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port

    def run(self):
        self._socket.bind(('127.0.0.1',self.port))
        self._socket.listen(5)
        print("Starting " + self.name)
        while True:
            sock, addr = self._socket.accept()
            t = threading.Thread(target=tcplink, args=(sock, addr))
            t.start()


def tcplink(sock, addr):
    print('Accept new connection from %s:%s...' % addr)
    sock.send(b'Welcome!')
    while True:
        data = sock.recv(1024)
        if not data or data.decode('utf-8') == 'exit':
            break
        sock.send(('Hello, %s!' % data.decode('utf-8')).encode('utf-8'))
    #sock.close()
    print('Connection from %s:%s closed.' % addr)



if __name__ == '__main__':

    thread1 = UnitServer(1, "Thread-1", 1,port_num)
    thread2 = UnitServer(2, "Thread-2", 2,port_num+1)

    thread1.start()
    thread2.start()