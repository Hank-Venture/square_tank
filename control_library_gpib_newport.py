# N. "Lushpuppy Facetat" Kruczek

# Contains all of the motion control functions for stages that are run through
# the Newport MM3000 controller.

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

# Move the newport-controlled stages a distance dist (int) relative to its
# current position. For details on newport commands, see the associated manual.
# This function DOES NOT wait for the motion to be complete, but does provide
# an expected amount of time until the motion will be finished. This allows the
# meta-code to move all of the stages at once and then wait for the longest
# running stage to finish.
def move_relative(s, stage, dist, SD):

    axis = SD[stage]["axis"]

    # Find out where the stage is currently and calculate where it should end up
    # Note - since function does not wait for motion to finish, stage position
    # is set by this final_pos variable. A seperate function is needed to check
    # if the stage ends up at the correct spot.

    curr_pos = get_position(s, axis)
    final_pos = int(curr_pos + dist)

    # Stage speed is used to calculate how long the motion will take. Ping the
    # controller to get that value. In general, V shouldn't change, but this is
    # a safety check in case someone has decided to change it.
    get_speed = write(s, axis + 'DV')
    spd_full = read(s)

    if abs(final_pos) < 1:
        move_to_limit(s, stage, axis, '+')
        final_pos = -20

    else:
        dist_st = str(dist)

        #get_accel = write(s, axis+'DA')

        # Make the move
        write(s, axis + 'PR' + dist_st)

        print("\nMoving " + stage + " " + dist_st + ". Will globally be at " +
            str(final_pos))

    # Calculate how long the motion will take.
    # Note - acceleration has not been accounted for. It shouldn't change from
    # its current large value, but I check for idiots above with the 'DV' command.
    # mind as well do it here too. Need to check what gets returned when pinged.
    spd_st = spd_full.find('_') + 1
    spd_ed = spd_full.find(' ')
    spd = float(spd_full[spd_st:spd_ed])/10.0

    ## Was really cutting it close, so added some slop
    t = abs(float(dist) / spd) + 1
    t_start = time.time()
    print("Will finish moving in " + str(t) + " seconds.\n")

    return final_pos, t_start, t

# MTM generates noise when on. Might be mitigated when motor is off. So do that.
# For details on the newport commands, see the associated manual.
def turn_off_motor(s, stage, axis):

    write(s, axis + 'MF')

    print('\n'+ stage + ' is off. A move command will restart it.\n')

# Get the newport controller to return the position of the stage associated
# with 'axis'. For details on the newport commands, see the associated manual.
def get_position(s, axis):

    write(s, axis + 'TP')

    pos_st = read(s)

    lab_loc = pos_st.find(' ')
    pos = int(pos_st[:lab_loc])

    return pos

# You can technically check if a newport controller stage is still moving using
# this command. The klingers don't have a corresponding command though, so this
# doesn't see much use in general. Instead, predicted timings are used.
def is_moving(s, stage, axis):
    write(s, 'TS')
    move_st = read(s)

    # See newport controller manual for details on the format of the bit string
    # that the 'TS' command returns.
    move_bits = [bin(ord(x))[2:].zfill(8) for x in move_st]
    len_num = int(axis)
    is_moving = move_bits[0][-len_num]

    if is_moving == 1:
        return True

    else:
        return False

# The newport stages can also be command to move to their limit switches.
# Doing this is nice for repeatability so it might see use even though the
# klinger's don't have a corresponding command for it.
def move_to_limit(s, stage, axis, limit):
    if limit == '+':
        limit = '\x1b' + limit
        dir_st = 'postive'
    else:
        dir_st = 'negative'

    write(s, axis + 'ML' + limit)

    print('\nMoving ' + stage + ' to its ' + dir_st + ' limit.\n')
