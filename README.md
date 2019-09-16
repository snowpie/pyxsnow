# pyxsnow

##Description

This is a python clone of the old xsnow package. It works by producing a transparent 'always on top' window that passes all its events through to whatever is behind it, so it doesn't need to draw on the root window. None of the code is taken from the original, though the images were very much derived from those supplied with xsnow.

##Known limitations:

   not many options (yet!).
   Systems like the raspberry pi that don't support transparency run this on top on a black background.
   Quitting ain't pretty. Try alt-f4, or kill, or ctrl-C a couple of times in the console that started it!
   
##Example Usage
```
$ python pyxsnow.py --help usage: pyxsnow.py [-h] [--flakes N] [--santa] [--tinsel]

Clone of the venerable xsnow, in python.

optional arguments: -h, --help show this help message and exit --flakes N Number of flakes to show. --santa Show Santa --tinsel Show Tinsel
```
