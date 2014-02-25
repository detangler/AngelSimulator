import socket
import struct

class DataStreamer:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dst_host = host
        self.dst_port = port
        self.is_connected = False
        
    def connect(self):
        self.socket.connect((self.dst_host, self.dst_port))
        self.is_connected = True
        
    def disconnect(self):
        self.socket.shutdown(1)
        self.socket.close()
        self.is_connected = False
        
    def stream_text(self, data):
        if self.is_connected:
            self.socket.send(bytearray(data, 'utf-8'))
        
    # num is a 16-bit integer, data is packed
    def stream_int(self, num):
        if self.is_connected:
            self.socket.send(struct.pack("!h", num))
        
    def stream_nums(self, nums):
        to_stream = bytes()
        for num in nums:
            to_stream += struct.pack("!h", num)
        
        if self.is_connected:
            self.socket.send(to_stream)