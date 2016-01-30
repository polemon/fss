# fss
Client app for the Microdia "Foot Switch" range of products, made by RDing (http://pcsensor.com/usb-keyboard.html)

## Introduction
The name "fss" is meant to be onomatopoeic.

It also may or may not be a shorthand for "foot switch settings" or something quite similar.

## Devices
So far this client supports only the "[DIY-KeyboardV1.0](http://pcsensor.com/diy-keyboard.html)" device.

The reason for that being, that it's the only one that I have. I may acquire the other products, though.
It seems pretty much all of these devices use the same chip, so it should work at least similarly.

Even though they're all identify themselves as "FootSwitch", many of these products obviously aren't meant
to be operated with feet. Either that, or the small six-button remote control is for people with very small feet.

## Dependencies
* Python 3.4 or higher
* hidapi

#### Secondary dependencies
* python3-xlib

I suggest installing these packages with `pip3`:

    pip3 install hidapi python3-xlib

Please be aware, that you need extra packages like Cython, and various libraries (and their source packages) when installing the dependencies.
I won't go into detail how to install these, here.

## Planned features
This is still too vague to put into a bullet list, so here's me being wordy:

The whole thing kinda depends on the user's knowledge about keycodes, and especially the difference in keycodes used within X, and by `kbd` on a linux console.
That's not exactly ideal...

A GUI might be nice, too.

## Things that don't make sense
The program understands `--super`, `--win`, `--command` to set the left keycode for the respective *left* mod keys,
but only `--rightsuper` to set the *right* mod key, for example. This applies to all the mod key selectors.

There are two reasons for that:
 1. I don't know these keys are dealt with on OSX, so I can't just assume `--rightoption` or something.
 2. They don't even make much sense on Linux either, because they often map to vastly different types of mod keys.

Setting the right keys is actually undocumented. The original Windows software is unable to set the right keys.
I guess one might say the left keys can be considered *default*.

## Links
 * Project on github: https://github.com/polemon/fss
 * gitclone: https://github.com/polemon/fss.git
 * Documentation Wiki: https://github.com/polemon/fss/wiki

