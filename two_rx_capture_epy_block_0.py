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

    def __init__(self, period=120):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Add Timestamp Tag',   # will show up in GRC
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.period=period
        self.last_time=None

    def write_rxtime_tag(self, tv):
        sec = int(tv)
        frac = tv % 1
        key = pmt.intern('rx_time')
        value = pmt.make_tuple(pmt.from_uint64(sec), pmt.from_double(frac))
        self.add_item_tag(0, self.nitems_written(0), key, value) 

    def work(self, input_items, output_items):
        now = time.time()
        if self.last_time and (now // self.period != self.last_time // self.period):
            self.write_rxtime_tag(now)
        self.last_time = now

        output_items[0][:] = input_items[0][:]
        return len(output_items[0])
