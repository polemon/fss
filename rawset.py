#!/usr/bin/env python3
import hid
import time

_VID = 0x0c45
_PID = 0x7403

devs = hid.enumerate(_VID, _PID)
for i in devs:
    if i['interface_number'] == 1:
        path = i['path']

dev = hid.device()
dev.open_path(path)

print(dev.get_product_string())

dev.write([0x01, 0x80, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00])
time.sleep(0.2)

s_char = 0x04

print("writing...")
for i in range(0, 14):
    dev.write([0x01, 0x81, 0x08, i + 1, 0x00, 0x00, 0x00, 0x00])
    time.sleep(0.1)
    #dev.write([0x08, 0x04, s_char + i*6, s_char + i*6 + 1, s_char + i*6 + 2, s_char + i*6 + 3, s_char + i*6 + 4, s_char + i*6 + 5 ])
    dev.write([0x08, 0x01, 0x00, s_char + i, 0x00, 0x00, 0x00, 0x00 ])
    time.sleep(0.1)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

for i in range(1, 15):
    dev.write([0x01, 0x82, 0x08, i, 0x00, 0x00, 0x00, 0x00])
    time.sleep(0.1)
    print("%2i: [ 0x%.2x  0x%.2x  0x%.2x  0x%.2x  0x%.2x  0x%.2x  0x%.2x  0x%.2x ]" % ((i,) +  tuple(dev.read(8))))
    time.sleep(0.1)
