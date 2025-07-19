# waterfall_spectrogram
A Joyful and simple 3D live waterfall spectrogram.

## About
This is NOT production ready or calibrated or certified or anything of the like.

It IS useful and fun to see what 'sounds' are happening around you.

You need a computer with python and a microphone.

Although this should pick up and display most of the range of human hearing (about 30Hz to 20kHz) 
most computer peripherals will not pick up audio past 8500 - 9000 Hz so that won't be displayed.

I left the capability there just incase you have nice things!

## How to run
If you don't already have it, install python from [python.org ](https://www.python.org/). 

Any recent version should do.

Download the 3d_Spectrogram.py and requirements.txt and save them in the same folder.

Open a termnal from that same folder (or open a terminal and cd to where the files are) and then:

    pip install -r requirements.txt

    python 3D_Spectrogram.py

Enjoy!

## Known 'particularities' 
Other than the above note about frequencies above 9kHz-ish, the only other major known quirk is that during periods of silence, or
very low noise levels, the low end of the spectrum will populate with noise. 

I've done what I care to for the time being to filter that out and not lose the capability of detecting low frequency noise.