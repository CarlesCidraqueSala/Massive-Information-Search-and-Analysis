import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import io

def f(n, k, beta):
    return k*(n**beta);

if __name__ == '__main__':

    N = [] # Numero total de palabras de cada índice 
    D = [] # numero diferente de palabras de cada índice

    novelasindexes = ["TXTnovelas.txt", "TXTnovelassAUX.txt", "TXTnovelasssAUX.txt", "TXTnovelassssAUX.txt"];

    for indexnov in novelasindexes:
        n = 0;
        d = 0;
        for line in reversed(open(indexnov).readlines()):
            line = line.strip();
            freq = float(line);
            n = n + freq;
            d = d + 1;
        print(indexnov,"Numero total de palabras = ", n,"Palabras diferentes = ", d);
        N.append(n);
        D.append(d);

    N_log = list(map(lambda x: np.log(x), N));
    D_log = list(map(lambda x: np.log(x), D));
    
    # Utilizamos método curve_fit
    popt, pcov = curve_fit(f, N, D);
    k = popt[0];
    beta = popt[1];
    print(k, beta);

    # Aplicamos la funcion f (de Heap )sobre cada uno de los numero totales de palabras obtenidos con los parametros k y beta ajustados por curve_fit 

    fit_arr     = list(map(lambda n: f(n, k, beta), N));
    fit_arr_log = list(map(lambda x: np.log(x), fit_arr));

    # plot
    plot_raw   = plt.plot(N, D, c='r', linewidth=2.0);   # real
    plot_heaps = plt.plot(N, fit_arr, c='g', linewidth=2.0, ls='-');   # Heaps
    plt.legend(["Real","Heap"], loc="upper left");
    plt.ylabel('#Palabras diferentes');
    plt.xlabel('#Palabras Totales')
    plt.show();