#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: bgelb
# GNU Radio version: 3.10.7.0

from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation




class towav(gr.top_block):

    def __init__(self, infile='in.wav', outfile='out.wav'):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.infile = infile
        self.outfile = outfile

        ##################################################
        # Blocks
        ##################################################

        self.blocks_wavfile_sink_0_0 = blocks.wavfile_sink(
            'ch2_'+outfile,
            1,
            12000,
            blocks.FORMAT_WAV,
            blocks.FORMAT_PCM_16,
            False
            )
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink(
            'ch1_'+outfile,
            1,
            12000,
            blocks.FORMAT_WAV,
            blocks.FORMAT_PCM_16,
            False
            )
        self.blocks_stream_demux_0 = blocks.stream_demux(gr.sizeof_gr_complex*1, (1, 1))
        self.blocks_multiply_const_xx_1 = blocks.multiply_const_ff(64, 1)
        self.blocks_multiply_const_xx_0 = blocks.multiply_const_ff(64, 1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, infile, False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_complex_to_real_0_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_real_0, 0), (self.blocks_multiply_const_xx_0, 0))
        self.connect((self.blocks_complex_to_real_0_0, 0), (self.blocks_multiply_const_xx_1, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_stream_demux_0, 0))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.blocks_multiply_const_xx_1, 0), (self.blocks_wavfile_sink_0_0, 0))
        self.connect((self.blocks_stream_demux_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_stream_demux_0, 1), (self.blocks_complex_to_real_0_0, 0))


    def get_infile(self):
        return self.infile

    def set_infile(self, infile):
        self.infile = infile
        self.blocks_file_source_0.open(self.infile, False)

    def get_outfile(self):
        return self.outfile

    def set_outfile(self, outfile):
        self.outfile = outfile
        self.blocks_wavfile_sink_0.open('ch1_'+self.outfile)
        self.blocks_wavfile_sink_0_0.open('ch2_'+self.outfile)



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--infile", dest="infile", type=str, default='in.wav',
        help="Set infile [default=%(default)r]")
    parser.add_argument(
        "--outfile", dest="outfile", type=str, default='out.wav',
        help="Set outfile [default=%(default)r]")
    return parser


def main(top_block_cls=towav, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(infile=options.infile, outfile=options.outfile)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
