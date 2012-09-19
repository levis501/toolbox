#!/bin/sh

# Gets the EasyTether android usb tethering driver out of memory so that adb can function on Mac OS
sudo kextunload -v /System/Library/Extensions/EasyTetherUSBEthernet.kext
