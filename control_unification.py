import stage_lib as sl
import control_library_gpib_klinger as cl
import control_library_gpib_newport as ncl
import time
import sys
import serial
import numpy as np


SD = sl.SD


def main(gpib_port):

    cmdline = serial.Serial(gpib_port)

    cl.write(cmdline,"++auto 1")
    cl.write(cmdline,"++eos 1")

    ## SA
    stg = "SA"
    lib = SD[stg]["lib"]
    lib.write(cmdline,"++addr "+SD[stg]["addr"])
    SD[stg]["hi_step"], SD[stg]["lo_step"], SD[stg]["acc_step"] = lib.setRate(cmdline, stg, SD[stg]["R"], SD[stg]["S"], SD[stg]["F"])

    lib.write(cmdline,"++addr "+SD[stg]["talk_addr"])
    SD[stg]["pos"] = lib.getPosition(cmdline,'1')

    ## UTM
    stg = "UTM"
    lib = SD[stg]["lib"]
    lib.write(cmdline,"++addr "+SD[stg]["addr"])
    SD[stg]["hi_step"], SD[stg]["lo_step"], SD[stg]["acc_step"] = lib.setRate(cmdline, stg, SD[stg]["R"], SD[stg]["S"], SD[stg]["F"])

    lib.write(cmdline,"++addr "+SD[stg]["talk_addr"])
    SD[stg]["pos"] = lib.getPosition(cmdline,'1')


    ## ROT
    stg = "ROT"
    lib = SD[stg]["lib"]
    lib.write(cmdline,"++addr "+SD[stg]["addr"])
    SD[stg]["hi_step"], SD[stg]["lo_step"], SD[stg]["acc_step"] = lib.setRate(cmdline, stg, SD[stg]["R"], SD[stg]["S"], SD[stg]["F"])

    lib.write(cmdline,"++addr "+SD[stg]["talk_addr"])
    SD[stg]["pos"] = lib.getPosition(cmdline,'1')


    ## MTM
    stg = "MTM"
    lib = SD[stg]["lib"]
    lib.write(cmdline,"++addr "+SD[stg]["addr"])
    SD[stg]["pos"] = lib.getPosition(cmdline,'1')

    cmd = ''
    while True:
        print('\nAvailable stages - SA, UTM, ROT, MTM, checkpos')
        cmd = input('Which stage (or exit): ')

        if cmd == 'exit':
            cmdline.close()
            exit()

        elif cmd not in SD.keys() and cmd != 'checkpos':
            print('\n!! Stage name not recognized.\n')

        elif cmd == 'checkpos':
            for i in SD.keys():
                lib = SD[i]["lib"]
                addr = SD[i]["addr"]
                taddr = SD[i]["talk_addr"]
                axis = SD[i]["axis"]
                pos = SD[i]["pos"]

                lib.write(cmdline,"++addr " + taddr)

                curr_pos = lib.getPosition(cmdline,axis)
                dpos = int(pos - curr_pos)

                ct = 0
                while abs(dpos) >= 1 and ct < 1:
                    print('Looks like ' + i + 'is not where it should be')
                    print('Slewing to the correct position')
                    dist_st = str(dpos)
                    if i != 'MTM' and dpos > 0:
                        dist_st = '+' + dist_st
                    lib.moveRelative(cmdline, i, dist_st, SD)

                    time.sleep(5)
                    lib.write(cmdline,"++addr " + taddr)
                    curr_pos = lib.getPosition(cmdline,axis)
                    dpos = int(pos - curr_pos)


                    ct += 1

        elif abs(time.time() - SD[cmd]["time_st"]) < SD[cmd]["time"]:
            dt = (time.time() - SD[cmd]["time_st"])
            time_left = round(SD[cmd]["time"] - dt,1)
            time_left_min = round(time_left/60.0,1)

            print('\n!! ' + cmd + ' is still moving.')
            print('!! It has ' + str(time_left) + ' sec (' + str(time_left_min) + ' min) left.')

        else:
            pos = SD[cmd]["pos"]
            home = SD[cmd]["home"]
            lib = SD[cmd]["lib"]
            addr = SD[cmd]["addr"]

            lib.write(cmdline,"++addr " + addr)

            if home > -9999999:
                print('\n' + cmd + ' is currently at ' + str(pos) + ' globally, ' + str(pos-home) + ' rel. to home')
            else:
                print('\n' + cmd + ' is currently at ' + str(pos) + ' globally. Home has not been set.')

            action = input('What action (rel, motoroff (for MTM), limit (for MTM), help): ')
            ### Need checks for MTM vs. Klinger

            if action == 'rel':
                dist_st = input('Move how much: ')

                SD[cmd]["pos"], SD[cmd]["time_st"], SD[cmd]["time"] = lib.moveRelative(cmdline, cmd, dist_st, SD)

            elif action == 'help':
                print('Dialing 911')

            elif action == 'motoroff' and cmd == 'MTM':

                lib.turnOffMotor(cmdline, cmd, SD[cmd]["axis"])

            elif action == 'limit' and cmd == 'MTM':
                limit = input('Which limit? (+/-): ')
                lib.moveToLimit(cmdline, cmd, SD[cmd]["axis"], limit)

            else:
                print('Does not compute')


if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Usage: control_loop.py <gpib_to_usb port>")
        exit()

    port = sys.argv[1]
    print("GPIB Port: {0:s}".format(port))

    print("\n!!!! REMINDER !!!!")
    print("This code is not intelligent. It is not guarenteed to catch your mistakes.")
    print("Some safeties have been implemented but are not fool proof.")
    print("Run code at air to ensure correct operation before using under vac.")
    print("!!!!!!!!!!!!!!!!!!\n")

    main(port)
