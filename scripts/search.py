from argparse import ArgumentParser
import numpy
from scipy import signal

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
    dp = -1*2*numpy.pi*f*DT
    return numpy.exp([1j*dp*i for i in range(n)])

def bin_to_baseband_freq(in_bin):
  #  assert in_bin >= 0 and in_bin < 128

   # return (in_bin - 64) * DF + DF/2
    return in_bin *DF

def make_input_matrix(input_samples, lag=0):
    in_vec = numpy.array(input_samples[lag:lag+162*256])
    out_mat = numpy.reshape(in_vec, [162,256])
    return out_mat

def make_osc_matrix():
    return numpy.array([osc(bin_to_baseband_freq(i), 256) for i in range(-64,64)])

def make_sync_matrix():
    return numpy.array([numpy.pad([-1,1,-1,1], (i,124-i)) for i in range(125)])

def filter_decimate(input_samples):
    nfft1=1474560
    nfft2=nfft1//32
    df=12000.0/nfft1;
    i0=int(1500.0/df+0.5);


    spectrum = numpy.fft.fft(input_samples, n=nfft1)
    filt_spectrum1 = spectrum[i0:i0+nfft2//2]
    filt_spectrum2 = spectrum[i0-nfft2//2:i0]
    filt_spectrum = numpy.concatenate((filt_spectrum1, filt_spectrum2))

    assert len(filt_spectrum) == nfft2

    out = numpy.fft.ifft(filt_spectrum)
    return out

def demux(muxed):
    return [muxed[idx::2] for idx in range(2)]

def main():
    options = argument_parser().parse_args()

    f = open(options.infile, 'rb')
    buf = f.read()
    in_items = numpy.frombuffer(buf, dtype=numpy.csingle, count=114*12000)

    channels = demux(in_items)
    downsampled = filter_decimate(channels[0])

    om = make_osc_matrix()
    sm = make_sync_matrix()
    for l in range(0, 1024, 32):
        im = make_input_matrix(downsampled, lag=l)

        ft = numpy.absolute(numpy.matmul(om, im.transpose()))
        z = numpy.matmul(sm,ft)
        corr = numpy.matmul(z,sync_vec)

        c = enumerate(corr)
        s = sorted(c, reverse=True, key=lambda x:x[1])
        print(s[:10])

if __name__ == '__main__':
    main()

