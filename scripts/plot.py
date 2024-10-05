import requests
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy

def get_spots():
    url = "http://db1.wspr.live/?query=select * from wspr.rx WHERE rx_sign LIKE 'N1VF/L%' AND code = '1' AND time > (NOW() - INTERVAL 1 DAY) FORMAT JSON"
    r = requests.get(url)
    data = r.json()['data']

    ret = {}
    for d in data:
        if d['tx_sign'] not in ret:
            ret[d['tx_sign']] = []
        ret[d['tx_sign']].append(d)

    return ret

def main():
    s = get_spots()

    # filter singletons
    filtered = {}
    for (k,v) in s.items():
        if len(v) > 1 and k != 'N1VF':
            filtered[k] = v

    dtime = [] 
    snr = {}
    for (tx,spots) in filtered.items():
        snr[tx] = {}
        for spot in spots:
            thetime = datetime.strptime(spot['time'], '%Y-%m-%d %H:%M:%S')
            dtime.append(thetime)
            if thetime not in snr[tx]:
                snr[tx][thetime] = {}
            snr[tx][thetime][spot['rx_sign']] = spot['snr']


    dtime = sorted(dtime)
    fig, axs = plt.subplots(len(snr.keys()), sharex=True, sharey=True)
    if len(snr.keys()) == 1:
        axs = [axs]
    for (i, (tx,txsnr)) in enumerate(snr.items()):
        axs[i].set_title(tx)
        axs[i].plot(dtime, [snr[tx][t]['N1VF/L1'] if t in snr[tx] and 'N1VF/L1' in snr[tx][t] else numpy.nan for t in dtime], '+', label="Active Vertical")
        axs[i].plot(dtime, [snr[tx][t]['N1VF/L2'] if t in snr[tx] and 'N1VF/L2' in snr[tx][t] else numpy.nan for t in dtime], '+', label="Res. Loop")
        axs[i].plot(dtime, [snr[tx][t]['N1VF/L3'] if t in snr[tx] and 'N1VF/L3' in snr[tx][t] else numpy.nan for t in dtime], '+', label="Diversity")
        axs[i].plot(dtime, [snr[tx][t]['N1VF/L3'] if t in snr[tx] and 'N1VF/L3' in snr[tx][t] and len(snr[tx][t].keys()) == 1 else numpy.nan for t in dtime], 'gx', label='Diversity Bonus Spot')
        axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        axs[i].grid(visible=True)
        axs[i].legend()
    fig.set_figwidth(17)
    fig.set_figheight(11)
    plt.show()

if __name__ == '__main__':
    main()
