from __future__ import division
import serial, sys
import numpy as np
import scipy
from array import array
import matplotlib.pyplot as plt
import time

# Configuration.
fS = 75000  # Sampling rate.
fL = 250  # Cutoff frequency.
fH = 7500  # Cutoff frequency.
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

def r_d(x, base=5):
    return x - (x % base)

#ser.write(b'>h\r')
ser.write(b'>hlt\r')
ser.write(b'>con\r')

while True:
    buffsum = 0
    bufffsum = 0
    buffmedian = 0
    cnt = 0
    for _ in range(1):
        ser_in = ""
        #print("writing cmd")
        ser.write(b'>dmp\r')        

        while len(ser_in) < 25:
            ser_in = ser.readline().split()
        

        #print("Buffer Length:",len(ser_in))
        if DEBUG:
            try:
                print("len ser_in",len(ser_in))
                deviation = r_d(int(ser_in[0]),5)
                buff = [int(ser_in[x]) for x in range(len(ser_in))]
                med = int(np.average(buff[1:]))
                #med1 = sum(buff) / len(buff)
                #print("debug:",med, med1)
                buffm = [int(ser_in[x]) - med for x in range(len(ser_in))]
                #buff = np.array(buff)
                bufff = np.convolve(buffm, hlpf)
            
                umax = int(np.max(buff[250:2250]))
                umin = int(np.min(buff[250:2250]))

                fmax = int(np.max(bufff[500:2500]))
                fmin = int(np.min(bufff[500:2500]))
                
                print("Min / Max",umin,fmin,umax,fmax,umax-umin,fmax-fmin)

                # Compute the FFT
                fft_values = np.fft.fft(buffm)
                freqs = np.fft.fftfreq(len(buff), 1/75_000)
                #print("length of freqs:",len(freqs))
    
                # Extract frequency components
                amplitudes = np.abs(fft_values)

                frequencies = freqs[:len(buff)//2]

                max_amplitude = np.max(amplitudes[:len(buff)//2])
                max_frequency = frequencies[np.argmax(amplitudes[:len(buff)//2])]
                


                fig = plt.figure("K3JSE Deviation Meter")
                
                ax = fig.add_subplot(2, 1, 1)
                #ax.plot(buff[32:])
                ax.plot(bufff[240:])
                plt.xlabel('Samples')
                plt.ylabel('ADC Count')
                plt.title('Input Signal - Deviation: ' + str(deviation) + " Hz")
                plt.grid()
                
                #ax = fig.add_subplot(3, 1, 2)
                #ax.plot(bufff[250:5250])
                #plt.xlabel('Samples')
                #plt.ylabel('ADC Count')
                #plt.title('Filtered Input Signal')
                #plt.grid()

                ax = fig.add_subplot(2, 1, 2)
                # Major ticks every 20, minor ticks every 5
                major_ticks = np.arange(0, 6001, 1000)
                minor_ticks = np.arange(0, 6001, 250)

                ax.set_xticks(major_ticks)
                ax.set_xticks(minor_ticks, minor=True)
                #ax.set_yticks(major_ticks)
                #ax.set_yticks(minor_ticks, minor=True)

                # And a corresponding grid
                ax.grid(which='both')

                # Or if you want different settings for the grids:
                ax.grid(which='minor', alpha=0.2)
                ax.grid(which='major', alpha=0.5)
                #print("len amplitudes",len(amplitudes))
                #ax.plot(frequencies[0:400], amplitudes[:400])
                ax.plot(frequencies[0:200], amplitudes[:200])

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

        
        
        if (len(ser_in) > 500):
            
            cnt += 1
            asn = time.time_ns()
            buff = [int(ser_in[x]) -2084 for x in range(len(ser_in))]
            #med = np.average(buff)
            #print("median:",med)
            #buff = [int(ser_in[x])-med for x in range(len(ser_in))]
            #bufff = np.convolve(buff, h)
            #bufff = np.convolve(buff, hhpf)
            bufff = np.convolve(buff, hlpf)
            #bufff = array('h', (int(x) for x in bufff[range(len(bufff)-1)]))
            #buffmedian += np.average(buff[500-3500])
            buffsum += max(buff[2000:4000]) - min(buff[2000:4000])
            bufffsum += max(bufff[2000:4000]) - min(bufff[2000:4000])
            #buffsum += max(bufff[250:len(bufff)]) - min(buff[250:len(bufff)])
            #print("filter:",(time.time_ns()-asn)/ 1000000)
            med = np.median(buff)
            raw_avgp2p = buffsum / cnt
            filt_avgp2p = bufffsum / cnt
            #print('p2p:',med,int(raw_avgp2p),int(filt_avgp2p))
    
    if CHART:
      plt.figure()
      plt.subplot(211)
      #plt.plot(buff[150:1150])
      plt.plot(buff)
      plt.title("Captured Waveform - Audio: 1500Hz, Deviation: 2500Hz")
      plt.grid()
      #plt.show()
    
      plt.subplot(212)

      #plt.plot(bufff[600:1600])
      plt.plot(bufff)
      plt.title("Filtered Output")
      plt.grid(True)
    
      plt.tight_layout()
      plt.show()

    #buff = ser.readline()
    #buff = ser.readline()
    #sys.exit()

print(type(buff))
print(len(buff),buff)
buffx = [byte for byte in buff]
print(type(buffx))
#buffx = list(buff)
#print(type(buffx))
print(len(buff),buffx)
plt.plot(buffx)
#plt.grid()
plt.show()

ser.write('>x\n')
ser.close()
