# Original framework by N. "I just wanna fly" Nell
# Crappy edits provided by N. "Lushpuppy Facetat" Kruczek
# v0.9

import serial
import numpy as np
import sys
import vm502
import time

# Run a loop of whatever monochromator + counter stuff you want
def integration(mp, cp, fname, sa_pos):

    pkuplam = '118.0'
    # Wavelengths for scan
    LAMBDA = ['0.0', '65.0', pskuplam, '65.0', '0.0']

    # Number of samples to average per wavelength
    N = 5

    # Open the mono and counter ports
    ms = serial.Serial(mp, 9600, timeout = 5.0)
    cs = serial.Serial(cp, 9600, timeout = 3.0)

    cs.reset_input_buffer()
    print(cs.read_until())

    # get current wavelength of the mono
    cl = vm502.vm502_get_lambda(ms)
    print("Wavelength: {0:s}".format(cl))

    flux = []
    fstd = []
    dt = []

    # Loop through the wavelengths taking N samples at each one except 0 nm
    for wav in LAMBDA:

        cl = vm502.vm502_goto(ms, wav)
        print("Wavelength: {0:s}".format(cl))

        # 0 is included to correct for mono hysteresis. Don't record its values.
        if wav != '0.0':
            # Safety to make sure mono is settled
            time.sleep(1.0)

            # Get N samples and append. Also record time the sample
            # was taken to improve incident extrapolation
            f, fdev = read_n_samples(cs, N)
            flux.append(f)
            fstd.append(fdev)
            dt.append(time.time())
            print("Flux: {0:f}, std: {1:f}".format(f, fdev))

        else:
            flux.append(0.0)
            fstd.append(0.0)

    # Record to the same file for each measurement
    dat = open(fname,'a')

    # Dark is assumed to be the average of the values measured on either
    # side of the light measurement
    dark_avg = (flux[1] + flux[3]) / 2.0
    dark_std = sqrt( (fstd[1]**2 + fstd[3]**2) / 4.0)

    dat.write(sa_pos + ',' + str(flux[2]) + ',' + str(fstd[2]) + ','
                + str(dark_avg) + ',' + str(dark_std) + ',' + str(dt[2]) + '\n')

    dat.close()
    print(LAMBDA[2])
    print(flux[2])
    print(fstd[2])

    cl = vm502.vm502_goto(ms, pkuplam)

    cs.close()
    ms.close()

# Read N samples from counter and return average
def read_n_samples(s, n):
    s.reset_input_buffer()
    print(s.read_until())
    #print(s.read_until())

    l = []
    for i in range(n):
        v = s.read_until()

        v = np.float(v.decode('ASCII').replace(',', ''))
        l.append(v)


    a = np.array(l)
    return(np.average(a), np.std(a))
