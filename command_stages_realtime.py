# N. "Lushpuppy Facetat" Kruczek

# Top level code for running one-off stage motions for alignment.

#import serial
import numpy as np
import sys
import time
import stage_lib as sl
import control_library_gpib_klinger as cl
import control_library_gpib_newport as ncl
import automated_stages as auto

def main(motor_conn, SD):

    # Reusing code from the fully automated routine, so we define order and
    # position lists that get fed to the motion function
    stage_ord = ['SA','UTM','ROT','MTM']
    stage_pos = [0, 0, 0, 0]
    while True:
        stg = input('Move which stage? (SA, UTM, ROT, MTM, exit): ')

        if stg == 'exit':
            motor_conn.close()
            exit()

        # Check to ensure that a motor isn't still running.
        elif abs(time.time() - SD[stg]["time_st"]) < SD[stg]["time"]:
            dt = (time.time() - SD[stg]["time_st"])
            time_left = round(SD[stg]["time"] - dt,1)
            time_left_min = round(time_left/60.0,1)

            print('\n!! ' + stg + ' is still moving.')
            print('!! It has ' + str(time_left) + ' sec (' + str(time_left_min)
                    + ' min) left.')

        else:
            curr_pos = SD[stg]["pos"]
            print(stg + ' is currently at ' + str(curr_pos))

            # Bit of a roundabout setup, but entering distances as opposed to
            # positions seems more ideal for this but move_stages takes a final
            # position (which it then turns back into a distance). 
            dist_st = input('Move how much? ')
            dist = int(dist_st)
            new_pos = curr_pos + dist

            pos_loc = stage_ord.index(stg)
            stage_pos[pos_loc] = new_pos

            SD, wait_t = auto.move_stages(motor_conn, stage_pos, SD, stage_ord)

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Usage: command_stages_realtime.py <control port>")
        exit()

    control_port = str(sys.argv[1])

    print("Control Port: {0:s}".format(control_port))

    cmd, SD = auto.init_stages(control_port)

    main(cmd,SD)
