This ReadMe is not exclusive for all the files in this directory.


About dcnet_on_off.sh:

WHAT IS, READ HERE: 
https://dreamcast-talk.com/forum/viewtopic.php?t=18143
https://www.reddit.com/r/dreamcast/comments/1i5dsfh/dcnet_is_here_on_flycast_play_native_online/

DCNET has now (06-fev-25) two exclusive games online: AeroDancing, Hundred Swords

DCNET Patched GDIs , just needed for real hardware
https://bit.ly/DCNET

DCNET Servers Add-on for DreamPi Tutorial (DC hardware)

Dreamcast WEB BROWSER ISP Setting: Use any username (you own) and password need to be "password" (no impact with shuouma sega tetris server authenication, will also be safe)
Example:
user: scrivani
pass: password

Open the RaspberryPi command line and run the commands below:
1. Download the DCNET On/Off Switch Script
>	wget https://github.com/scrivanidc/dreampi_custom_scripts/raw/refs/heads/main/dcnet_on_off.sh
2. Grant execution permission
>	chmod +x dcnet_on_off.sh
3. Run DCNET On/Off Switch
>	./dcnet_on_off.sh
4. Choose an option and press Enter


![image](https://github.com/user-attachments/assets/744726b9-f24f-4960-9334-3da5d9e21631)


![image](https://github.com/user-attachments/assets/1fa3306a-5147-480a-81a4-2e4badbeb735)

![image](https://github.com/user-attachments/assets/573a387b-2dc0-42a6-b74b-1b63d10df153)


Explanation of the options:

Option 1: Installs/Replaces the script that gives access to the DCNET servers - On Switch

Option 2: Restores the default DreamPi script (access to DCLive servers) - Off Switch

Option 3: Deletes files related to the DCNET connection - Total Uninstallation

Explanation of the approach:
This automation script makes a backup (2 times) of the original DreamPi script, as well as downloads the two files related 
to DCNET directly from the Flycast/Flyinghead github, so it has everything needed to install the add-on.
And whenever an option is chosen between on or off, it simply replaces the dreampi.py file with the backup, either from the standard DCLive, or from DCNET.

In short, this installer/executor works as a router between one script and another, being the traditional one and the DCNET.
