
class Message:

    end_delimiter = b'|'

    def __init__(self, version):
        self.ver = version
