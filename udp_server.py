import socket
import gossip_const
import threading


class Udp_server(threading.Thread):

    def __init__(self,port = gossip_const.udp_lis_port):
        threading.Thread.__init__(self)
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(('',self._port))

    def run(self):
        while True:
            data, addr = self._sock.recvfrom(1024)
            """
            这里还可以验证收到的udp
            """
            if data == b'0x233':
                self._sock.sendto(b'0x466', addr)
                return addr

    def send_udp_boardcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = b'0x233'
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(data, ('255.255.255.255', gossip_const.udp_lis_port))
        data,addr = sock.recvfrom(1024)
        return data.decode('utf-8'),addr


if  __name__ == '__main__':


    u = Udp_server()
    u.run()