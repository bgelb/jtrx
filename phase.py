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




class phase(gr.top_block):

    def __init__(self, gain=0, infile='in.wav', outfile='out.wav', phi=0):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.gain = gain
        self.infile = infile
        self.outfile = outfile
        self.phi = phi

        ##################################################
        # Blocks
        ##################################################

        self.blocks_wavfile_sink_0 = blocks.wavfile_sink(
            'combined_'+outfile,
            1,
            12000,
            blocks.FORMAT_WAV,
            blocks.FORMAT_PCM_16,
            False
            )
        self.blocks_stream_demux_0 = blocks.stream_demux(gr.sizeof_gr_complex*1, (1, 1))
        self.blocks_phase_shift_0 = blocks.phase_shift(phi, False)
        self.blocks_multiply_const_xx_2 = blocks.multiply_const_cc(10**(-gain/10), 1)
        self.blocks_multiply_const_xx_1 = blocks.multiply_const_cc(10**(gain/10), 1)
        self.blocks_multiply_const_xx_0 = blocks.multiply_const_ff(64, 1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, infile, False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.blocks_multiply_const_xx_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_stream_demux_0, 0))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.blocks_multiply_const_xx_1, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_const_xx_2, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_phase_shift_0, 0), (self.blocks_multiply_const_xx_2, 0))
        self.connect((self.blocks_stream_demux_0, 0), (self.blocks_multiply_const_xx_1, 0))
        self.connect((self.blocks_stream_demux_0, 1), (self.blocks_phase_shift_0, 0))


    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.blocks_multiply_const_xx_1.set_k(10**(self.gain/10))
        self.blocks_multiply_const_xx_2.set_k(10**(-self.gain/10))

    def get_infile(self):
        return self.infile

    def set_infile(self, infile):
        self.infile = infile
        self.blocks_file_source_0.open(self.infile, False)

    def get_outfile(self):
        return self.outfile

    def set_outfile(self, outfile):
        self.outfile = outfile
        self.blocks_wavfile_sink_0.open('combined_'+self.outfile)

    def get_phi(self):
        return self.phi

    def set_phi(self, phi):
        self.phi = phi
        self.blocks_phase_shift_0.set_shift(self.phi)



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--gain", dest="gain", type=eng_float, default=eng_notation.num_to_str(float(0)),
        help="Set gain [default=%(default)r]")
    parser.add_argument(
        "--infile", dest="infile", type=str, default='in.wav',
        help="Set infile [default=%(default)r]")
    parser.add_argument(
        "--outfile", dest="outfile", type=str, default='out.wav',
        help="Set outfile [default=%(default)r]")
    parser.add_argument(
        "--phi", dest="phi", type=eng_float, default=eng_notation.num_to_str(float(0)),
        help="Set phi [default=%(default)r]")
    return parser


def main(top_block_cls=phase, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(gain=options.gain, infile=options.infile, outfile=options.outfile, phi=options.phi)

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
