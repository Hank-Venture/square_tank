# N. "Lushpuppy Facetat" Kruczek

# Contains all of the motion control functions for stages that are run through
# the Klinger CC1.2 controllers

import time

## Credit N. Nell for the serial stuff
def write(s, m):

    m = bytes(m + "\n", "utf-8")
    s.write(m)

def read(s):

    m = ''

    while(True):
        n = s.inWaiting()

        if (n > 0):
            m += s.read(n).decode("utf-8")

        if m.find('\r') != -1:
            break

    return m

# Set (R)ate, (S)lope, and step rate (F)actor, which define how a stage
# accelerates and what its max and min speeds are. Those values are used
# for timing how long a motion will take.
def set_rate(s, stage, R, S, F):
    write(s, "R " + str(R))
    write(s, "S " + str(S))
    write(s, "F " + str(F))

    # Use int here since it rounds down and the +7.5 is technically a +/-7.5.
    # Since these things will be used for timing measurements I want the value
    # to err on the side of being too long. These equations come from the
    # Klinger manual and that should be consulted for additional details.
    hi_steps_sec = int(10.0**6 / (80.0 * (256 - R) + 10.0 * F + 75.0 + 7.5))
    lo_steps_sec = int(10.0**6 / (80.0 * (256 - R) + 10.0 * (255 - S) + 75.0 + 7.5))
    accel_steps = int((255.0 - F) / S)

    print('\n'+ stage + ' will move from ' + str(lo_steps_sec) + ' stps/sec to '
            + str(hi_steps_sec) + ' stps/sec across ' + str(accel_steps) +
            ' steps when slewing.\n')

    return hi_steps_sec, lo_steps_sec, accel_steps

# Move the klinger-controlled stages a distance dist (int) relative to its
# current position. For details on klinger commands, see the associated manual.
# This function DOES NOT wait for the motion to be complete, but does provide
# an expected amount of time until the motion will be finished. This allows the
# meta-code to move all of the stages at once and then wait for the longest
# running stage to finish.
def move_relative(s, stage, dist, SD):

    # Find out where the stage is currently and calculate where it should end up
    # Note - since function does not wait for motion to finish, stage position
    # is set by this final_pos variable. A seperate function is needed to check
    # if the stage ends up at the correct spot.
    pos = SD[stage]["pos"]
    new_pos = pos + dist

    INV = SD[stage]["inv"]
    MAXL = SD[stage]["max"]
    MINL = SD[stage]["min"]

    # Klinger commands are DUMB.
    # Require a direction command to be sent first, so we determine that here.
    # Also, trim the '-' sign from the distance since that is sent separatley.
    dist_st = str(dist)
    if dist >= 0:
        dir = '+'
    else:
        dist_st = dist_st[1:]
        dir = '-'

    # The swing arm is extra dumb and it has its directions flipped between
    # manual commands and computer commands. So, account for that here.
    if INV:
        if dir == '+':
            dir = '-'
        else:
            dir = '+'

    # Check to make sure the final position isn't outside of the stage_lib
    # defined limits of each stage. Those def need to be tweaked, but I wanted
    # that functionaility in here in some capacity. Need to better fold this
    # error triggering into the overall code functionaility.
    if (new_pos > MAXL) or (new_pos < MINL):
        if stage != 'SA':
            print("\n!! Final position (=" + str(new_pos) + ") is out of " +
                    stage + " range (" + str(MINL) + " to " + str(MAXL) +
                    "), not executing.\n")
        else:
            print("\n!! Final position (=" + str(-new_pos) + ") is out of " +
                    stage + " range (" + str(-MAXL) + " to " + str(-MINL) +
                    "), not executing.\n")

        return pos, time.time(), 0

    # gpib controller manual claims it can't handle '+' being sent without
    # an escape character. So if we are moving in a positive direction, append
    # that character. Gotta check if this is actually true.
    if dir == '+':
        write(s, "\x1b" + dir)
    else:
        write(s, dir)

    # 'scend it
    write(s, "N " + dist_st)
    write(s, "G")

    print("\nMoving " + stage + " " + str(dist) + ". Will globally be at " +
            str(new_pos) + "\n")

    # Determine how long the motion will take.

    # If the distance is shorter than the ramp up + ramp down length, then it
    # will just happen at the slowest speed.
    if dist <= 2 * SD[stage]["acc_step"]:

        tot_time = float(dist) / SD[stage]["lo_step"]

    # If the distance is longer, account for the speed up/slow down time to
    # calculate the duration. See the Klinger manual for more information.
    else:
        # An upper limit of the ramp time for ease of calculation
        ramp_time = 2 * SD[stage]["acc_step"] / SD[stage]["lo_step"]

        # The rest of the time is spent at high speed
        hispd_time = (dist - SD[stage]["acc_step"]) / SD[stage]["hi_step"]
        tot_time = abs(ramp_time + hispd_time)

    print("\n" + stage + " will finish moving in " + str(round(tot_time,1)) +
            " sec.\n")

    return new_pos, time.time(), tot_time

# Straight forward. Meta code handles addressing the correct board, since
# you need to talk to the TK-2 boards in the Klinger boxes.
def get_position(s, axis):

    pos_st = read(s)

    pos = int(pos_st)

    return pos

# Obsolete command for setting a 'home' position. It's really just useful for
# making 'absolute' motion commands. But home is defined to be 0 and only
# positive motions are allowed relative to it, so that isn't necessary.
# Function remains so that the functionality can be introduced if desired,
# but should be tested first
def set_home(s, stage, pos):
    print("\nSetting " + stage + " home at " + str(pos) + "\n")
    write(s, "A")

    return pos

# Obsolete command for moving to some position relative to the user set 'home'.
# Fairly redundent with moving to a relative position and is more limited
# because negative absolute positions are not allowed (as far as I can tell
# from the manual). Function remains so that it can be introduced if desired,
# but should be tested first.
def move_absolute(s, stage, pos, old_pos, home, max):
    if home < -9999999:
        print("\n !! " + stage + " home has not been set. Cannot move\n")

    else:
        tot_dist = int(pos) + int(home)

        if tot_dist > max:
            print("\n!! Global Position (=" + str(tot_dist) + ") is out of " +
                    stage + " range (=" + str(max) + "), not executing.\n")
            return old_pos

        else:
            print("\nMoving to position " + str(pos) + " relative to home.")
            print("This puts it at " + str(tot_dist) + " globally.\n")

            write(s, "P " + pos)
            return tot_dist
