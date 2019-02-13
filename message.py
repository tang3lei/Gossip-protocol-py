
class Message:

    _str_delimiter = '&'

    def __init__(self, version):
        self.ver = version

    #消息间分隔符
    @staticmethod
    def end_delimiter():
        return b'|'

    #消息内分隔符
    @staticmethod
    def str_delimiter():
        return Message._str_delimiter

    #消息头 例0x22心跳包 0x17区块包 0x18数据包

    #

