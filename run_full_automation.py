# N. "Lushpuppy Facetat" Kruczek
# v0.9

import serial
import numpy as np
import sys
import vm502
import time
import stage_lib as sl
import control_library_gpib_klinger as cl
import control_library_gpib_newport as ncl
import automated_stages as auto
import monoscan as ms
from random import randint

CNTRL_FL = 'stage_schedule.csv'

# Handles the high level commands to initiate stage motion and begin integration
def main(mono_port, counter_port, motor_conn, fname, SD, isPrac):

    # Get stage order as a safety precuation against people being dumb
    # and changing the order in the file for whatever reason.
    getord = open(CNTRL_FL, 'r')
    stage_ord_full = getord.readlines()
    getord.close()

    # Trim unused parts of header and turn into a list
    stage_ord_st = stage_ord_full[2]
    stage_ord_st = stage_ord_st[1:-1]
    stage_ord = stage_ord_st.split(',')

    # Read in all of the positions as a list of lists
    stage_pos = np.loadtxt(CNTRL_FL, delimiter = ',')

    for i in range(1, len(stage_pos)):
        # Move all of the stages to the positions listed in CNTRL_FL
        # Note that file contains FINAL positions. Code handles converting
        # that into the correct relative movement.
        SD, wait_t = auto.moveStages(motor_conn, stage_pos[i], SD, stage_ord)

        # moveStages returns the longest wait time for all of the motions.
        # Wait that amount of time for the movement process to complete
        time.sleep(wait_t)

        # Stage motion can be imperfect so, once stages have moved, make sure
        # they all ended up in the correct locations. This function also
        # serves as a secondary check to the wait time above.
        SD = auto.checkPositions(motor_conn, SD, stage_ord)

        # This might help the noise caused by the MTM, we will see.
        ncl.turnOffMotor(motor_conn, 'MTM', SD['MTM']['axis'])

        if isPrac:
            print('\nStep ' + str(i) + ' of ' + str(len(stage_pos)) +
                    ' complete. Move to next position?')
            nextStep = input('Y - Move again, N - exit code: ')

            if nextStep == 'N':
                motor_conn.close()
                exit()

        else:
            # Get them counts
            ms.integration(mono_port, counter_port, fname, str(SD['SA']['pos']))

            # Random safety check to make sure people don't walk away while
            # code is running. Deleting this part would be a pretty rude move.
            do_a_check = randint(0,100)
            if do_a_check == 1:
                input('You here? Hit enter to continue')

if __name__ == '__main__':
    if (len(sys.argv) < 6):
        print("Usage: monopmtd2scan.py <mono port> <counter port>"
                "<control port> filename practicerun")
        print("Where: ")
        print("<> indicates an associated COM port")
        print("filename is the output file")
        print("practicerun is either T or F, where T means only stage motions"
                " will be executed.")
        exit()

    mono_port = str(sys.argv[1])
    counter_port = str(sys.argv[2])
    control_port = str(sys.argv[3])
    fname = sys.argv[4]

    prac = sys.argv[5]
    if prac == 'T':
        isPrac = True
    elif prac == 'F':
        isPrac = False
    else:
        print('Final command line argument must be T or F.')
        exit()

    print("Monochromator Port: {0:s}".format(mono_port))
    print("Counter Port: {0:s}".format(counter_port))
    print("Control Port: {0:s}".format(control_port))
    print("Saving Data to " + fname)

    print('''\n                  !!!! User Warning !!!!
    This software is not smart. Using it risks damaging any/all
    of the square tank stages. This code does not know where the
    limits of the stages are. It also cannot detect any offsets
    in the motion of the stages that could lead to their positions
    being different from what their controller's display. This is
    particularly true for the swing arm. It is the responsibility
    of the user to ensure the code is enabled correctly and operating
    as expected throughout use. The code should not be left to
    run unattended. If you accept these terms, type 'ok' below:''')

    user_accept = input('')

    if user_accept == 'ok':

        cmd, SD = auto.initStages(control_port)

        print("Saving to file: {0:s}".format(fname))

        main(mono_port, counter_port, cmd, fname, SD, isPrac)

    else:
        print('\nSmart choice\n')
        exit()
