from argparse import ArgumentParser
import numpy
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

def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--infile", dest="infile", type=str, default='in.dat',
        help="Set infile [default=%(default)r]")
    return parser


def osc(f, n, dt=1.0/375.0):
    dp = 2*numpy.pi*f*dt
    return numpy.exp([1j*dp*i for i in range(n)])

def bin_to_freq(in_bin):
    return in_bin * 375.0/256.0

def bin_power(in_samples, in_bin, fshift=0):
    assert len(in_samples) == 256
    f = bin_to_freq(in_bin)+fshift
    m = osc(f, 256)
    d = numpy.vdot(m, in_samples)
    mag = numpy.absolute(d)
    return mag

def sync(in_samples, start_bin, fshift=0, lag=0):
    p = []
    for i in range(162):
        p.append([bin_power(in_samples[i*256+lag:(i+1)*256+lag], start_bin+b, fshift) for b in range(0,4)])

    cmet = [p[i][1]+p[i][3]-(p[i][0]+p[i][2]) for i in range(0, 162)]
    correlation = numpy.dot(cmet, sync_vec)
    return correlation

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

    for l in range(0,1024,32):
        correlation = []
        for i in range(1,124):
            correlation.append((i, sync(downsampled, i, lag=l)))
    
        s = sorted(correlation, reverse=True, key=lambda x: x[1])
        print(l, s[:10])

if __name__ == '__main__':
    main()

