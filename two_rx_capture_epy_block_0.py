"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
import time
import pmt
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, period=120, duration=118):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Periodic Burst Tagger',   # will show up in GRC
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.period=period
        self.duration=duration
        self.in_burst=False

    def write_burst_tag(self, state):
        key = pmt.intern('burst')
        value = pmt.from_bool(state)
        self.add_item_tag(0, self.nitems_written(0), key, value)

    def write_rxtime_tag(self, tv):
        sec = int(tv)
        frac = tv % 1
        key = pmt.intern('rx_time')
        value = pmt.make_tuple(pmt.from_uint64(sec), pmt.from_double(frac))
        self.add_item_tag(0, self.nitems_written(0), key, value) 

    def work(self, input_items, output_items):
        now = time.time()
        if (now % self.period < self.duration) and not self.in_burst:
            self.in_burst = True
            self.write_burst_tag(True)
            self.write_rxtime_tag(now)
        elif (now % self.period >= self.duration) and self.in_burst:
            self.in_burst = False
            self.write_burst_tag(False)
            self.write_rxtime_tag(now)

        output_items[0][:] = input_items[0][:]
        return len(output_items[0])
