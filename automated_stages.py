# N. "Lushpuppy Facetat" Kruczek

# Handles the bulk motion of any of the square tank stages. This includes
# initialization, group movement + wait times, confirmation of positioning.

import stage_lib as sl
import control_library_gpib_klinger as cl
import control_library_gpib_newport as ncl
import time
import sys
import serial
import numpy as np

# Initializes all of the stages and controller for proper communication
def init_stages(gpib_port):
    SD = sl.SD

    cmdline = serial.Serial(gpib_port)

    # Puts the gpib controller into Read-after-Write mode
    # write commands with a ++ prefix are gpib controller commands
    cl.write(cmdline, "++auto 1")
    # Appends a carriage return to commands passed by the gpib controller
    cl.write(cmdline, "++eos 1")

    # Initialize the klinger stages. See functions for details
    SD = init_klingers(cmdline, "SA", SD)
    SD = init_klingers(cmdline, "UTM", SD)
    SD = init_klingers(cmdline, "ROT", SD)

    # Initialize the non-klinger controlled MTM (aka just get its position).
    stg = "MTM"
    lib = SD[stg]["lib"]
    lib.write(cmdline, "++addr " + SD[stg]["addr"])
    SD[stg]["pos"] = lib.get_position(cmdline, SD[stg]["axis"])

    return cmdline, SD

# Klinger velocities are set by R, S, and F parameters. This function gets the
# desired values entered and gets the position of each stage. For more info on
# Klinger velocity information, see the associated manuals
def init_klingers(cmd, stg, SD):

    # Send the values to the associated stage. R, S, and F values can be changed
    # in stage_lib, but this is not recommended without consulting the manaual.
    lib = SD[stg]["lib"]
    lib.write(cmd, "++addr " + SD[stg]["addr"])
    SD[stg]["hi_step"], SD[stg]["lo_step"], SD[stg]["acc_step"] =\
                lib.set_rate(cmd, stg, SD[stg]["R"], SD[stg]["S"], SD[stg]["F"])

    # Get the initial position of the stage. Requires interfacing with the
    # TK-2 boards, which reside at different addresses.
    lib.write(cmd, "++addr " + SD[stg]["talk_addr"])
    SD[stg]["pos"] = lib.get_position(cmd,'0')

    return SD

# Loop through the stages and move each one. This function does not wait for
# any single stage to be finished before moving the next stage.
def move_stages(cmd, stage_pos, SD, ord):

    # max_wait tracks which stage will take the longest. Presumably all of these
    # commands should be executed quickly so max_wait should be the best
    # indicator of wait time. The checkPositions function can serve as a
    # secondary check that everything is finished running.
    max_wait = 0.0
    for j in range(len(stage_pos)):
        stg = ord[j]
        new_pos = int(stage_pos[j])

        pos = SD[stg]["pos"]
        lib = SD[stg]["lib"]
        addr = SD[stg]["addr"]

        # Final stage positions are read in from the file but code only makes
        # relative movements. So calculate what the relative distance is.
        move_dist = int(new_pos - pos)

        lib.write(cmd, "++addr " + addr)

        # Only do stuff if the user wants a stage to move (duh)
        if abs(move_dist) > 0:
            # I like to move it move it
            SD[stg]["pos"], SD[stg]["time_st"], SD[stg]["time"] =\
                                    lib.move_relative(cmd, stg, move_dist, SD)

            if SD[stg]["time"] > max_wait:
                max_wait = SD[stg]["time"]

    return SD, max_wait

# Confirm that all of the stages ended up in the place we expected them to.
# If they didn't, try moving them there. If that doesn't work, make the user
# fix the problem.
# NOTE!!! In its current form, this basically just checks that the
# number listed on the controller display is the same as what you wanted
# it to be. It does not check for things like SA slippage.
def check_positions(cmd, SD, ord):

    for j in range(len(ord)):
        stg = ord[j]

        # Sanity check that no stage is still moving
        # I can imagine odd scenarios where it might rarely occur.
        dt = time.time() - SD[stg]["time_st"]

        if dt < SD[stg]["time"]:
            time_left = SD[stg]["time"] - dt
            #Put some slop on there just to be safe.
            time.sleep(time_left + 2.0)

        lib = SD[stg]["lib"]
        addr = SD[stg]["addr"]
        taddr = SD[stg]["talk_addr"]
        axis = SD[stg]["axis"]

        # moveRelative returns what the desired position was,
        # so this is our point of comparison
        planned_pos = SD[stg]["pos"]

        lib.write(cmd, "++addr " + taddr)

        # getPosition gives us a reading of where the stage currently is.
        curr_pos = lib.get_position(cmd, axis)
        SD[stg]["pos"] = curr_pos

        # This should be 0 in an ideal world
        dpos = int(planned_pos - curr_pos)

        # ct counts the number of times the stage has tried to move to the
        # desired position, but has failed. We don't want it to try forever so
        # we set some max number of times to try, after which the user is
        # brought in to address the situation. This will probably only really
        # help with the MTM since the klingers can always 'move' even if the
        # stage isn't physically moving, but that's a seperate problem.
        ct = 0
        ct_lim = 5
        while (abs(dpos) >= 1) and (ct < ct_lim):
            print('Looks like ' + stg + ' is not where it should be')
            print('Slewing to the correct position')

            # Move dpos, which should re-align the stage's current position with
            # the original desired position
            lib.write(cmd, "++addr " + addr)
            SD[stg]["pos"], SD[stg]["time_st"], SD[stg]["time"] =\
                                        lib.move_relative(cmd, stg, dpos, SD)

            # Wait for that movement to execute and then check the new position
            # to see if it is now correct
            time.sleep(SD[stg]["time"] + 1)
            lib.write(cmd, "++addr " + taddr)
            curr_pos = lib.get_position(cmd, axis)
            dpos = int(planned_pos - curr_pos)

            ct += 1

        ## If the code could not get the stage to the correct position in time
        if (ct == ct_lim) and (abs(dpos) >= 1):

            # The klingers can lock out manual movement if they're
            # currently addressing the TK-2 boards. So switch address back.
            lib.write(cmd, "++addr " + addr)

            print("\n!! " + stg + " cannot be moved to its desired position.")
            print("If you can fix it manually, move it to " + str(planned_pos))
            print("and hit enter. If it's a bigger issue (which it prob. is)")
            print("type 'exit' to quit the code and address the issue.")
            dowhatnow = input('')

            if dowhatnow == 'exit':
                cmd.close()
                exit()

            else:
                # If the user was successful, update the stage info
                SD[stg]["pos"] = planned_pos
                SD[stg]["time_st"] = time.time()
                SD[stg]["time"] = 0.0

    return SD
