# Author: Nicholas Nell
# nicholas.nell@colorado.edu

from datetime import datetime

VM502_BAUD = 9600

VM502_GOTO = ' GOTO'
VM502_SCAN = ' NM'
#VM502_SCAN = ' >NM'
VM502_DONE = 'MONO-?DONE'
VM502_GRATING = '?GRATING'
VM502_GRATINGS = '?GRATINGS'
VM502_RATE = '?NM/MIN'
VM502_SRATE = ' NM/MIN'
VM502_RESET = 'MONO-RESET'
VM502_LAMBDA = '?NM'
VM502_MODEL = 'MODEL'
VM502_SERIAL = 'SERIAL'

VM502_TIMEOUT = 10.0
VM502_INIT_TIMEOUT = 60.0

def vm502_init(s):
    m = ''
    #s.write(VM502_RESET)
    vm502_write(s, VM502_RESET)
    while(True):
        n = s.inWaiting()
        if (n > 0):
            m += s.read(n).decode("utf-8")
        if (m[-4:] == 'ok\r\n'):
            return
    #pass
    # wait for 'ok\r\n'

def vm502_get_grating(s):
    m = ''
    vm502_write(s, VM502_GRATING)
    while(True):
        n = s.inWaiting()
        if (n > 0):
            m += s.read(n).decode("utf-8")
        if (m[-4:] == 'ok\r\n'):
            break

    print(m)
    return(m[len(VM502_GRATING) + 1])

def vm502_get_model(s):
    m = ''
    vm502_write(s, VM502_MODEL)
    while(True):
        n = s.inWaiting()
        if (n > 0):
            m += s.read(n).decode("utf-8")
        if (m[-4:] == 'ok\r\n'):
            break

    print(m)
    return(m[len(VM502_MODEL) + 1:-4])

def vm502_get_serial(s):
    m = ''
    vm502_write(s, VM502_SERIAL)
    while(True):
        n = s.inWaiting()
        if (n > 0):
            m += s.read(n).decode("utf-8")
        if (m[-4:] == 'ok\r\n'):
            break

    print(m)
    return(m[len(VM502_SERIAL) + 1:-4])

def vm502_get_rate(s):
    m = ''
    vm502_write(s, VM502_RATE)
    while(True):
        n = s.inWaiting()
        if (n > 0):
            m += s.read(n).decode("utf-8")
        if (m[-4:] == 'ok\r\n'):
            break

    print(m)
    return(m[len(VM502_RATE) + 1:-4])

def vm502_set_rate(s, rate):
    m = ''
    #print(rate + VM502_SRATE)
    #exit()
    vm502_write(s, rate + VM502_SRATE)
    while(True):
        n = s.inWaiting()
        if (n > 0):
            m += s.read(n).decode("utf-8")
        if (m[-4:] == 'ok\r\n'):
            break
        #print(m)

    print(m)
    nrate = vm502_get_rate(s)
    return(nrate)

def vm502_get_gratings(s):
    m = ''
    vm502_write(s, VM502_GRATINGS)
    while(True):
        n = s.inWaiting()
        if (n > 0):
            m += s.read(n).decode("utf-8", 'ignore')
        if (m[-4:] == 'ok\r\n'):
            break

    print(m)
    return(m[len(VM502_GRATINGS) + 1:-4])    

def vm502_goto(s, lam):
    #s.write(lam + VM502_GOTO)
    # Wait for return...
    # OK\r\n

    m = ''
    vm502_write(s, lam + VM502_GOTO)
    while(True):
        n = s.inWaiting()
        if (n > 0):
            m += s.read(n).decode("utf-8", 'ignore')
        if (m[-4:] == 'ok\r\n'):
            break

    print(m)
    #return(m[len(VM502_GRATINGS) + 1:-4])
    nlam = vm502_get_lambda(s)
    return(nlam)

def vm502_scan(s, lam):
    m = ''
    vm502_write(s, lam + VM502_SCAN)
    # while(True):
    #     n = s.inWaiting()
    #     if (n > 0):
    #         m += s.read(n).decode("utf-8", 'ignore')
    #     if (m[-4:] == 'ok\r\n'):
    #         break

    # print(m)

def vm502_done(s):
    m = ''
    vm502_write(s, VM502_DONE)
    while(True):
        n = s.inWaiting()
        if (n > 0):
            m += s.read(n).decode("utf-8", 'ignore')
        if (m[-4:] == 'ok\r\n'):
            break

    print(m)
    return(m[len(VM502_DONE) + 1:-4])

def vm502_get_lambda(s):
    m = ''
    vm502_write(s, VM502_LAMBDA)
    while(True):
        n = s.inWaiting()
        if (n > 0):
            m += s.read(n).decode("utf-8", 'ignore')
        if (m[-4:] == 'ok\r\n'):
            break

    print(m)
    return(m[len(VM502_LAMBDA) + 1:-4])
    
def vm502_lambda(s):
    s.write(VM502_LAMBDA)

    ts = datetime.now()
    ts2 = datetime.now()
    diff = ts2 - ts
    buf = ''
    while(diff < VM502_TIMEOUT):
        n = s.inWaiting()
        if (n > 0):
            buf += s.read(n)
        # Find ok\r\n
            
        diff = datetime.now() - ts

def vm502_write(s, m):
    m = bytes(m + "\r", "utf-8")
    s.write(m)
    
    
