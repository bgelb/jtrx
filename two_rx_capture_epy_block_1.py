"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
import pmt
import time
from datetime import datetime
from gnuradio import gr

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, period_sec=120, debug=False):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Rotating File Sink',   # will show up in GRC
            in_sig=[np.complex64],
            out_sig=None
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.period_sec = period_sec
        self.outfile = None
        self.debug = debug
        self.last_rx_time = None

    def __exit__(self, *args):
        if self.outfile:
            print('{}: Closing current output file (shutdown).'.format(datetime,now))
            self.outfile.close()

    def is_period_start(self, last_ts, cur_ts):
        if last_ts:
            last_period = last_ts[0] // self.period_sec
            cur_period = cur_ts[0] // self.period_sec
            assert cur_period >= last_period
            if cur_period > last_period:
                return True
        return False

    def update_last_rx_time(self, cur_ts):
        if cur_ts:
            self.last_rx_time = cur_ts

    def work(self, input_items, output_items):

        time_pos_list = [(None, self.last_rx_time)]

        # find all rx_time tags in input
        tags = self.get_tags_in_window(0, 0, len(input_items[0]))
        for tag in tags:
            key = pmt.to_python(tag.key)
            value = pmt.to_python(tag.value)
            offset = tag.offset
            pos = offset - self.nitems_read(0)
            assert pos < (self.nitems_read(0) + len(input_items[0]))
            if key == 'rx_time':
                if self.debug:
                    print ('{} => {}'.format(pos, value))
                time_pos_list.append((pos, value))

        # find all period start boundaries
        start_pos = None
        for i in range(1, len(time_pos_list)):
            if self.is_period_start(time_pos_list[i-1][1], time_pos_list[i][1]):
                # check there aren't multiple starts
                assert start_pos == None
                start_pos = time_pos_list[i]

        self.update_last_rx_time(time_pos_list[-1][1])

        if start_pos:
            period_name = datetime.fromtimestamp(start_pos[1][0]).strftime("%y%m%d_%H%M")
            cur_file_items = input_items[0][:start_pos[0]]
            new_file_items = input_items[0][start_pos[0]:]

            # write out items for current file
            if self.outfile:
                self.outfile.write(cur_file_items.tobytes())
                print('{}: Closing current output file.'.format(datetime.now()))
                self.outfile.close()

            # write out items for new file
            filename = period_name + '.dat'
            print ('{}: New period start at sample {} (ts={:.8f}), opening new output file {}.'.format(datetime.now(), start_pos[0]+self.nitems_read(0), start_pos[1][0]+start_pos[1][1], filename))
            self.outfile = open(filename, 'wb')
            self.outfile.write(new_file_items.tobytes())

        elif self.outfile:
            self.outfile.write(input_items[0].tobytes())

        return len(input_items[0])
