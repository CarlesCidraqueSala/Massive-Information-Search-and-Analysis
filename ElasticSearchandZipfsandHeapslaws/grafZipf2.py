import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# Global a
a = 1;

def f(rank, b=1, c=1):
    return c/(rank+b)**a;

if __name__ == '__main__':
    
    freq = [];
    freq_log = [];
    freqF = [];
    freqF_log = [];

    for line in reversed(open("TXTnovelas.txt").readlines()):
        line = line.strip();
        num = float(line);
        freq.append(num);
        freq_log.append(np.log(num));

    ranks = range(1, len(freq)+1);

    # Utilizamos método curve_fit
    popt, pcov = curve_fit(f, ranks, freq);
    b = popt[0];
    c = popt[1];
    print(b, c);

    # Aplicamos la funcion f (Zipf) sobre cada uno de los rangos con los parametros b y c ajustados por curve_fit
    freqF = list(map(lambda rank: f(rank, b, c), ranks));
    freqF_log = list(map(lambda x: np.log(x), freqF));

    # plot
    plot_zipfs = plt.plot(freqF, c='g', linewidth=2.0, ls='-');
    plt.legend(["Zipfs"]);
    plt.axis([0, 500, 0, 206546]);
    plt.ylabel('Frecuencia');
    plt.xlabel('Rango (de más a menos frecuente)')
    plt.show();

    # log plot
    plot_raw   = plt.plot(np.log(range(1,len(freq_log)+1)),   freq_log,   c='r', linewidth=2.0);   # real log
    plot_zipfs = plt.plot(np.log(range(1,len(freqF_log)+1)), freqF_log, c='g', linewidth=2.0, ls='-');   # Zipf's log
    plt.legend(["Real","Zipfs"]);
    plt.ylabel('log(Frecuencia)');
    plt.xlabel('log(Rango) [de más a menos frecuente]');
    plt.show();
