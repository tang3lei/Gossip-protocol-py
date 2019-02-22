import socket
import errno
import tornado.ioloop
import tornado.iostream
import periodicCallback
from message import Message
import queue
import signal
import sys,os
import functools
import gossip_const
import udp_server


def deal_sigint(signum, frame):
    print('KeyboardInterrupt', file=sys.stderr)
    for con in g.connection_map.values():
        con.close()
    if g.sock:
        g.sock.close()

    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


class Gossip_Server(object):

    def __init__(self, host, port, heartbeat, id):
        self._host = host
        self._port = port
        self._heartbeat = heartbeat
        self._id = id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_map = {}   # key: addr value: socket
        self.msg_queue = queue.Queue()
        self._time_stamp_map = {}
        self._addr_fd_map = {}

    def __del__(self):
        if self.sock:
            self.sock.close()

    def socket_init(self):
        try:
            self.sock.bind((self._host, self._port))
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.listen(128)
            self.sock.setblocking(False)
        except socket.error as e:
            print('Except', e)

    def _add_read_handle(self, connection, addr, fd, events):

        r_stream = tornado.iostream.IOStream(connection)
        data = r_stream.read_until(Message.end_delimiter(),max_bytes=1024)

        if data.exception() is not None:
            print('close')
            self._del_connection(addr)
            tornado.ioloop.IOLoop.current().remove_handler(fd)
        else:
            print('rec',connection)
            msg = data.result().decode('utf-8')
            str_list = msg.split(Message.str_delimiter())
            if str_list[0] == '0x22':
                print('heartbeat')
                print(msg)
                self._time_stamp_map[addr] = tornado.ioloop.IOLoop.current().time()



    def _add_connection(self, connection, address):
        print('add connection')
        con = self.connection_map.get(address)

        if con is None :
            self._addr_fd_map[address] = connection.fileno()
            self.connection_map[address] = connection
            self._time_stamp_map[address] = tornado.ioloop.IOLoop.current().time()

            read_handle = functools.partial(self._add_read_handle,connection,address)
            tmp_loop = tornado.ioloop.IOLoop.current()
            tmp_loop.add_handler(connection.fileno(),read_handle,tmp_loop.READ)
        else:
            self._addr_fd_map[address] = connection.fileno()
            self.connection_map[address] = connection
            self._time_stamp_map[address] = tornado.ioloop.IOLoop.current().time()

            read_handle = functools.partial(self._add_read_handle,connection,address)
            tmp_loop = tornado.ioloop.IOLoop.current()
            tmp_loop.remove_handler(connection.fileno())
            tmp_loop.add_handler(connection.fileno(),read_handle,tmp_loop.READ)

    def _check_connection(self):
        tmp_time = tornado.ioloop.IOLoop.current().time()
        tmp_list = []

        for addr, t in self._time_stamp_map.items():
            if (tmp_time-t) > gossip_const.heartbeat_secs:
                tmp_list.append(addr)
            elif self.connection_map[addr].fileno() == -1:
                tmp_list.append(addr)

        for addr in tmp_list:
            tornado.ioloop.IOLoop.current().remove_handler(self._addr_fd_map[addr])

            self._time_stamp_map.pop(addr)
            self.connection_map.pop(addr)
            self._addr_fd_map.pop(addr)

    async def handle_connection(self, connection, address):
        print(connection.fileno())

        if connection.fileno() == -1:
            self._del_connection(address)
        else:
            self._add_connection(connection, address)
            self.broadcast_heartbeat()

    def _del_connection(self, address):
        print('del connection')

        self.connection_map.pop(address)
        self._addr_fd_map.pop(address)
        self._time_stamp_map.pop(address)

    def connection_ready(self, fd, events):
        while True:
            try:
                connection, address = self.sock.accept()
            except socket.error as e:
                if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                return
            connection.setblocking(0)

            io_loop = tornado.ioloop.IOLoop.current()
            io_loop.spawn_callback(self.handle_connection, connection, address)

    def add_con(self, address):
        nsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        nsock.connect(address)
        nsock.setblocking(0)
        io_loop = tornado.ioloop.IOLoop.current()
        io_loop.spawn_callback(self.handle_connection, nsock, address)

    def broadcast_heartbeat(self):
        self._check_connection()
        for addr, con in self.connection_map.items():
            #msg = message.Message(1)
            print('heartbeat:',con)

            msg = '0x22&|'

            self.sendMsg(msg, con)

    def sendMsg(self, msg, connection):
        s_stream = tornado.iostream.IOStream(connection)
        s_stream.write(msg.encode('utf-8'))

    def join(self, network):
        pass

def fun(str):
    print('1234',str)


if __name__ == '__main__':

    signal.signal(signal.SIGINT, deal_sigint)

    u = udp_server.Udp_server(63112)
    s, addr = u.send_udp_boardcast()
    print(s, addr)

    #t = udp_server.Udp_server()
    #t.start()

    g = Gossip_Server('', gossip_const.server_port, 123, 'server 1')
    #host port beat str_id
    g.socket_init()
    g.add_con(addr)


    io_loop1 = tornado.ioloop.IOLoop.current()
    io_loop1.add_handler(g.sock,g.connection_ready,io_loop1.READ)

    p = periodicCallback.PeriodicCallback(g.broadcast_heartbeat,30).start()      #每三十秒心跳一次

    io_loop1.start()
