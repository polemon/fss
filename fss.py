#!/usr/bin/env python3
import sys
import getopt
from microdia import FootSwitch, SwitchDef

from Xlib import XK, display

def print_switch(sw):
    if sw.type == SwitchDef.STRING:
        print("switch %d: string" % sw.num)
    elif sw.type == SwitchDef.EVENT:
        print("switch %d: event" % sw.num)
        bl = ""
        ml = ""
        if sw.buttonLeft:
            bl = "left"

        if sw.buttonRight:
            if bl != "":
                bl += " "

            bl += "right"

        if sw.buttonMiddle:
            if bl != "":
                bl += " "

            bl += "middle"

        if bl == "":
            bl = "(none)"

        if sw.noLatch:
            print("  action: non-latching")
        else:
            print("  action: latching")

        if sw.key != None:
            print("  key: %d, raw code: 0x%.2x" % (sw.key, sw.raw_key))

        if sw.modCtrlL:
            ml = "Ctrl"

        if sw.modShift:
            if ml == "":
                ml += " "
            
            ml += "Shift"

        if sw.modAlt:
            if ml == "":
                ml += " "

            ml += "Alt/Option"

        if sw.modSuper:
            if ml == "":
                ml += " "

            ml += "Super/Win/Command"

        if ml == "":
            ml = "(none)"

        print("  mod keys: %s" % ml)

        print("  mouse buttons: %s" % bl)
        print("  mouse movement: x-axis: %d, y-axis: %d, mouse wheel: %d" % (sw.x_move, sw.y_move, sw.mouseWheel))
    else:
        print("switch %d: not initialized or not present" % sw.num)

def usage():
    with open("usage.text", 'r') as usage_f:
        for line in usage_f:
            print(line, end='')

def main():
    reading = True # determins if we're reading or writing, etc.
    switch = SwitchDef()

    shortopts = "hs:k:lrmx:y:w:"
    longopts  = ["help", "switch=", "key=", "nolatch"
                "ctrl", "shift", "alt", "option", "super", "win", "command",
                "left", "right", "middle",
                "wheel=",
                "string="]

    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-s", "--switch"):
            # TODO check for input sanity
            switch.num = int(arg)
        elif opt in ("-k", "--key"):
            reading = False
            try:
                switch.key = arg
            except ValueError:
                print("key »%s« not recognized" % arg)
                sys.exit(2)

    sw_matrix = FootSwitch()
    sw_matrix.open()

    print("Device: %s" % sw_matrix.product)

    if reading:
        if switch.num:
            print_switch(sw_matrix.get_switch(switch.num))
        else:
            for i in range(1, 15):
                print_switch(sw_matrix.get_switch(i))
    else:
        if not switch.num:
            print("provide a switch number!")
            usage()
            sys.exit(2)
        


    sw_matrix.close()

    sys.exit(0)

if __name__ == "__main__":
    main()
