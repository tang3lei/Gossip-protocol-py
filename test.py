from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
import socket
import tornado.web
import functools
import errno
from tornado.iostream import IOStream
import time

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


async def f():
    http_client = AsyncHTTPClient()
    try:
        response = await http_client.fetch("http://www.baidu.com")
    except Exception as e:
        print("Error: %s" % e)
    else:
        print(response.body)

async def handle_connection(connection):
    stream = IOStream(connection)
    message = await stream.read_until_close()
    print("message from client:", message.decode().strip())

def my_handler(sock, fd, events):
    try:
        rec = sock.recv(1024)
        print(rec.decode('utf-8'))
        data=b'echo me'
        #tmp1 =  sock.send(data)
        #tmp2 =  sock.send(b'exit')
        #io_loop = tornado.ioloop.IOLoop.current()
        #io_loop.spawn_callback(handle_connection, sock)
    except socket.error as e:
        if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
            raise
        return

def write_handler(sock, fd, events):
    try:
        data=b'echo me'
        sock.send(data)
        sock.send(b'exit')
    except socket.error as e:
        if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
            raise
        return

def prt(str,dt):
    print("1111111",str)


def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        r = '200 OK'

def produce(c):
    c.send(None)
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()



if __name__ == '__main__':
    '''
    IOLoop.current().run_sync(f)

    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    
    

    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.bind(('',56112))
    sock.connect(('127.0.0.1',8899))
    '''
        data = []
    while True:
        b = sock.recv(1024)
        if b:
            data.append(b)
            print(b)
        else:
            sock.close()
            break

    print(data)
    '''
    sock.send(b'0x22&|')
    #time.sleep(5)


