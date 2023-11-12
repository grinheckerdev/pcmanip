
# pcmanip
### Warning! This tool is created only for educational use: do not use it for illegal purpose!
## About
**PcManip** is a very powerfull yet simple windows computer manipulation tool.
## Installation

First install python from the [official site](python.org) (python>=3.11)
Then open the console in the folder of the repository and run

For Linux and MacOS:

`python3 -m pip install -r requirments.txt`

For Windows:

`py.exe -m pip install -r requirments.txt`

## Run
For Linux and MacOS:

`python3 ./src/code/main.py`

For Windows:

`py.exe ./src/code/main.py`

## FAQ
**I am sending a message, but it doesn't show up!***

msg.exe is available only on Windows Pro and higher, we can't fix this.


**Can this run on Linux or MacOS?**

Yes, but there are some commands that work only on windows (like turning off remote computer or sending a message)

## Features
### Remote manipulation
![remote manipulation window](https://raw.githubusercontent.com/grinheckerdev/pcmanip/main/images/windows_remote_manipulation_showcase.png)

In the remote manipulation tab you can remotely manipulate other windows PC's
#### Features:
 1. Scan computers in local network (works if you have the `ipconfig` command)
 2. Remotely shutdown a computer in local network (works only if the target computer and this computer are both on windows and the target computer has the remote shutdown option on read [here](https://www.windows-active-directory.com/how-to-shut-down-and-restart-a-remote-computer.html))
 3. Send a popup message to a remote computer (works only if the computer that you want to shutdown and this computer are both on windows and you have the `msg` command

### Personaliztion
![personaliztion window](https://raw.githubusercontent.com/grinheckerdev/pcmanip/main/images/windows_personalization_showcase.png)

This tab allows you to personalize your PC.
#### Features:

 1. Set wallpaper (allows to bypass when windows is not activated) (works on windows)
 2. Set system colors (works on windows)

### Computer / system info
![enter image description here](https://raw.githubusercontent.com/grinheckerdev/pcmanip/main/images/windows_computer_info_showcase.png)

This tab allows you to view system info.
#### Features:

 1. Computer name, that will be displayed when scanning computers in the remote manipulation tab
 2. Computer local ip
 3. Computer public ip
 4. Platform name (got using python's `sys.platform` attribute)
 5. Full platform (OS) name (got using python's `platform.platform()` function)
 6. OS name (got using python's `os.name` attribute)
 7. OS version (got using python's `platform.version()` function)
 8. Logical CPUs
 9. Physical CPUs
 10. CPUs percentage
 11. CPU architecture
 12. Boot time
 13. Is power plugged in (works if you have a battery)
 14. Battery percentage (works if you have a battery)
 15. Estimated seconds (works if you have a battery)
