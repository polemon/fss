# fss
Client app for the Microdia "Foot Switch" range of products, made by RDing (http://pcsensor.com/usb-keyboard.html)

## Introduction
The name "fss" is meant to be onomatopoeic.

It also may or may not be a shorthand for "foot switch settings" or something quite similar.

## Devices
So far this client supports only the "[DIY-KeyboardV1.0][http://pcsensor.com/diy-keyboard.html]" device.

The reason for that being, that it's the only one that I have. I may acquire the other products, though.
It seems pretty much all of these decices use the same chip, so it should work at least similarly.

## Dependencies
* Python 3.4 or higher
* hidapi

#### secondary dependencies
* python3-Xlib

I suggest installing these packages with `pip3`:

    pip3 install hidapi python3-xlib

Please be aware, that you need extra packages like Cython, and various libraries (and their source packages) when installing the dependencies.
I won't go into detail how to install these, here.

