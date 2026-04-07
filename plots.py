from __future__ import division
import serial, sys
import numpy as np
import scipy
from array import array
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import time

# Configuration.
#fS = 75000  # Sampling rate.
fS = 150000  # Sampling rate.
fL = 50  # Cutoff frequency.
fH = 5500  # Cutoff frequency.
NL = 461  # Filter length for roll-off at fL, must be odd.
NH = 461  # Filter length for roll-off at fH, must be odd.

# Compute a low-pass filter with cutoff frequency fH.
hlpf = np.sinc(2 * fH / fS * (np.arange(NH) - (NH - 1) / 2))
hlpf *= np.blackman(NH)
hlpf /= np.sum(hlpf)

# Compute a high-pass filter with cutoff frequency fL.
hhpf = np.sinc(2 * fL / fS * (np.arange(NL) - (NL - 1) / 2))
hhpf *= np.blackman(NL)
hhpf /= np.sum(hhpf)
hhpf = -hhpf
hhpf[(NL - 1) // 2] += 1

# Convolve both filters.
h = np.convolve(hlpf, hhpf)
print(len(h))
#print(h)

# Applying the filter to a signal s can be as simple as writing
# s = np.convolve(s, h)

ser = serial.Serial("/dev/ttyACM1",115200)
print(ser.name)
buff = []
#buff = ser.readline()

DEBUG = True
CHART = False
M = 1.4698216
B = -116.4997

def r_d(x, base=5):
    return x - (x % base)

def quit(val):
    global ser
    print("quit")
    ser.write(b'>bye\n')
    ser.write(b'>run\n')
    ser.close()
    sys.exit()


#ser.write(b'>h\r')
ser.write(b'>hlt\r')
ser.write(b'>con\r')

while True:
    buffsum = 0
    bufffsum = 0
    buffmedian = 0
    cnt = 0
    ser_in = ""
    #print("writing cmd")
    ser.write(b'>dmp\r')        

    while len(ser_in) < 25:
        ser_in = ser.readline().split()
        

    #print("Buffer Length:",len(ser_in))

    try:
        print("len ser_in",len(ser_in))
        deviation = r_d(int(ser_in[0]),5)
        buff = [int(ser_in[x]) for x in range(len(ser_in))]
        med = int(np.average(buff[1:]))
        #med1 = sum(buff) / len(buff)
        #print("debug:",med, med1)
        buffm = [int(ser_in[x]) - med for x in range(len(ser_in))]
        #buff = np.array(buff)
        #bufff = np.convolve(buffm, hlpf)
        bufff = np.convolve(buffm, hhpf)
    
        umax = int(np.max(buff[250:3250]))
        umin = int(np.min(buff[250:3250]))
        up2p = umax-umin
        dup2p = M * up2p + B

        fmax = int(np.max(bufff[500:3250]))
        fmin = int(np.min(bufff[500:3250]))
        fp2p = fmax-fmin
        dfp2p = M * fp2p + B
        
        print("up2p / fp2p",int(dup2p),int(dfp2p),int(dup2p-dfp2p))

        # Compute the FFT
        fft_values = np.fft.fft(buffm)
        #freqs = np.fft.fftfreq(len(buff), 1/75_000)
        freqs = np.fft.fftfreq(len(buff), 1/fS)
        #print("length of freqs:",len(freqs))

        # Extract frequency components
        amplitudes = np.abs(fft_values)

        frequencies = freqs[:len(buff)//2]

        max_amplitude = np.max(amplitudes[:len(buff)//2])
        max_frequency = frequencies[np.argmax(amplitudes[:len(buff)//2])]
        
        fig = plt.figure("K3JSE Deviation Meter")
        
        #axes = plt.axes([0.81, 0.000001, 0.1, 0.075])
        #bnext = Button(axes, 'Quit',color="yellow")
        #bnext.on_clicked(quit)

        ax = fig.add_subplot(2, 1, 1)
        #ax.plot(buff[32:])
        ax.plot(buffm[32:])
        #ax.plot(bufff[240:len(buff)])
        plt.xlabel('Samples')
        plt.ylabel('ADC Count')
        plt.title('Input Signal - Deviation: ' + str(deviation) + " Hz")
        plt.grid()
        
        #ax = fig.add_subplot(3, 1, 2)
        ##ax.plot(buff[32:])
        #ax.plot(bufff[240:len(buff)])
        #plt.xlabel('Samples')
        #plt.ylabel('ADC Count')
        #plt.title('Input Signal - Deviation: ' + str(deviation) + " Hz")
        #plt.grid()


        ax = fig.add_subplot(2, 1, 2)
        # Major ticks every 20, minor ticks every 5
        major_ticks = np.arange(0, 6001, 1000)
        minor_ticks = np.arange(0, 6001, 250)

        ax.set_xticks(major_ticks)
        ax.set_xticks(minor_ticks, minor=True)

        # And a corresponding grid
        ax.grid(which='both')

        # Or if you want different settings for the grids:
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)
        #print("len amplitudes",len(amplitudes))
        #ax.plot(frequencies[0:400], amplitudes[:400])
        #
        # sample size / (sample rate / upper freq)  3500 / (150000 / 6000)
        sz = int(len(buff) / (fS / 6000))
        #print("Size:",sz)
        ax.plot(frequencies[0:sz], amplitudes[:sz])
        #ax.plot(frequencies[0:140], amplitudes[:140])

        plt.title('Frequency Components')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude')
    
        plt.tight_layout()            
        plt.show()
    except:
        print("exiting")
        ser.write(b'>bye\n')
        ser.write(b'>run\n')
        ser.close()
        sys.exit()

