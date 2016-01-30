import sys
import time
import signal

import hid
#from Xlib import XK, display

# module name and device taken from http://www.linux-usb.org/usb.ids
_VID = 0x0c45  # "Microdia"
_PID = 0x7403  # "Foot Switch"

# commands understood by the CoB chip
_INIT  = 0x80
_WRITE = 0x81
_QUERY = 0x82

# prepared lists for communication
# FIXME expand further?
class Comm:
    def query(self, sw_num):
        return [0x01, _QUERY, 0x08, sw_num, 0x00, 0x00, 0x00, 0x00]

    def write(self, sw_num):
        return [0x01, _WRITE, 0x08, sw_num, 0x00, 0x00, 0x00, 0x00]

    @property
    def init(self):
        return [0x01, _INIT, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00]

# index: raw code written to the switch matrix controller,
# value: Xlib keycode sent by the device to the system.
#
# In string mode, the first 0x7f values are the same as these, the
# second half (0x80 - 0xff), are the same keycodes as the first 0x7f,
# but with an extra keycode 50 (usually Shift_L) sent before the character keycode.
#
# example 1: while 0x05 sends 56, 0x85 sends 50,56.
# example 2: while 0x00, 0x01, 0x02, and 0x03 send nothing at all,
#            0x80, 0x81, 0x82, and 0x83 send a single 50 (Shift + nothing).
_keymap = [
 # 0x-0  0x-1  0x-2  0x-3  0x-4  0x-5  0x-6  0x-7  0x-8  0x-9  0x-a  0x-b  0x-c  0x-d  0x-e  0x-f
   None, None, None, None,   38,   56,   54,   40,   26,   41,   42,   43,   31,   44,   45,   46, # 0x0-
     58,   57,   32,   33,   24,   27,   39,   28,   30,   55,   25,   53,   29,   52,   10,   11, # 0x1-
     12,   13,   14,   15,   16,   17,   18,   19,   36,    9,   22,   23,   65,   20,   21,   34, # 0x2-
     35,   51,   51,   47,   48,   49,   59,   60,   61,   66,   67,   68,   69,   70,   71,   72, # 0x3-
     73,   74,   75,   76,   95,   96,  107,   78,  127,  118,  110,  112,  119,  115,  117,  114, # 0x4-
    113,  116,  111,   77,  106,   63,   82,   86,  104,   87,   88,   89,   83,   84,   85,   79, # 0x5-
     80,   81,   90,   91,   94,  135,  124,  125,  191,  192,  193,  194,  195,  196,  197,  198, # 0x6-
    199,  200,  201,  202,  142,  146,  138,  140,  136,  137,  139,  145,  141,  143,  144,  121, # 0x7-
    123,  122,  248,  248,  248,  129,  248,   97,  101,  132,  100,  102,  103,  248,  248,  248, # 0x8-
    130,  131,   98,   99,   93,  248,  248,  248,  248,  248,  248,  248,  119,  248,  248,  248, # 0x9-
    248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248, # 0xa-
    248,  248,  248,  248,  248,  248,  187,  188,  248,  248,  248,  248,  248,  248,  248,  248, # 0xb-
    248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248,  248, # 0xc-
    248,  248,  248,  248,  248,  248,  248,  248,  119,  248,  248,  248,  248,  248,  248,  248, # 0xd-
     37,   50,   64,  133,  105,   62,  108,  134,  172,  174,  173,  171,  169,  123,  122,  121, # 0xe-
    158,  166,  167,  136,  144,  185,  186,  184,  150,  160,  181,  148,  248,  248,  248,  248 # 0xf-
]

def mkkbdkeymap():
    _keymap = list(map(lambda x: x-8 if x else None, _keymap))

# bit pattern of mod key mapped to Xlib keycode
# I should mention, that the high-nibble mod keys are undocumented and not accessible via
# the original software supplied by the manufacturer.
_modmap = {
    0b00000001:  37, # Control_L
    0b00000010:  50, # Shift_L
    0b00000100:  64, # Alt_L
    0b00001000: 133, # Super_L (Windows key)
    0b00010000: 105, # Control_R
    0b00100000:  62, # Shift_R
    0b01000000: 108, # ISO_Level3_Shift (Alt_R)
    0b10000000: 134  # Super_R (right Windows key)
}

_mbutton = {
    'LEFT'  : 0b001,
    'RIGHT' : 0b010,
    'MIDDLE': 0b100
}

# NOLATCH works only 
_msgtype = {
    'NONE'   : 0b000,
    'KEY'    : 0b001,
    'MOUSE'  : 0b010,
    'STRING' : 0b100,
    'NOLATCH': 0x80
}

class Timeout():
    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0)

    def raise_timeout(self, *args):
        raise Timeout.Timeout()

