from argparse import ArgumentParser
import numpy as fft_np
#import cupy as np
import numpy as np

sync_vec = [ 1,  1, -1, -1, -1, -1, -1, -1,  1, -1, -1, -1,  1,  1,  1, -1, -1,
       -1,  1, -1, -1,  1, -1,  1,  1,  1,  1, -1, -1, -1, -1, -1, -1, -1,
        1, -1, -1,  1, -1,  1, -1, -1, -1, -1, -1, -1,  1, -1,  1,  1, -1,
       -1,  1,  1, -1,  1, -1, -1, -1,  1,  1, -1,  1, -1, -1, -1, -1,  1,
        1, -1,  1, -1,  1, -1,  1, -1,  1, -1, -1,  1, -1, -1,  1, -1,  1,
        1, -1, -1, -1,  1,  1, -1,  1, -1,  1, -1, -1, -1,  1, -1, -1, -1,
       -1, -1,  1, -1, -1,  1, -1, -1,  1,  1,  1, -1,  1,  1, -1, -1,  1,
        1, -1,  1, -1, -1, -1,  1,  1,  1, -1, -1, -1, -1, -1,  1, -1,  1,
       -1, -1,  1,  1, -1, -1, -1, -1, -1, -1, -1,  1,  1, -1,  1, -1,  1,
        1, -1, -1, -1,  1,  1, -1, -1, -1]

DT=1.0/375.0 # sample period
DF=375.0/256.0 # freq width of 1 bin

def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--infile", dest="infile", type=str, default='in.dat',
        help="Set infile [default=%(default)r]")
    return parser

def osc(f, n):
    dp = -1*2*np.pi*f*DT
    return np.exp(np.array([1j*dp*i for i in range(n)]))

def bin_to_baseband_freq(in_bin):
    assert in_bin >= 0 and in_bin < 128
    return (in_bin - 64) * DF + DF/2

def bin_to_af_freq(in_bin):
    return 1500.0 + bin_to_baseband_freq(in_bin) + 1.5*DF

def bin_to_rf_freq(in_bin):
    return 475700 + bin_to_baseband_freq(in_bin) + 1.5*DF

def make_input_matrix(input_samples, lag=0):
    in_vec = np.array(input_samples[lag:lag+162*256])
    out_mat = np.reshape(in_vec, [162,256])
    return out_mat

def make_osc_matrix(shift=0):
    return np.array([osc(bin_to_baseband_freq(i)+shift, 256) for i in range(128)])

def make_sync_matrix():
    return np.array([np.pad(np.array([-1,1,-1,1]), (i,124-i)) for i in range(125)])

def filter_decimate(input_samples):
    nfft1=1474560
    nfft2=nfft1//32
    df=12000.0/nfft1;
    i0=int(1500.0/df+0.5);


    spectrum = fft_np.fft.fft(input_samples, n=nfft1)
    filt_spectrum1 = spectrum[i0:i0+nfft2//2]
    filt_spectrum2 = spectrum[i0-nfft2//2:i0]
    filt_spectrum = fft_np.concatenate((filt_spectrum1, filt_spectrum2))

    assert len(filt_spectrum) == nfft2

    out = np.array(fft_np.fft.ifft(filt_spectrum))
    return out

def demux(muxed):
    return [muxed[idx::2] for idx in range(2)]

def combine(channels, gain, phi):
    assert len(channels) == 2
    assert phi >= 0 and phi < 360.0

    return channels[0] * 10**(gain/10) + channels[1] * 10**(-gain/10) * np.exp(1j*(phi/360.0)*2*np.pi)

def main():
    options = argument_parser().parse_args()

    f = open(options.infile, 'rb')
    buf = f.read()
    in_items = fft_np.frombuffer(buf, dtype=fft_np.csingle, count=114*12000)

    # channel 0 and 1 are from two different antennas, for now just use antenna 0
    channels = demux(in_items)
    downsampled = [filter_decimate(channels[0]), filter_decimate(channels[1])]

    om = make_osc_matrix()

    # sync matrix looks at all sets of 4 adjacent frequency bins, to correlate against sync vector
    sm = make_sync_matrix()

    bin_info = {}

    for phi in range(0, 350, 30):
        for g in range(-1, 9, 1):
            #combined = downsampled[0]
            combined = combine(downsampled, g, phi)
            combined /= np.std(combined)
            for d in range(8):
                shift = d/8 * DF
                om = make_osc_matrix(shift)
                for l in range(0, 1024, 25):

                    # chop up the input samples into 162 256-long vectors, each corresponding to 1 symbol
                    im = make_input_matrix(combined, lag=l)

                    # multiply by a matrix full of "oscillators" spaced 1.46Hz (one frequency shift bin apart).
                    # This is basically a discrete fourier transform...
                    ft = np.absolute(np.matmul(om, im.transpose()))

                    # compare each starting freq bin vs. the sync vector
                    z = np.matmul(sm,ft)
                    corr = np.matmul(z,np.array(sync_vec))
                    # save the best freq/delay for each bin
                    for item in enumerate(corr):
                        if item[0] not in bin_info or bin_info[item[0]]['sync'] < item[1]:
                            bin_info[item[0]] = {
                                'sync' : item[1],
                                'lag' : l,
                                'shift' : shift,
                                'gain' : g,
                                'phi' : phi
                            }

    # look at top 20 bins
    s = sorted(bin_info.items(), reverse=True, key=lambda x:x[1]['sync'])
    for (k,v) in s[:10]:
        print('bin={} af={} rf={}: sync={}, lag={} ({:.2f}s), shift={}, gain={}, phi={}'.format(k, bin_to_af_freq(k), bin_to_rf_freq(k), v['sync'], v['lag'], v['lag']/375.0-1, v['shift'], v['gain'], v['phi']))

if __name__ == '__main__':
    main()

