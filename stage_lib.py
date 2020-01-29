# N. "Lushpuppy Facetat" Kruczek

import control_library_gpib_klinger as cl
import control_library_gpib_newport as ncl
import time

# Library for all of the stage parameters
# Don't change these.... please, don't
# but if you absolutly think you have to:
#   a) Talk to Nick K. (or who(m?)ever handles this code now) first
#   b) Make a new file so these parameters aren't lost
#   c) Take all responsability if things go to shit

## axis values for klinger-run stages do not matter.
## talk_addr values for newport-run stages need to be the same as their addr
## both are included to facility code re-use between controllers.
SD = {
    "SA" : {
        "max" : 17100,
        "min" : -200,
        "inv" : True,
        "home" : -10000000,
        "pos" : 0,
        "addr" : "1",
        "talk_addr" : "6",
        "R" : 235,
        "S" : 1,
        "F" : 17,
        "axis" : 0,
        "lib" : cl,
        "time" : 0,
        "time_st" : time.time()},
    "UTM" : {
        "max" : 30000,
        "min" : -30000,
        "inv" : False,
        "home" : -10000000,
        "pos" : 0,
        "addr" : "2",
        "talk_addr" : "7",
        "R" : 235,
        "S" : 1,
        "F" : 17,
        "axis" : 0,
        "lib" : cl,
        "time" : 0,
        "time_st" : time.time()},
    "ROT" : {
        "max" : 45000,
        "min" : -45000,
        "inv" : False,
        "home" : -10000000,
        "pos" : 0,
        "addr" : "3",
        "talk_addr" : "8",
        "R" : 235,
        "S" : 1,
        "F" : 17,
        "axis" : 0,
        "lib" : cl,
        "time" : 0,
        "time_st" : time.time()},
    "MTM" : {
        "pos" : 0,
        "home" : -10000000,
        "addr" : "4",
        "talk_addr" : "4",
        "axis" : "1",
        "lib" : ncl,
        "time" : 0,
        "time_st" : time.time()}}