class SwitchDef():
    ##
    # left Ctrl
    # right Ctrl
    # left Shift
    # right Shift
    # left Alt / Option
    # right Alt / Option (this is often set to ISO_Level3_Shift / AltGr)
    # left Super / Windows / Command
    # right Super / Windows / Command
    class STRING(): pass
    class EVENT(): pass

    type = None # either SwitchDef.STRING or SwitchDef.EVENT
    num  = None # switch number on switchboard matrix

    _charlist =       []  # string data (list of keycode values) if switch binds to a string
    _raw_charlist =   []  # this is gonna be a list containing the raw keycodes
    # TODO ^---- well, that thing isn't there yet
    
    _key =          None    # Xlib keycode (sent to the system)
    _raw_key =      None    # raw keycode (number set in the controller)
    noLatch =       False   # key down and key up on single push
    modkeys =       []      # modkey list
    buttonLeft =    False   # left mouse button
    buttonRight =   False   # right mouse button
    buttonMiddle =  False   # middle mouse button
    x_move =        0       # mouse movement on x-axis, positive is right
    y_move =        0       # mouse movement on y-axis, positive is down
    mouseWheel =    0       # mouse wheel movement, positive is up (button 4)

    @property
    def key(self):
        return self._key

    @property
    def raw_key(self):
        return self._raw_key

    @property
    def charlist(self):
        return self._string

    @property
    def raw_charlist(self):
        return self._raw_string

    @key.setter
    def key(self, val):
        try:
            v = _keymap.index(val)
        except ValueError:
            raise

        if v:
            self._key = val
            self._raw_key = v
            print("+++ DEBUG +++ raw key value: 0x%.2x" % v)

    @raw_key.setter
    def raw_key(self, val):
        self._raw_key = val
        self._key = _keymap[val]

    @charlist.setter
    def string(self, val):
        # TODO for now, lets just assign the values and be good with it...
        self._charlist = val

    @raw_charlist.setter
    def raw_key(self, val):
        # TODO yeah, same as above...
        self._raw_charlist = val


class FootSwitch:
    ##
    #  all data packets are at least eight bytes long
    #  and is aligined to the next modulus of that set of eight bytes.

    #  Key query:
    #      0x01 0x82 0x08 <sw_num> 0x00 0x00 0x00 0x00
    #        |    |            |
    #        | query command   |
    #        |                 |
    #      query length    0x01 to 0x0e


    #  Response for key and/or mouse settings:
    #      0x08 <msgtype> <modkey> <sw_code> <mbutton> <x-defl> <y-defl> <wheel>

    #  This message response is used for both, key events and mouse events.
    #  It is possible to combine a key and mousebutton event, the <msgtype> byte
    #  is then 0b011.
    #  The MSB of <msgtype> is set for single shot button presses.
    #  <x-defl> is -128 to 127, positive is right.
    #  <y-defl> is -128 to 127, positive is down.
    #  <wheel> is -128 to 127, positive is up.

    #  Response for strings:
    #      <length> 0x04 <keycode1> <keycode2> <keycode3> <keycode4> <keycode5> <keycode6>

    #  The <length> byte is (like the length of the regular key encoding) the length of
    #  the entire message. So the actual string is <length> - 2.
    #  the string response is split up by eight bytes (since always eight bytes have to be
    #  read).

    def __init__(self):
        self.product = ""

        self.dev = hid.device()
        self.path = self.__get_path()

    def open(self):
        self.dev.open_path(self.path)
        self.product = self.dev.get_product_string()

    def close(self):
        self.dev.close()

    def get_switch(self, sw_n):
        # print("+++ DEBUG +++ QRY: 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x" % (0x01, _READ, 0x08, sw_n, 0x00, 0x00, 0x00, 0x00))
        self.dev.write()
        time.sleep(0.05)

        response = SwitchDef()
        response.num = sw_n

        try:
            with Timeout(1):
                res = self.dev.read(8)

                if res[1] & _msgtype['NONE']:
                    return response # return empty respnse object

                if res[1] & _msgtype['STRING']:
                    response.type = SwitchDef.STRING
                    length = res[0] - 2 # check if something like negative 
                    # TODO decode string
                    # print("+++ DEBUG +++ RES: 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x" % (res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7]))
                    print("+++ DEBUG +++ string length: ")

                    return response # immediately return string object

                # set response type inside so UNKNOWN type pass through.
                if res[1] & _msgtype['MOUSE']:
                    response.type = SwitchDef.EVENT

                    # take care of mouse buttons
                    if res[4] & _mbutton['LEFT']:
                        response.buttonLeft = True

                    if res[4] & _mbutton['RIGHT']:
                        response.buttonRight = True

                    if res[4] & _mbutton['MIDDLE']:
                        response.buttonMiddle = True

                    # take care of mouse movement
                    response.x_move = res[5]
                    if res[5] > 127:
                        response.x_move = res[5] - 256

                    response.y_move = res[6]
                    if res[6] > 127:
                        response.y_move = res[6] - 256

                    # this is technically a mouse button, but whatever...
                    response.mouseWheel = res[7]
                    if res[7] > 127:
                        response.mouseWheel = res[7] - 256

                if res[1] & _msgtype['KEY']:
                    response.type = SwitchDef.EVENT

                    response.raw_key = res[3] # this takes care of .key

                    for (k, v) in _modmap:
                        if res[2] & k:
                            response.modkeys.append(v)
                    

                # FIXME must check if combines with only mouse move or even string type
                if res[1] & _msgtype['NOLATCH']:
                    response.noLatch = True

                print("+++ DEBUG +++ RES: 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x 0x%.2x" % (res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7]))
        except Timeout.Timeout:
            pass

        return response

    ##
    # Init command:
    #    0x01 0x80 0x08 <sw_num> 0x00 0x00 0x00 0x00
    #      |    |           |
    #      | Init command   | 
    #      |                |
    #    Command length  switch number
    #
    #    It is unclear why the original software provided by the manufacturer
    #    sets <sw_num> to a number > 0x00. simply sending
    #        0x01 0x80 0x08 0x00 0x00 0x00 0x00 0x00
    #    seems to work as expected (clearing all keys to all 0x00's).
    def init(self):
        self.dev.write(Comm.init())

    def __get_path(self):
        devs = hid.enumerate(_VID, _PID)

        for i in devs:
            if i['interface_number'] == 1:
                return i['path']

    def __del__(self):
        self.dev.close()
