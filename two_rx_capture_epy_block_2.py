"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import socket
import struct

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, sample_rate=12000, stream_name='gnuradio', enabled=True):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='VBAN Audio Sink',   # will show up in GRC
            in_sig=[np.short],
            out_sig=None
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.sample_rate = sample_rate
        self.stream_name = stream_name
        self.framecounter = 0
        self.sr_const = [6000, 12000, 24000, 48000, 96000, 192000, 384000, 8000, 16000, 32000, 64000, 128000, 256000, 512000,11025, 22050, 44100, 88200, 176400, 352800, 705600]
        self.to_ip = '192.168.2.255'
        self.to_port = 6980
        self.enabled = enabled

        # create a socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def make_packet(self, samples, fcount):
        header  = b"VBAN" 
        header += bytes([self.sr_const.index(self.sample_rate)])
        header += bytes([len(samples)-1])
        header += bytes([0]) # mono 1 channel
        header += b'\x01'  #VBAN_CODEC_PCM
        header += bytes(self.stream_name + "\x00" * (16 - len(self.stream_name)), 'utf-8')
        header += struct.pack("<L",fcount)
        return header+samples.tobytes()

    def send_packet(self, packet):
        self.sock.sendto(packet, (self.to_ip, self.to_port))

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        if self.enabled:
          max_samples_per_packet = 255
          frames = [input_items[0][i:i+max_samples_per_packet] for i in range(0, len(input_items[0]), max_samples_per_packet)] 
          for f in frames:
              packet = self.make_packet(f, self.framecounter)
              self.send_packet(packet)
              self.framecounter += 1


        return len(input_items[0])
