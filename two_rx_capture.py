#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Two RX Capture Graph
# Author: Ben Gelb
# Description: Capture two streams of samples from sdrDUO
# GNU Radio version: 3.10.7.0

from gnuradio import blocks
import math
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import sdrplay3
import two_rx_capture_epy_block_0 as epy_block_0  # embedded python block
import two_rx_capture_epy_block_1 as epy_block_1  # embedded python block




class two_rx_capture(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Two RX Capture Graph", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2000000
        self.fc = fc = 7038.6e3
        self.f_if = f_if = 10e3
        self.decim = decim = 125
        self.bw = bw = 3e3

        ##################################################
        # Blocks
        ##################################################

        self.sdrplay3_rspduo_0 = sdrplay3.rspduo(
            '',
            rspduo_mode="Dual Tuner (diversity reception)",
            antenna="Both Tuners",
            stream_args=sdrplay3.stream_args(
                output_type='fc32',
                channels_size=2
            ),
        )
        self.sdrplay3_rspduo_0.set_sample_rate(2000e3)
        self.sdrplay3_rspduo_0.set_center_freq((fc-f_if))
        self.sdrplay3_rspduo_0.set_bandwidth(0)
        self.sdrplay3_rspduo_0.set_antenna("Both Tuners")
        self.sdrplay3_rspduo_0.set_gain_modes(False, False)
        self.sdrplay3_rspduo_0.set_gain(-40, -40, 'IF')
        self.sdrplay3_rspduo_0.set_gain(-float('0'), -float('0'), 'RF')
        self.sdrplay3_rspduo_0.set_freq_corr(0)
        self.sdrplay3_rspduo_0.set_dc_offset_mode(False)
        self.sdrplay3_rspduo_0.set_iq_balance_mode(False)
        self.sdrplay3_rspduo_0.set_agc_setpoint((-30))
        self.sdrplay3_rspduo_0.set_rf_notch_filter(False)
        self.sdrplay3_rspduo_0.set_dab_notch_filter(False)
        self.sdrplay3_rspduo_0.set_am_notch_filter(False)
        self.sdrplay3_rspduo_0.set_biasT(False)
        self.sdrplay3_rspduo_0.set_debug_mode(True)
        self.sdrplay3_rspduo_0.set_sample_sequence_gaps_check(True)
        self.sdrplay3_rspduo_0.set_show_gain_changes(False)
        self.freq_xlating_fir_filter_xxx_0_0 = filter.freq_xlating_fir_filter_ccc(decim, firdes.low_pass(1.0,samp_rate,bw/2,100), (f_if+bw/2), samp_rate)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(decim, firdes.low_pass(1.0,samp_rate,bw/2,100), (f_if+bw/2), samp_rate)
        self.epy_block_1 = epy_block_1.blk(period_sec=60)
        self.epy_block_0 = epy_block_0.blk(period=1)
        self.blocks_tag_debug_0 = blocks.tag_debug(gr.sizeof_gr_complex*1, '', "")
        self.blocks_tag_debug_0.set_display(True)
        self.blocks_stream_mux_0 = blocks.stream_mux(gr.sizeof_gr_complex*1, (1, 1))
        self.blocks_freqshift_cc_0_0 = blocks.rotator_cc(2.0*math.pi*(bw/2)/(samp_rate/decim))
        self.blocks_freqshift_cc_0 = blocks.rotator_cc(2.0*math.pi*(bw/2)/(samp_rate/decim))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_freqshift_cc_0, 0), (self.blocks_stream_mux_0, 0))
        self.connect((self.blocks_freqshift_cc_0_0, 0), (self.blocks_stream_mux_0, 1))
        self.connect((self.blocks_stream_mux_0, 0), (self.blocks_tag_debug_0, 0))
        self.connect((self.blocks_stream_mux_0, 0), (self.epy_block_1, 0))
        self.connect((self.epy_block_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.blocks_freqshift_cc_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0_0, 0), (self.blocks_freqshift_cc_0_0, 0))
        self.connect((self.sdrplay3_rspduo_0, 0), (self.epy_block_0, 0))
        self.connect((self.sdrplay3_rspduo_0, 1), (self.freq_xlating_fir_filter_xxx_0_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_freqshift_cc_0.set_phase_inc(2.0*math.pi*(self.bw/2)/(self.samp_rate/self.decim))
        self.blocks_freqshift_cc_0_0.set_phase_inc(2.0*math.pi*(self.bw/2)/(self.samp_rate/self.decim))
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(1.0,self.samp_rate,self.bw/2,100))
        self.freq_xlating_fir_filter_xxx_0_0.set_taps(firdes.low_pass(1.0,self.samp_rate,self.bw/2,100))

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.sdrplay3_rspduo_0.set_center_freq((self.fc-self.f_if))

    def get_f_if(self):
        return self.f_if

    def set_f_if(self, f_if):
        self.f_if = f_if
        self.freq_xlating_fir_filter_xxx_0.set_center_freq((self.f_if+self.bw/2))
        self.freq_xlating_fir_filter_xxx_0_0.set_center_freq((self.f_if+self.bw/2))
        self.sdrplay3_rspduo_0.set_center_freq((self.fc-self.f_if))

    def get_decim(self):
        return self.decim

    def set_decim(self, decim):
        self.decim = decim
        self.blocks_freqshift_cc_0.set_phase_inc(2.0*math.pi*(self.bw/2)/(self.samp_rate/self.decim))
        self.blocks_freqshift_cc_0_0.set_phase_inc(2.0*math.pi*(self.bw/2)/(self.samp_rate/self.decim))

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.blocks_freqshift_cc_0.set_phase_inc(2.0*math.pi*(self.bw/2)/(self.samp_rate/self.decim))
        self.blocks_freqshift_cc_0_0.set_phase_inc(2.0*math.pi*(self.bw/2)/(self.samp_rate/self.decim))
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(1.0,self.samp_rate,self.bw/2,100))
        self.freq_xlating_fir_filter_xxx_0.set_center_freq((self.f_if+self.bw/2))
        self.freq_xlating_fir_filter_xxx_0_0.set_taps(firdes.low_pass(1.0,self.samp_rate,self.bw/2,100))
        self.freq_xlating_fir_filter_xxx_0_0.set_center_freq((self.f_if+self.bw/2))




def main(top_block_cls=two_rx_capture, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
